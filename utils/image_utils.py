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
from .camera_utils import create_camera
from .lighting_utils import setup_lighting
from .object_utils import apply_transformations
from .scene_utils import clear_scene, setup_scene, create_textured_plane
from .bbox_utils import calculate_bounding_boxes, save_yolo_format, visualize_bounding_boxes

# Configuration
from config import config

def generate_image(index: int,
                   textures: list[str],
                   models: list[tuple[int, str, str]],
                   visualise: bool) -> None: 
    """
    Generate a single image with bounding boxes.

    Args:
        index (int): The index of the image to generate.
        textures (list[str]): The list of texture paths to use.
        models (list[str]): The list of model paths to use.
        visualise (bool): Whether to visualise the labels on the image.
    """
    # Convert relative paths to absolute paths
    images_dir_abs = os.path.abspath(config["paths"]["images"])
    labels_dir_abs = os.path.abspath(config["paths"]["labels"])

    # Set up filenames for this image
    image_filename = f"image_{index:06d}.png"
    label_filename = f"image_{index:06d}.txt"

    logger.info(f"Generating image: {image_filename} and label: {label_filename}")
    
    render_path = os.path.join(images_dir_abs, image_filename)
    label_path = os.path.join(labels_dir_abs, label_filename)
    
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
        
        # Randomly select a texture if available
        texture_path = None
        if textures:
            texture_path = random.choice(textures)
            logger.info(f"Using texture: {texture_path}")
        
            # Create textured plane
            create_textured_plane(texture_path)

            # Randomly determine number of objects to generate (1-15)
            num_objects = random.randint(1, 15)
            logger.info(f"Generating {num_objects} objects for this image")

            imported_objects = []
            
            # Generate the specified number of objects
            for obj_idx in range(num_objects):
                if models:
                    model = random.choice(models)
                    model_class_idx = model[0]
                    model_class_name = model[1]
                    model_path = model[2]
                    logger.info(f"Object {obj_idx + 1}/{num_objects} using model:\n\tpath: {model_path}\n\tclass name: {model_class_name}\n\tclass index: {model_class_idx}")
                else:
                    logger.error("No models provided")
                    raise ValueError("No models provided")
                
                # Import models
                # Deselect all objects to merge the newly imported objects
                bpy.ops.object.select_all(action='DESELECT')
                bpy.ops.wm.obj_import(
                    filepath=model_path,
                    use_split_objects=False,
                    use_split_groups=False,
                )
                object_to_merge = [o for o in bpy.context.selected_objects if o.type == 'MESH']
            
                # Check if they need merging, merge if necessary
                if len(object_to_merge) > 1:
                    bpy.context.view_layer.objects.active = object_to_merge[0]
                    bpy.ops.object.join()
                else:
                    object_to_merge = bpy.context.selected_objects

                obj = object_to_merge[0]

                # Set the class index
                obj["class_idx"] = model_class_idx
                obj["class_name"] = model_class_name

                # Apply transformations
                apply_transformations(obj, imported_objects)
                imported_objects.append(obj)

        # Get fresh list of objects for bounding box calculation
        current_objects = [obj for obj in bpy.data.objects if obj.type == 'MESH']
        if not current_objects:
            raise ValueError("No valid objects found for bounding box calculation")
                
        # Calculate bounding boxes
        bounding_boxes = calculate_bounding_boxes(scene, camera, current_objects)

        # Save bounding boxes
        save_yolo_format(bounding_boxes, label_path)
        
        # Render the scene
        bpy.ops.render.render(write_still=True)
        logger.info(f"Image {index+1} rendered to: {render_path}")

        if visualise:
            visualization_path = os.path.join(config["paths"]["vis"], f"vis_{index:06d}.png")
            visualize_bounding_boxes(render_path, label_path, visualization_path)
            logger.info(f"Visualization saved to: {visualization_path}")
        else:
            logger.info("Skipped visualisation")
        

    except FileNotFoundError as e:
        logger.error(f"Error in image generation: {e}")
    finally:
        # Always try to clean up
        try:
            clear_scene()
        except Exception as e:
            logger.error(f"Error in cleanup: {e}")

