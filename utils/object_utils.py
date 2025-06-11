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
        # Get object dimensions and center
        obj_dims = obj.dimensions
        obj_center = obj.location
        
        # Calculate the maximum dimension of the object
        max_obj_dim = max(obj_dims.x, obj_dims.y)
        
        # Calculate distance between centers in 3D space
        distance = math.sqrt(
            (position[0] - obj_center.x)**2 + 
            (position[1] - obj_center.y)**2 +
            0
        )
        
        # Calculate minimum required distance based on object dimensions
        # Add a buffer to ensure objects don't get too close
        min_required_distance = max(
            min_distance,
            max_obj_dim * 1.5  # Use 1.5 times the maximum dimension as minimum distance
        )
        
        if distance < min_required_distance:
            return True
    return False

def find_valid_position(existing_objects):
    """Find a valid position that doesn't collide with existing objects.
    
    Args:
        existing_objects: List of existing objects
        
    Returns:
        Tuple of (x, y, z) coordinates if valid position found, None otherwise
    """
    # Get bounds from config
    grid_size = config["scene"]["grid"]["size"]
    half_grid = grid_size / 2
    
    # Add a buffer to keep objects away from the edges
    edge_buffer = 2.0
    
    CAMERA_BOUNDS = {
        'x_min': -half_grid + edge_buffer,  # Half of scene grid size with buffer
        'x_max': half_grid - edge_buffer,   # Half of scene grid size with buffer
        'y_min': -half_grid + edge_buffer,  # Half of scene grid size with buffer
        'y_max': half_grid - edge_buffer,   # Half of scene grid size with buffer
    }
    
    for _ in range(config["object"]["max_collision_check_amount"]):
        # Try a random position within camera bounds
        x = random.uniform(CAMERA_BOUNDS['x_min'], CAMERA_BOUNDS['x_max'])
        y = random.uniform(CAMERA_BOUNDS['y_min'], CAMERA_BOUNDS['y_max'])
        
        if not is_colliding((x, y, 0), existing_objects):
            return (x, y, 0)  # Return with z=0, we'll adjust height in apply_transformations
    
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
        
        # Rotate the object so that it stands upright
        obj.rotation_euler = (
            math.radians(90),       # x rotation
            0,                      # y rotation
            random.uniform(0, 360)  # z rotation for random orientation
        )
        
        # Update the scene to apply transformations
        bpy.context.view_layer.update()
        
        # Adjust the height to ensure object sits on ground
        # Get the object's dimensions after transformations
        final_dims = obj.dimensions
        # Move the object up by half its height to sit on ground
        obj.location.z = final_dims.z / 2
        