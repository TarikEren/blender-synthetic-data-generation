"""
Lighting Utilities for Blender Bounding Box Generator

This module contains utility functions for lighting setup and management in Blender.
"""

import bpy
import random

from typing import Dict

from utils.logger_utils import logger

def setup_lighting(config: Dict, seed: int = None) -> None:
    """
    Create randomized lighting setup for the scene.

    Args:
        config (Dict): The config dictionary.
        seed (int, optional): The seed for the random number generator.
    """
    if seed is not None:
        random.seed(seed)

    # Delete existing lights
    for obj in bpy.data.objects:
        if obj.type == 'LIGHT':
            bpy.data.objects.remove(obj)

    # Get the lighting types from the config
    lighting_types = ['three_point', 'studio', 'outdoor', 'dramatic']

    # Determine lighting style for this scene
    lighting_style = random.choice(lighting_types)

    if lighting_style == 'three_point':
        # Key light (main light)
        key_light = bpy.data.objects.new(name="KeyLight", object_data=bpy.data.lights.new(name="KeyLight", type='AREA'))
        # Randomise the location of the key light using the randomiser constants
        key_light.location = (
            random.uniform(config["light"]["position"]["x"] - config["light"]["randomiser_constants"]["location"]["x"],
                           config["light"]["position"]["x"] + config["light"]["randomiser_constants"]["location"]["x"]),
            random.uniform(config["light"]["position"]["y"] - config["light"]["randomiser_constants"]["location"]["y"],
                           config["light"]["position"]["y"] + config["light"]["randomiser_constants"]["location"]["y"]),
            random.uniform(config["light"]["position"]["z"] - config["light"]["randomiser_constants"]["location"]["z"],
                           config["light"]["position"]["z"] + config["light"]["randomiser_constants"]["location"]["z"])
        )
        key_light.rotation_euler = (
            random.uniform(config["light"]["rotation"]["x"] - config["light"]["randomiser_constants"]["rotation"]["x"],
                           config["light"]["rotation"]["x"] + config["light"]["randomiser_constants"]["rotation"]["x"]),
            random.uniform(config["light"]["rotation"]["y"] - config["light"]["randomiser_constants"]["rotation"]["y"],
                           config["light"]["rotation"]["y"] + config["light"]["randomiser_constants"]["rotation"]["y"]),
            random.uniform(config["light"]["rotation"]["z"] - config["light"]["randomiser_constants"]["rotation"]["z"],
                           config["light"]["rotation"]["z"] + config["light"]["randomiser_constants"]["rotation"]["z"])
        )
        key_light.data.energy = random.uniform(config["light"]["energy"].get("min"), 
                                               config["light"]["energy"].get("max"))
        key_light.data.size = random.uniform(5, 10)
        
        # Fill light (softer, less intense)
        fill_light = bpy.data.objects.new(name="FillLight", object_data=bpy.data.lights.new(name="FillLight", type='AREA'))
        fill_light.location = (random.uniform(-12, -8), random.uniform(-5, 5), random.uniform(8, 12))
        bpy.context.collection.objects.link(fill_light)
        fill_light.data.energy = random.uniform(300, 500)
        fill_light.data.size = random.uniform(8, 15)
        
        # Back light (rim light)
        back_light = bpy.data.objects.new(name="BackLight", object_data=bpy.data.lights.new(name="BackLight", type='AREA'))
        back_light.location = (random.uniform(-3, 3), random.uniform(-12, -8), random.uniform(12, 15))
        bpy.context.collection.objects.link(back_light)

        logger.info(f"Three-point lighting setup created with key light at {key_light.location}, fill light at {fill_light.location}, and back light at {back_light.location}")

    elif lighting_style == 'studio':
        # Soft overhead lighting
        lights = []
        for i in range(4):
            light = bpy.data.objects.new(name=f"StudioLight{i}", object_data=bpy.data.lights.new(name=f"StudioLight{i}", type='AREA'))
            x = random.uniform(-8, 8)
            y = random.uniform(-8, 8)
            light.location = (x, y, random.uniform(10, 15))
            bpy.context.collection.objects.link(light)
            light.data.energy = random.uniform(300, 500)
            light.data.size = random.uniform(4, 8)
            lights.append(light)
        logger.info(f"Studio lighting setup created with {len(lights)} lights")

    elif lighting_style == 'outdoor':
        # Sun light (directional)
        sun = bpy.data.objects.new(name="Sun", object_data=bpy.data.lights.new(name="Sun", type='SUN'))
        sun.location = (random.uniform(-5, 5), random.uniform(-5, 5), random.uniform(15, 20))
        sun.rotation_euler = (random.uniform(0, 0.8), random.uniform(-0.8, 0.8), random.uniform(-0.8, 0.8))
        bpy.context.collection.objects.link(sun)
        sun.data.energy = random.uniform(2, 5)
        
        # Ambient light
        ambient = bpy.data.objects.new(name="Ambient", object_data=bpy.data.lights.new(name="Ambient", type='AREA'))
        ambient.location = (0, 0, random.uniform(10, 15))
        ambient.scale = (20, 20, 1)
        bpy.context.collection.objects.link(ambient)
        ambient.data.energy = random.uniform(100, 300)
        logger.info(f"Outdoor lighting setup created with ambient light at {ambient.location} and sun light at {sun.location}")
        
    elif lighting_style == 'dramatic':
        # Strong single light source
        main_light = bpy.data.objects.new(name="DramaticLight", object_data=bpy.data.lights.new(name="DramaticLight", type='SPOT'))
        main_light.location = (random.uniform(-10, 10), random.uniform(-10, 10), random.uniform(12, 18))
        main_light.rotation_euler = (random.uniform(0, 0.8), random.uniform(-0.8, 0.8), random.uniform(-0.8, 0.8))
        bpy.context.collection.objects.link(main_light)
        main_light.data.energy = random.uniform(1000, 2000)
        main_light.data.spot_size = random.uniform(0.5, 1.2)
        
        # Subtle fill light
        fill = bpy.data.objects.new(name="DramaticFill", object_data=bpy.data.lights.new(name="DramaticFill", type='AREA'))
        fill.location = (-main_light.location.x, -main_light.location.y, random.uniform(5, 10))
        bpy.context.collection.objects.link(fill)
        fill.data.energy = random.uniform(100, 200)
        logger.info(f"Dramatic lighting setup created with main light at {main_light.location} and fill light at {fill.location}")

    # Reset random seed
    if seed is not None:
        random.seed() 

    
