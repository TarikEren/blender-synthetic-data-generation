"""
Object Utilities for Blender Bounding Box Generator

This module contains utility functions for object creation and management in Blender.
"""
# Standard Library Imports
import math
import random

# Third Party Imports
import bpy

# Configuration
from config import config
from .logger_utils import logger

def is_colliding(position, existing_objects, min_distance=3.0):
    """Check if a position would collide with existing objects.
    
    Args:
        position: Tuple of (x, y, z) coordinates
        existing_objects: List of existing objects
        min_distance: Minimum distance required between objects
        
    Returns:
        True if collision would occur, False otherwise
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

def find_valid_position(existing_objects):
    """Find a valid position that doesn't collide with existing objects.
    
    Args:
        existing_objects: List of existing objects
        
    Returns:
        Tuple of (x, y, z) coordinates if valid position found, None otherwise
    """
    for _ in range(config["object"]["max_collision_check_amount"]):
        # Try a random position
        x = random.uniform(-30, 30)
        y = random.uniform(-20, 20)
        z = 0
        
        if not is_colliding((x, y, z), existing_objects):
            return (x, y, z)
    
    return None 

def apply_transformations(obj, imported_objects):
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
            logger.warning(f"Could not find valid position for object {obj.name}, skipping...")
            bpy.data.objects.remove(obj)
            return None
        
        # Set the position
        obj.location = position
        
        # Check if this is a tank model using the class_name property
        is_tank = "tank" in obj["class_name"].lower()

        # Check if this is a plane model using the class_name property
        is_plane = "plane" in obj["class_name"].lower()
        
        # Apply appropriate rotations
        if is_tank:
            # For tanks: rotate 180 degrees around X axis to make them stand upright with turrets forward
            # Then apply random rotation around Z axis
            obj.rotation_euler = (
                math.radians(90),  # x rotation to make tank stand upright with turret forward
                0,                  # y rotation
                random.uniform(0, 360)  # z rotation for random orientation
            )
        elif is_plane:
            # For planes only random rotation around Z axis
            obj.rotation_euler = (
                0,
                0,
                random.uniform(0, 360)  # z rotation
            )
        else:
            # For other objects only random rotation around Z axis
            obj.rotation_euler = (
                0,
                0,
                random.uniform(0, 360)  # z rotation
            )
        
        # Update the scene to apply transformations
        bpy.context.view_layer.update()
        