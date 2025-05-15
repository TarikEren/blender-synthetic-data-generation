"""
Lighting Utilities for Blender Bounding Box Generator

This module contains utility functions for lighting setup and management in Blender.
"""
# Standard Library Imports
import random

# Third Party Imports
import bpy

def setup_lighting(seed=None):
    """Create randomized lighting setup for the scene."""
    if seed is not None:
        random.seed(seed)
    
    # Delete existing lights
    for obj in bpy.data.objects:
        if obj.type == 'LIGHT':
            bpy.data.objects.remove(obj)

    lighting_types = ['three_point', 'studio', 'outdoor', 'dramatic']

    # Determine lighting style for this scene
    lighting_style = random.choice(lighting_types)
    
    if lighting_style == 'three_point':
        # Key light (main light)
        key_light = bpy.data.objects.new(name="KeyLight", object_data=bpy.data.lights.new(name="KeyLight", type='AREA'))
        key_light.location = (random.uniform(8, 12), random.uniform(-5, 5), random.uniform(10, 15))
        key_light.rotation_euler = (random.uniform(0, 0.5), random.uniform(-0.5, 0.5), random.uniform(-0.5, 0.5))
        bpy.context.collection.objects.link(key_light)
        key_light.data.energy = random.uniform(800, 1200)
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
        back_light.data.energy = random.uniform(500, 700)
        back_light.data.size = random.uniform(3, 6)
        
    elif lighting_style == 'studio':
        # Soft overhead lighting
        for i in range(4):
            light = bpy.data.objects.new(name=f"StudioLight{i}", object_data=bpy.data.lights.new(name=f"StudioLight{i}", type='AREA'))
            x = random.uniform(-8, 8)
            y = random.uniform(-8, 8)
            light.location = (x, y, random.uniform(10, 15))
            bpy.context.collection.objects.link(light)
            light.data.energy = random.uniform(300, 500)
            light.data.size = random.uniform(4, 8)
            
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
    
    # Reset random seed
    if seed is not None:
        random.seed() 