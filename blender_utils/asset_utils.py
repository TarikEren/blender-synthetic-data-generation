# Standard Library Imports
import os
import math
import random
from pathlib import Path

# Third Party Imports
import bpy

# Local Imports
from .logger_utils import logger
from .scene_utils import clear_scene

# Configuration
from config import config

def import_custom_model(model_path):
    """Import a custom 3D model into the scene."""
    logger.info(f"Attempting to import model from: {model_path}")
    
    # Clear the scene first
    clear_scene()
    
    # Import the model based on file extension
    file_ext = os.path.splitext(model_path)[1].lower()
    logger.debug(f"File extension: {file_ext}")
    
    try:
        # Store the current object names
        existing_objects = set(obj.name for obj in bpy.data.objects)
        
        # Import based on file type
        if file_ext == '.obj':
            logger.info("Importing OBJ file...")
            try:
                # First try the new method (Blender 4.x)
                if hasattr(bpy.ops.wm, 'obj_import'):
                    bpy.ops.wm.obj_import(filepath=model_path)
                # Then try the legacy method
                elif hasattr(bpy.ops.import_scene, 'obj'):
                    bpy.ops.import_scene.obj(filepath=model_path)
                else:
                    raise ImportError("No OBJ import operator found")
            except Exception as e:
                logger.error(f"Import error: {str(e)}")
                raise
        elif file_ext == '.fbx':
            logger.info("Importing FBX file...")
            if hasattr(bpy.ops.wm, 'fbx_import'):
                bpy.ops.wm.fbx_import(filepath=model_path)
            else:
                bpy.ops.import_scene.fbx(filepath=model_path)
        elif file_ext == '.blend':
            logger.info("Importing Blend file...")
            bpy.ops.wm.append(filepath=model_path)
        else:
            raise ValueError(f"Unsupported file format: {file_ext}")
        
        # Find newly added objects
        new_objects = [obj for obj in bpy.data.objects if obj.name not in existing_objects]
        logger.debug(f"New objects after import: {new_objects}")
        
        if not new_objects:
            raise ValueError("No new objects were imported")
            
        # Get the main imported object (usually the first one)
        imported_obj = new_objects[0]
        logger.info(f"Using imported object: {imported_obj.name}")
        
        # Store the object's name for later reference
        obj_name = imported_obj.name
        
        try:
            # Set a custom property to identify this as a custom model
            bpy.data.objects[obj_name]['class_idx'] = 0
            
            denominator = random.randint(config["object"]["denominator_range"][0],
                                         config["object"]["denominator_range"][1])
            
            # Calculate scale to make largest dimension 5 units
            scale_factor = config["object"]["max_scale"] / denominator
            
            # Scale and position the object
            obj = bpy.data.objects[obj_name]
            obj.scale = (scale_factor, scale_factor, scale_factor)
            
            # Reset all rotations first
            obj.rotation_euler = (0, 0, 0)
            
            # Apply 90 degrees counter-clockwise rotation around all axes
            # Note: math.pi/2 is 90 degrees
            obj.rotation_euler = (math.pi/2, math.pi/2, math.pi/2)
            
            # Update the scene to apply rotation
            bpy.context.view_layer.update()
            
            # Position slightly above ground after rotation
            obj.location = (0, 0, 2)
            
            logger.info(f"Adjusted object scale to {scale_factor}, rotated 90 degrees on X, Y, and Z axes, and positioned at height 2")
            
        except Exception as e:
            logger.warning(f"Error during object adjustment: {str(e)}")
            logger.warning("Continuing with unadjusted object...")
        
        return obj_name  # Return the name instead of the object reference
        
    except Exception as e:
        logger.error(f"Error during model import: {str(e)}")
        raise

def check_directories():
    """
    Check if the images and labels directories exist.
    """
    images_dir = os.path.join(config["paths"]["images"])
    labels_dir = os.path.join(config["paths"]["labels"])
    vis_dir = os.path.join(config["paths"]["vis"])

    if not os.path.exists(images_dir):
        raise FileNotFoundError(f"Images directory does not exist: {images_dir}")
    if not os.path.exists(labels_dir):
        raise FileNotFoundError(f"Labels directory does not exist: {labels_dir}")
    if not os.path.exists(vis_dir):
        raise FileNotFoundError(f"Visualization directory does not exist: {vis_dir}")

def find_textures() -> list[str]:
    """
    Find all texture files in the given directory and its subdirectories.
    
    Args:
        path: Root directory to search for textures
        
    Returns:
        List of paths to texture files
    """
    texture_files = []
    texture_extensions = ['.blend']  # Focus on .blend files for now
    
    # Walk through the directory and its subdirectories
    for root, dirs, files in os.walk(config["paths"]["textures"]):
        for file in files:
            # Check if file has a texture extension
            if any(file.lower().endswith(ext) for ext in texture_extensions):
                # Get the full path to the texture file
                texture_path = os.path.join(root, file)
                # Convert to absolute path
                texture_path = os.path.abspath(texture_path)
                texture_files.append(texture_path)
    
    return texture_files

def get_models_and_classes():
    """
    Find all model files in the given directory and its subdirectories.
    
    Returns:
        (List[(int, str, str)]) List of tuples containing the class index, class name and the model path

        For example: [(0, 'class0', 'models/class0/model_name.obj')]
    """
    # All accepted model extensions
    model_extensions = ['.obj']

    # Get all classes
    classes = get_classes()

    # Get all model files
    model_files = []
    for root, dirs, files in os.walk("./models"):
        for file in files:
            if any(file.lower().endswith(ext) for ext in model_extensions):
                # Get the model path
                model_path = os.path.join(root, file)

                # Get the class name and index
                class_name = Path(model_path).parent.parent.name
                class_idx = classes.index(class_name)

                # Get the absolute path
                model_path = os.path.abspath(model_path)

                # Add the model to the list
                model_files.append((class_idx, class_name, model_path))
    return model_files

def get_classes():
    """
    Gets the classes from the models folder which is structured as follows:
    ```
    models/
        class1/
            model_name.obj
        class2/
            model_name.obj
            ...
    ```
    The function will return a list of the class names.
    """
    models_path = "./models" # Hardcoded path
    classes = []
    for path in Path(models_path).glob('*/'):
        classes.append(path.name)    
    return classes