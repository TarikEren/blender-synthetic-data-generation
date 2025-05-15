"""
Scene Utilities for Blender Bounding Box Generator

This module contains utility functions for scene setup and management in Blender.
"""

# Standard Library Imports
import os

# Third Party Imports
import bpy

# Local Imports
from .logger_utils import logger

# Configuration
from config import config

def clear_scene():
    """Remove all objects, materials, meshes and lights from the scene."""
    bpy.ops.object.select_all(action='SELECT')
    bpy.ops.object.delete()
    
    # Clear all materials
    for material in bpy.data.materials:
        bpy.data.materials.remove(material)
    
    # Clear all meshes
    for mesh in bpy.data.meshes:
        bpy.data.meshes.remove(mesh)
        
    # Clear all lights
    for light in bpy.data.lights:
        bpy.data.lights.remove(light)

def setup_scene():
    """Configure scene settings for rendering."""
    # Create a new scene with all default settings
    scene = bpy.context.scene
    
    # Configure render settings
    scene.render.engine = 'CYCLES'  # Use Cycles renderer
    
    # Enable GPU rendering
    prefs = bpy.context.preferences
    cuda_prefs = prefs.addons['cycles'].preferences
    
    # Log available devices
    logger.debug("Available Devices:")
    for device in cuda_prefs.devices:
        logger.debug(f"Device: {device.name}, Type: {device.type}, Use: {device.use}")
    
    # Force CUDA compute type and refresh devices
    cuda_prefs.compute_device_type = 'CUDA'
    cuda_prefs.refresh_devices()
    
    # Enable all available CUDA devices
    for device in cuda_prefs.devices:
        if device.type == 'CUDA':
            device.use = True
            logger.debug(f"Enabled CUDA device: {device.name}")
    
    # Set render settings for faster preview
    scene.render.resolution_x = config["scene"]["resolution"]["x"]
    scene.render.resolution_y = config["scene"]["resolution"]["y"]
    scene.render.resolution_percentage = config["scene"]["resolution"]["percentage"]
    scene.render.filepath = '//rendered_image.png'
    
    # Optimize render settings for GPU
    scene.cycles.device = 'GPU'
    scene.cycles.tile_size = config["scene"]["cycles"]["tile_size"]            # Larger tile size for GPU
    scene.cycles.samples = config["scene"]["cycles"]["sample_count"]           # Reduced samples for faster preview
    scene.cycles.use_denoising = config["scene"]["cycles"]["use_denoising"]    # Enable denoising for cleaner results
    
    # Additional GPU optimizations
    scene.cycles.use_adaptive_sampling = config["scene"]["cycles"]["use_adaptive_sampling"]
    scene.cycles.adaptive_threshold = config["scene"]["cycles"]["adaptive_threshold"]
    scene.cycles.adaptive_min_samples = config["scene"]["cycles"]["adaptive_min_samples"]
    scene.cycles.use_denoising_prefilter = config["scene"]["cycles"]["use_denoising_prefilter"]
    
    # Force GPU compute
    scene.cycles.feature_set = 'EXPERIMENTAL'
    
    # Configure grayscale output
    scene.view_settings.view_transform = 'Standard'  # Use standard view transform
    scene.view_settings.look = 'None'  # No color look
    scene.view_settings.exposure = 0.0  # No exposure adjustment
    scene.view_settings.gamma = 1.0  # No gamma adjustment
    
    # Add a compositor node setup for grayscale conversion
    scene.use_nodes = True
    tree = scene.node_tree
    nodes = tree.nodes
    
    # Clear existing nodes
    nodes.clear()
    
    # Create nodes
    render_layers = nodes.new('CompositorNodeRLayers')
    rgb_to_bw = nodes.new('CompositorNodeRGBToBW')
    composite = nodes.new('CompositorNodeComposite')
    
    # Link nodes
    links = tree.links
    links.new(render_layers.outputs[0], rgb_to_bw.inputs[0])
    links.new(rgb_to_bw.outputs[0], composite.inputs[0])
    
    # Log render settings for verification
    logger.debug("==== Render Settings ====")
    logger.debug(f"Device: {scene.cycles.device}")
    logger.debug(f"Tile Size: {scene.cycles.tile_size}")
    logger.debug(f"Samples: {scene.cycles.samples}")
    logger.debug(f"Denoising: {scene.cycles.use_denoising}")
    logger.debug(f"Feature Set: {scene.cycles.feature_set}")
    
    # Adjust world settings (simple white background)
    world = bpy.data.worlds['World']
    world.use_nodes = True
    bg_node = world.node_tree.nodes['Background']
    bg_node.inputs[0].default_value = config["scene"]["default_background"]
    bg_node.inputs[1].default_value = config["scene"]["default_background_strength"]
    
    return scene

def create_textured_plane(texture_path=None):
    """Create a 3x3 grid of planes with optional texture.
    
    Args:
        texture_path: Path to the texture file (.blend)
    """
    planes = []
    plane_size = config["scene"]["grid"]["size"] # Size of each individual plane
    spacing = plane_size  # Planes will touch perfectly
    
    # Create a plane grid
    for i in range(3):
        for j in range(3):
            # Calculate position for this plane
            x = (i - 1) * spacing  # -1, 0, 1
            y = (j - 1) * spacing  # -1, 0, 1
            
            # Create the plane
            bpy.ops.mesh.primitive_plane_add(size=plane_size, location=(x, y, 0))
            plane = bpy.context.active_object
            
            # Set plane name for easy identification
            plane.name = f"Background_Plane_{i}_{j}"
            
            # Create material
            mat = bpy.data.materials.new(name=f"Ground_Material_{i}_{j}")
            mat.use_nodes = True
            nodes = mat.node_tree.nodes
            links = mat.node_tree.links
            
            # Clear existing nodes
            nodes.clear()
            
            # Create nodes for texture setup
            material_output = nodes.new('ShaderNodeOutputMaterial')
            principled_bsdf = nodes.new('ShaderNodeBsdfPrincipled')
            
            # Link Principled BSDF to Material Output
            links.new(principled_bsdf.outputs['BSDF'], material_output.inputs['Surface'])
            
            if texture_path and os.path.exists(texture_path):
                try:
                    # Append the material from the .blend file
                    with bpy.data.libraries.load(texture_path) as (data_from, data_to):
                        # Find material names in the .blend file
                        material_names = [name for name in data_from.materials]
                        if material_names:
                            # Load the first material found
                            data_to.materials = [material_names[0]]
                    
                    if data_to.materials and data_to.materials[0] is not None:
                        # Use the loaded material instead of creating a new one
                        imported_mat = data_to.materials[0]
                        
                        # Assign the imported material to the plane
                        if plane.data.materials:
                            plane.data.materials[0] = imported_mat
                        else:
                            plane.data.materials.append(imported_mat)
                        
                        logger.info(f"Successfully applied material from: {texture_path}")
                        planes.append(plane)
                        continue
                    
                    raise Exception("No valid materials found in the .blend file")
                    
                except Exception as e:
                    logger.error(f"Error applying material from .blend file: {str(e)}")
                    # Fallback to default material if texture fails
                    principled_bsdf.inputs[0].default_value = config["object"]["default_colour"]
            else:
                # Fallback to default again
                principled_bsdf.inputs[0].default_value = config["object"]["default_colour"]
            
            # Assign material to plane (only if we didn't successfully import a material)
            if plane.data.materials:
                plane.data.materials[0] = mat
            else:
                plane.data.materials.append(mat)
            
            planes.append(plane)
    
    return planes 
