"""
Camera Utilities for Blender Bounding Box Generator

This module contains utility functions for camera setup and management in Blender.
"""

import bpy
from config import scene_config, camera_config

def create_camera():
    """Create a camera positioned above the scene looking down."""
    bpy.ops.object.camera_add(location=(0, 0, scene_config["camera_height"]))
    camera = bpy.context.active_object
    
    # Point camera straight down (negative Z-axis)
    camera.rotation_euler = (0, 0, 0)
    
    # Set camera parameters
    camera_data = camera.data
    camera_data.lens = camera_config["focal_length"]  # Focal length in mm
    camera_data.clip_start = camera_config["clip_start"]
    camera_data.clip_end = camera_config["clip_end"]  # Set clip end to twice the camera height
    
    # Set this camera as the active/scene camera
    bpy.context.scene.camera = camera
    
    return camera

def bpy_coords_to_pixel_coords(scene, camera, coord):
    """Convert 3D world coordinates to 2D pixel coordinates using the camera projection.
    
    Args:
        scene: The Blender scene
        camera: The camera object
        coord: 3D coordinate to project
        
    Returns:
        Tuple of (x, y) pixel coordinates
    """
    render = scene.render
    res_x = render.resolution_x
    res_y = render.resolution_y
    
    # Convert world coordinates to camera view coordinates
    co_local = camera.matrix_world.inverted() @ coord
    
    # Convert camera coordinates to normalized device coordinates
    if co_local.z == 0:
        # Avoid division by zero
        co_local.z = 0.0001
        
    co_2d = (co_local.x / -co_local.z, co_local.y / -co_local.z)
    
    # Convert normalized device coordinates to pixel coordinates
    render_scale = render.resolution_percentage / 100
    
    # Account for camera sensor size and lens
    camera_data = camera.data
    sensor_width = camera_data.sensor_width
    sensor_height = sensor_width * res_y / res_x
    pixel_x = res_x * render_scale * (co_2d[0] * camera_data.lens / sensor_width + 0.5)
    pixel_y = res_y * render_scale * (co_2d[1] * camera_data.lens / sensor_height + 0.5)
    
    return (pixel_x, pixel_y) 