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

def create_objects(num_objects=5, distribution_seed=None):
    """Create random 3D objects within the camera's field of view.
    
    Args:
        num_objects: Number of objects to create
        distribution_seed: Seed for random number generator
        
    Returns:
        List of created objects
    """
    # Set a random seed for this distribution if provided
    if distribution_seed is not None:
        random.seed(distribution_seed)
        
    objects = []
    object_classes = ['cube', 'sphere', 'cone', 'cylinder', 'torus']
    
    # Determine positioning strategy for this batch
    # Sometimes cluster objects, sometimes spread them out
    spread_factor = random.uniform(config["object"]["spread_factor_range"][0],
                                   config["object"]["spread_factor_range"][1])  

    x_center_offset = random.uniform(config["object"]["x_center_offset_range"][0],
                                     config["object"]["x_center_offset_range"][1])
    
    y_center_offset = random.uniform(config["object"]["y_center_offset_range"][0],
                                     config["object"]["y_center_offset_range"][1])
    
    # Helper function to check collision with existing objects
    def is_colliding(position, obj_type, existing_objects):
        # Determine object radius based on type (approximate)
        if obj_type == 'cube':
            radius = 1.0  # Half of size 2
        elif obj_type == 'sphere':
            radius = 1.0
        elif obj_type == 'cone':
            radius = 1.0
        elif obj_type == 'cylinder':
            radius = 1.0
        elif obj_type == 'torus':
            radius = 1.5
        
        # Add some padding for better spacing
        radius += 0.5
        
        # Check distance to all existing objects
        for obj in existing_objects:
            obj_pos = obj.location
            # Get approximate radius of existing object
            obj_radius = 1.5  # Default for safety
            
            # Calculate distance between centers
            distance = math.sqrt(
                (position[0] - obj_pos[0])**2 + 
                (position[1] - obj_pos[1])**2 + 
                (position[2] - obj_pos[2])**2
            )
            
            # If distance is less than sum of radii, they collide
            if distance < (radius + obj_radius):
                return True
                
        # No collision found
        return False
    
    for i in range(num_objects):
        # Try to find a non-colliding position
        max_attempts = config["object"]["max_collision_check_amount"]
        attempt = 0
        colliding = True
        
        # Randomly choose an object type
        obj_type = random.choice(object_classes)
        
        x, y, z = 0, 0, 0
        
        # Keep trying until we find a non-colliding position
        while colliding and attempt < max_attempts:
            # Randomly position within visible area with the custom distribution
            x = random.uniform(config["object"]["random_x_range"][0],
                               config["object"]["random_x_range"][1]) * spread_factor + x_center_offset
            y = random.uniform(config["object"]["random_y_range"][0],
                               config["object"]["random_y_range"][1]) * spread_factor + y_center_offset
            z = random.uniform(config["object"]["random_z_range"][0],
                               config["object"]["random_z_range"][1])  # Height above ground
            
            # Check if this position would collide with existing objects
            colliding = is_colliding((x, y, z), obj_type, objects)
            attempt += 1
        
        # If we couldn't find a non-colliding position after max attempts,
        # just use the last position we tried and continue
        
        # Create the object based on type
        if obj_type == 'cube':
            bpy.ops.mesh.primitive_cube_add(size=2, location=(x, y, z))
            obj = bpy.context.active_object
            obj['class_idx'] = 0
        elif obj_type == 'sphere':
            bpy.ops.mesh.primitive_uv_sphere_add(radius=1, location=(x, y, z))
            obj = bpy.context.active_object
            obj['class_idx'] = 1
        elif obj_type == 'cone':
            bpy.ops.mesh.primitive_cone_add(radius1=1, location=(x, y, z))
            obj = bpy.context.active_object
            obj['class_idx'] = 2
        elif obj_type == 'cylinder':
            bpy.ops.mesh.primitive_cylinder_add(radius=1, location=(x, y, z))
            obj = bpy.context.active_object
            obj['class_idx'] = 3
        elif obj_type == 'torus':
            bpy.ops.mesh.primitive_torus_add(location=(x, y, z))
            obj = bpy.context.active_object
            obj['class_idx'] = 4
        
        # Add random rotation
        obj.rotation_euler = (
            random.uniform(config["object"]["random_rotation_range"][0],
                           config["object"]["random_rotation_range"][1]),      # x rotation
            random.uniform(config["object"]["random_rotation_range"][0],
                           config["object"]["random_rotation_range"][1]),      # y rotation
            random.uniform(config["object"]["random_rotation_range"][0],
                           config["object"]["random_rotation_range"][1]),      # z rotation
        )
        
        # Create a random colored material
        mat = bpy.data.materials.new(name=f"Material_{i}")
        mat.use_nodes = True
        principled_bsdf = mat.node_tree.nodes.get('Principled BSDF')
        if principled_bsdf:
            principled_bsdf.inputs[0].default_value = (
                random.uniform(0.1, 1),     # Red
                random.uniform(0.1, 1),     # Green
                random.uniform(0.1, 1),     # Blue
                1                           # Alpha
            )
        
        # Assign material to object
        if obj.data.materials:
            obj.data.materials[0] = mat
        else:
            obj.data.materials.append(mat)
        
        objects.append(obj)
    
    # Create a plane for the ground
    bpy.ops.mesh.primitive_plane_add(size=config["scene"]["grid"]["size"],
                                     location=(0, 0, 0))
    ground = bpy.context.active_object
    
    # Add a material to the ground
    mat = bpy.data.materials.new(name="Ground_Material")
    mat.use_nodes = True
    principled_bsdf = mat.node_tree.nodes.get('Principled BSDF')
    if principled_bsdf:
        principled_bsdf.inputs[0].default_value = (
            config["object"]["default_colour"][0],
            config["object"]["default_colour"][1],
            config["object"]["default_colour"][2],
            config["object"]["default_colour"][3])
    
    # Assign material to ground
    if ground.data.materials:
        ground.data.materials[0] = mat
    else:
        ground.data.materials.append(mat)
    
    # Reset random seed if we changed it
    if distribution_seed is not None:
        random.seed()
        
    return objects

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