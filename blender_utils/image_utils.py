"""
Image Generation Utilities for Blender Bounding Box Generator

This module contains the main image generation function and related utilities.
"""
# Standard Library Imports
import os
import random

# Third Party Imports
import bpy

# Local Imports
from .logger_utils import logger
from .asset_utils import find_textures
from .camera_utils import create_camera
from .lighting_utils import setup_lighting
from .object_utils import create_objects, find_valid_position
from .scene_utils import clear_scene, setup_scene, create_textured_plane
from .bbox_utils import calculate_bounding_boxes, save_yolo_format, visualize_bounding_boxes

# Configuration
from config import config

def generate_single_image(index, custom_model_path=None):
    """
    Generate a single image with bounding boxes.

    Args:
        index (int): The index of the image to generate.
        custom_model_path (str, optional): The path to the custom model to use. Defaults to None.
    """
    logger.info(f"Generating image {index+1}")
    logger.info(f"Custom model path: {custom_model_path}")
    
    # Convert relative paths to absolute paths
    images_dir_abs = os.path.abspath(config["paths"]["images"])
    labels_dir_abs = os.path.abspath(config["paths"]["labels"])
    visualization_dir_abs = os.path.join(config["paths"]["vis"])
    
    if custom_model_path:
        custom_model_abs = os.path.abspath(custom_model_path)
        logger.debug(f"Absolute custom model path: {custom_model_abs}")
        logger.debug(f"Custom model file exists: {os.path.exists(custom_model_abs)}")
    
    # Create directories if they don't exist
    os.makedirs(images_dir_abs, exist_ok=True)
    os.makedirs(labels_dir_abs, exist_ok=True)
    os.makedirs(visualization_dir_abs, exist_ok=True)  # Create visualization directory
    
    # Set up filenames for this image
    image_filename = f"image_{index:03d}.png"
    label_filename = f"image_{index:03d}.txt"
    render_path = os.path.join(images_dir_abs, image_filename)
    bbox_path = os.path.join(labels_dir_abs, label_filename)
    visualization_path = os.path.join(visualization_dir_abs, f"vis_{index:03d}.png")
    
    try:
        # Clear the scene
        clear_scene()
        
        # Setup scene
        scene = setup_scene()
        scene.render.filepath = render_path
        
        # Create camera
        camera = create_camera()
        
        # Setup randomized lighting using the image index as seed
        setup_lighting(seed=index+100)
        
        # Get list of available textures
        texture_files = find_textures()
        logger.info(f"Found {len(texture_files)} texture files")
        
        # Randomly select a texture if available
        texture_path = None
        if texture_files:
            texture_path = random.choice(texture_files)
            logger.info(f"Using texture: {texture_path}")
        
        # Create textured plane
        create_textured_plane(texture_path)
        
        # Import or create objects
        if custom_model_path:
            logger.info("Using custom model path...")
            try:
                # Get file extension
                file_ext = os.path.splitext(custom_model_path)[1].lower()
                logger.debug(f"File extension: {file_ext}")
                
                # Determine number of models to create (1-10)
                num_models = random.randint(1, 10)
                logger.info(f"Creating {num_models} instances of the model")
                
                # Create a list to store all imported objects
                imported_objects = []
                
                for i in range(num_models):
                    # Import custom model
                    if file_ext == '.obj':
                        logger.info(f"Importing OBJ file {i+1}...")
                        if hasattr(bpy.ops.wm, 'obj_import'):
                            bpy.ops.wm.obj_import(filepath=custom_model_path)
                        else:
                            bpy.ops.import_scene.obj(filepath=custom_model_path)
                    elif file_ext == '.fbx':
                        logger.info(f"Importing FBX file {i+1}...")
                        if hasattr(bpy.ops.wm, 'fbx_import'):
                            bpy.ops.wm.fbx_import(filepath=custom_model_path)
                        else:
                            bpy.ops.import_scene.fbx(filepath=custom_model_path)
                    elif file_ext == '.blend':
                        logger.info(f"Importing Blend file {i+1}...")
                        bpy.ops.wm.append(filepath=custom_model_path)
                    else:
                        raise ValueError(f"Unsupported file format: {file_ext}")
                    
                    # Find the newly imported mesh object
                    mesh_objects = [obj for obj in bpy.data.objects if obj.type == 'MESH' and obj not in imported_objects]
                    if not mesh_objects:
                        raise ValueError(f"No mesh objects found after import {i+1}")
                    
                    # Set up the mesh object
                    obj = mesh_objects[0]
                    obj['class_idx'] = 0
                    
                    # Scale the object with randomization
                    dims = obj.dimensions
                    max_dim = max(dims)
                    if max_dim > 0:
                        # Base scale factor
                        base_scale = config["object"]["max_scale"] / max_dim
                        
                        # Random scale variation between 1 and 1.5
                        scale_variation = random.uniform(config["object"]["scale_variation_range"][0],
                                                         config["object"]["scale_variation_range"][1])
                        
                        # Apply random scale
                        scale_factor = base_scale * scale_variation
                        obj.scale = (scale_factor, scale_factor, scale_factor)
                        
                        # Reset all rotations first
                        obj.rotation_euler = (0, 0, 0)
                        
                        # Find a valid position that doesn't collide with existing objects
                        position = find_valid_position(imported_objects)
                        if position is None:
                            logger.warning(f"Could not find valid position for object {i+1}, skipping...")
                            bpy.data.objects.remove(obj)
                            continue
                        
                        # Set the position
                        obj.location = position
                        
                        # Random rotation around Z axis only
                        obj.rotation_euler = (
                            0,
                            0,
                            random.uniform(0, 360)  # z rotation
                        )
                        
                        # Update the scene to apply transformations
                        bpy.context.view_layer.update()
                        
                        logger.debug(f"Adjusted object {i+1} scale to {scale_factor} (variation: {scale_variation})")
                        logger.debug(f"Set position: {obj.location}")
                        logger.debug(f"Set random rotation: {obj.rotation_euler}")
                    else:
                        logger.warning(f"Object {i+1} has zero dimensions")
                    
                    imported_objects.append(obj)
                
            except Exception as e:
                logger.error(f"Error importing custom model: {str(e)}")
                raise
        else:
            logger.info("No custom model path provided, creating random objects...")
            create_objects(num_objects=7, distribution_seed=index)
        
        # Get fresh list of objects for bounding box calculation
        current_objects = [obj for obj in bpy.data.objects if obj.type == 'MESH']
        if not current_objects:
            raise ValueError("No valid objects found for bounding box calculation")
        
        # Calculate bounding boxes
        bounding_boxes = calculate_bounding_boxes(scene, camera, current_objects)
        
        # Save bounding boxes in YOLO format
        save_yolo_format(bounding_boxes, bbox_path)
        
        # Render the scene
        bpy.ops.render.render(write_still=True)
        
        # Visualize and test the bounding boxes
        if os.path.exists(render_path) and os.path.exists(bbox_path):
            logger.info(f"Creating visualization for image {index+1}")
            logger.info(f"Render path exists: {os.path.exists(render_path)}")
            logger.info(f"Bbox path exists: {os.path.exists(bbox_path)}")
            logger.info(f"Visualization path: {visualization_path}")
            visualize_bounding_boxes(render_path, bbox_path, visualization_path)
            logger.info(f"Visualization complete for image {index+1}")
        else:
            logger.warning(f"Could not create visualization - missing files:")
            logger.warning(f"Render path exists: {os.path.exists(render_path)}")
            logger.warning(f"Bbox path exists: {os.path.exists(bbox_path)}")
        
        logger.info(f"Image {index+1} rendered to: {render_path}")
        logger.info(f"Labels saved to: {bbox_path}")
        
    except Exception as e:
        logger.error(f"Error in generate_single_image: {str(e)}")
        raise
    finally:
        # Always try to clean up
        try:
            clear_scene()
        except:
            pass 