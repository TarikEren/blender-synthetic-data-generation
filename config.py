"""
Config file for the Blender Object Generator.

This file contains the configuration for the Blender Object Generator.
It is used to configure the camera, light, scene, object, paths, and output.

The config is split into 5 main sections:
- camera_config: Config for the camera.
- light_config: Config for the light.
- scene_config: Config for the scene.
- object_config: Config for the object.
- paths_config: Config for the paths.
- output_config: Config for the output.

The config is then merged into a single config dictionary which is used to configure the Blender Object Generator.
"""

# Camera config
camera_config = {
    "position": {
            "x": 0,                         # The x position of the camera
            "y": 0,                         # The y position of the camera
            "z": 100                        # The z position of the camera
        },
    "rotation": {
            "x": 90,                        # The x rotation of the camera
            "y": 0,                         # The y rotation of the camera
            "z": 0                          # The z rotation of the camera
        },
    "focal_length": 50                      # The focal length of the camera
}

# Light config
light_config = {
    "position": {
        "x": 0,                             # The x position of the light
        "y": 0,                             # The y position of the light
        "z": 0                              # The z position of the light
    },
    "rotation": {
        "x": 0,                             # The x rotation of the light
        "y": 0,                             # The y rotation of the light
        "z": 0                              # The z rotation of the light
    },
    "energy": {
        "min": 100,
        "max": 1000
    },
    "randomiser_constants": {               # The randomiser constants for the light
        "location": {                       # The randomiser constants for the light location 
        "x": 0.1,                           # The x randomiser constant for the light location
        "y": 0.1,                           # The y randomiser constant for the light location
            "z": 0.1                        # The z randomiser constant for the light location
        },
        "rotation": {                       # The randomiser constants for the light rotation
            "x": 0.1,                       # The x randomiser constant for the light rotation
            "y": 0.1,                       # The y randomiser constant for the light rotation
            "z": 0.1                        # The z randomiser constant for the light rotation
        }
    }
}

# Scene config
scene_config = {
    "name": "Test Scene",                   # The name of the scene
    "resolution": {
        "x": 1920,                          # The width of the scene
        "y": 1080,                          # The height of the scene
        "percentage": 100                   # The percentage of the scene resolution
    },
    "engine": "CYCLES",                     # The rendering engine to use
    "grid": {
        "size": 10,                         # The size of each grid cell
        "spacing": 10,                      # The spacing of each grid cell
        "width": 10,                        # The width of the grid
        "height": 10,                       # The height of the grid
        "default_colour": {
            "r": 0.5,                       # The red value of the default colour
            "g": 0.5,                       # The green value of the default colour
            "b": 0.5,                       # The blue value of the default colour
            "a": 1.0                        # The alpha value of the default colour
        }
    },
    "cycles": {
        "use_progressive_refine": False,    # Whether to use progressive refinement
        "tile_size": 256,                   # The tile size of the rendering
        "use_persistent_data": True,        # Whether to use persistent data
        "samples": 64,                      # The number of samples to use
        "use_adaptive_sampling": True,      # Whether to use adaptive sampling
        "adaptive_threshold": 0.02,         # The adaptive threshold
        "use_denoising": True,              # Whether to use denoising
        "max_bounces": 4,                   # The maximum number of bounces
        "diffuse_bounces": 2,               # The number of diffuse bounces
        "glossy_bounces": 2,                # The number of glossy bounces
        "sample_clamp_indirect": 1.0        # The sample clamp indirect
    },
    "clip_start": 0.1,                      # The near clipping plane of the camera
    "clip_end": camera_config["position"]["z"] * 2  # The far clipping plane of the camera
}

# Object config
object_config = {
    "max_scale": 5.0,
    "denominator_range": [1, 10],
    "max_collision_check_amount": 100
}

# Paths config
paths_config = {
    "models":   "./models",
    "images":   "./images",
    "labels":   "./labels",
    "vis":      "./images/vis",
    "textures": "./textures"
}

# Output config
output_config = {
    "classes": [
        "class0",
        "class1",
        "class2"
    ],
    "class_colours": [
        [1.0, 0.0, 0.0],
        [0.0, 1.0, 0.0],
        [0.0, 0.0, 1.0]
    ]
}

# Merge the config dictionaries into a single config dictionary
config = {
    "camera": camera_config,
    "light": light_config,
    "scene": scene_config,
    "object": object_config,
    "paths": paths_config,
    "output": output_config,
    "create_visualization": True
}