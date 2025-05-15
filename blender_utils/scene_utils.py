"""
Scene Utilities for Blender Bounding Box Generator

This module contains utility functions for scene setup and management in Blender.
"""

import bpy

from .logger_utils import logger

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