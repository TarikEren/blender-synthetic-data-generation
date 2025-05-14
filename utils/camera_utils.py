"""
Camera Utilities for Blender Bounding Box Generator

This module contains utility functions for camera setup and management in Blender.
"""

import bpy
from typing import Dict

from old_config import camera_config

def create_camera(config: Dict) -> bpy.types.Object:
    """
    Create a camera positioned above the scene looking down.

    Args:
        config (Dict): The config dictionary.

    Returns:
        bpy.types.Object: The created camera object.
    """
    # Add a camera object
    bpy.ops.object.camera_add(location=(0, 0, camera_config["height"]))
    camera = bpy.context.active_object

    # Set the camera's rotation
    camera.rotation_euler = (0, 0, 0)

    # Set the camera's focal length
