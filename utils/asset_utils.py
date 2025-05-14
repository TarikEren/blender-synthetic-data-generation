"""
Asset utilities for loading textures and models.
"""

import os
import math
import random
from typing import Dict

import bpy

from utils.logger_utils import logger
from utils.scene_utils import clear_scene

def get_textures(config: Dict) -> list[str]:
    """
    Check if textures are provided in the config. If not, raise an error.

    Args:
        config (Dict): The config dictionary.

    Returns:
        list: List of textures
    """
    # Initialize the list of textures
    textures = []

    # Get the textures directory
    textures_dir = config["paths"]["textures"]

    # Check if the textures directory exists
    if not os.path.exists(textures_dir):
        logger.error(f"Textures directory not found: {textures_dir}")
        raise FileNotFoundError(f"Textures directory not found: {textures_dir}")
    
    # Check if the textures directory is empty
    if not os.listdir(textures_dir):
        logger.warning(f"Textures directory is empty: {textures_dir}")
        return textures
    
    # Get all the files in the textures directory
    for root, dirs, files in os.walk(textures_dir):
        for file in files:
            if file.endswith(".blend"):
                textures.append(os.path.join(root, file))

    # Log the textures
    logger.info(f"Textures found: {textures}")

    # Return the list of textures
    return textures

def collision_check(position: tuple[float, float, float],
                    existing_objects: list[bpy.types.Object],
                    min_distance: float = 3.0) -> bool:
    """
    Check if a position would collide with existing objects.

    Args:
        position (tuple[float, float, float]): The position to check.
        existing_objects (list[bpy.types.Object]): The list of existing objects.
        min_distance (float): The minimum distance between objects.

    Returns:
        bool: True if the position would collide with existing objects, False otherwise.
    """
    for obj in existing_objects:
        # Calculate distance between centers
        distance = math.sqrt(
            (position[0] - obj.location.x)**2 + 
            (position[1] - obj.location.y)**2
        )
        if distance < min_distance:
            return True
    return False

def find_valid_position(existing_objects,
                        config: Dict) -> tuple[float, float, float]:
    """
    Find a valid position that doesn't collide with existing objects and is within the camera's view frustum.
    
    Args:
        existing_objects: List of existing objects
        config: The config dictionary
        
    Returns:
        Tuple of (x, y, z) coordinates if valid position found, None otherwise
    """
    # Get the camera
    camera = bpy.context.scene.camera
    if not camera:
        logger.error("No camera found in the scene")
        return None

    # Calculate the camera's view frustum
    # The camera is looking down at 90 degrees, so we can calculate the view frustum
    # based on the camera's height and field of view
    camera_height = camera.location.z
    fov = camera.data.angle  # Field of view in radians
    aspect_ratio = bpy.context.scene.render.resolution_x / bpy.context.scene.render.resolution_y

    # Calculate the view frustum dimensions at ground level (z=0)
    # tan(fov/2) = opposite/adjacent = half_width/camera_height
    half_width = camera_height * math.tan(fov/2)
    half_height = half_width / aspect_ratio

    # Add a small margin to ensure objects are well within the view
    margin = 0.1  # 10% margin
    half_width *= (1 - margin)
    half_height *= (1 - margin)

    for _ in range(config["objects"].get("max_collision_check_amount", 100)):
        # Try a random position within the view frustum
        x = random.uniform(-half_width, half_width)
        y = random.uniform(-half_height, half_height)
        z = 0  # Objects are placed on the ground plane

        # Check if this position would collide with existing objects
        if not collision_check((x, y, z), existing_objects):
            return (x, y, z)

    return None

def get_models(config: Dict) -> list[str]:
    """
    Check if models are provided in the config. If not, raise an error.

    Args:
        config (Dict): The config dictionary.

    Returns:
        list: List of models
    """
    # Initialize the list of models
    models = []

    # Get the models directory
    models_dir = config["paths"]["models"]

    # Check if the models directory exists
    if not os.path.exists(models_dir):
        logger.error(f"Models directory not found: {models_dir}")
        raise FileNotFoundError(f"Models directory not found: {models_dir}")
    
    # Check if the models directory is empty
    if not os.listdir(models_dir):
        logger.warning(f"Models directory is empty: {models_dir}")
        return models

    # Get all the files in the models directory
    for root, dirs, files in os.walk(models_dir):
        for file in files:
            if file.endswith(".fbx") or file.endswith(".obj"):
                models.append(os.path.join(root, file))

    # Log the models
    logger.info(f"Models found: {models}")

    # Return the list of models
    return models
    
def import_model(model_path: str,
                  config: Dict) -> bpy.types.Object:
    """
    Import a model based on the provided model path.

    Args:
        model_path (str): The path to the model file.
        config (Dict): The config dictionary.

    Returns:
        bpy.types.Object: The imported object.
    """
    
    # Clear the scene first
    clear_scene()

    # Import the model based on file extension
    file_ext = os.path.splitext(model_path)[1].lower()
    
    try:
        # Store the current object names
        existing_objects = set(obj.name for obj in bpy.data.objects)

        # Import the model based on file extension
        if file_ext == ".obj":
            logger.info(f"Importing OBJ file: {model_path}")
            bpy.ops.import_mesh.obj(filepath=model_path)
        elif file_ext == ".fbx":
            logger.info(f"Importing FBX file: {model_path}")
            bpy.ops.import_scene.fbx(filepath=model_path)
        else:
            raise ValueError(f"Unsupported file extension: {file_ext}")

        # Find newly added objects
        new_objects = [obj for obj in bpy.data.objects if obj.name not in existing_objects]
        logger.debug(f"New objects after import: {new_objects}")
        
        if not new_objects:
            raise ValueError("No new objects were imported")
        
        # Get the main imported object (The first one)
        imported_obj = new_objects[0]
        logger.info(f"Using imported object: {imported_obj.name}")

        # Store the object's name for later reference
        obj_name = imported_obj.name

        try:
            # Set a custom property to identify this as a custom model
            bpy.data.objects[obj_name]['class_idx'] = 0

            # Calculate scale to make largest dimension 5 units
            denominator_range_1 = config["objects"].get("denominator_range")[0]
            denominator_range_2 = config["objects"].get("denominator_range")[1]
            denominator = random.randint(denominator_range_1, denominator_range_2)
            scale_factor = config["objects"].get("max_scale") / denominator
            
            
            # Scale the object
            imported_obj.scale = (scale_factor, scale_factor, scale_factor)
            
            # Reset all rotations first
            imported_obj.rotation_euler = (0, 0, 0)
            
            # Apply 90 degrees counter-clockwise rotation around all axes
            # Note: math.pi/2 is 90 degrees
            imported_obj.rotation_euler = (math.pi/2, math.pi/2, math.pi/2)
            
            # Update the scene to apply rotation
            bpy.context.view_layer.update()

            # Position slightly above ground after rotation
            imported_obj.location = (0, 0, 2)
            
            logger.info(f"Adjusted object scale to {scale_factor}, rotated 90 degrees on X, Y, and Z axes, and positioned at height 2")
            
        except Exception as e:
            logger.warning(f"Error during object adjustment: {str(e)}. Continuing with unadjusted object...")
        
        # Return the imported object
        return imported_obj

    except Exception as e:
        logger.error(f"Error importing model: {e}")
        raise e


