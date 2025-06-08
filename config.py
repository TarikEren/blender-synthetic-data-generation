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
    "focal_length": 50,                     # The focal length of the camera
    "clip_start": 0.1,                      # The near clipping plane of the camera
    "clip_end": 100 * 2                     # The far clipping plane of the camera (Twice the camera height)
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
        "z": 0.1                            # The z randomiser constant for the light location
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
    "name": "Synthetic Dataset",            # The name of the scene
    "resolution": {
        "x": 1920,                          # The width of the scene
        "y": 1080,                          # The height of the scene
        "percentage": 100                   # The percentage of the scene resolution
    },
    "default_background": (1, 1, 1, 1),     # The default background colour
    "default_background_strength": 1,       # The default background strength
    "engine": "CYCLES",                     # The rendering engine to use
    "grid": {
        "size": 40,                         # The size of each grid cell
        "spacing": 10,                      # The spacing of each grid cell
        "width": 10,                        # The width of the grid
        "height": 10,                       # The height of the grid
        "default_colour": {
            "r": 0.25,                       # The red value of the default colour
            "g": 0.25,                       # The green value of the default colour
            "b": 0.25,                       # The blue value of the default colour
            "a": 1.0                        # The alpha value of the default colour
        }
    },
    "ground_plane": {
        "size": 40,                         # Size of each ground plane
        "col": 3,                           # The column size of the ground plane grid
        "row": 3,                           # The row size of the ground plane grid
        "default_colour": (1, 1, 1, 1),     # Default colour of the background
        "colour_strength": 1                # Background colour strength
    },
    "cycles": {
        "use_progressive_refine": False,    # Whether to use progressive refinement
        "tile_size": 256,                   # The tile size of the rendering
        "use_persistent_data": True,        # Whether to use persistent data
        "samples": 64,                      # The number of samples to use
        "use_adaptive_sampling": True,      # Whether to use adaptive sampling
        "adaptive_threshold": 0.02,         # The adaptive threshold
        "adaptive_min_samples": 64,         # Minimum samples before adaptive sampling kicks in
        "use_denoising": True,              # Whether to use denoising
        "use_denoising_prefilter": True,    # Whether to use denoising prefilter
        "max_bounces": 4,                   # The maximum number of bounces
        "diffuse_bounces": 2,               # The number of diffuse bounces
        "glossy_bounces": 2,                # The number of glossy bounces
        "sample_clamp_indirect": 1.0,       # The sample clamp indirect
        "sample_count": 128                 # The number of samples to use
    },
    "clip_start": 0.1,                      # The near clipping plane of the camera
    "clip_end": camera_config["position"]["z"] * 2  # The far clipping plane of the camera
}

# Object config
object_config = {
    "max_scale": 5.0,                      # The maximum scale of the object    
    "denominator_range": [1, 10],          # The range of the denominator which will divide the max scale value to generate randomised scale values
    "max_collision_check_amount": 100,     # The maximum number of collision checks to perform
    "spread_factor_range": (0.6, 1.0),      # How spread out objects are (1.0 = full spread)
    "x_center_offset_range": (-5, 5),       # x offset of the object
    "y_center_offset_range": (-5, 5),       # y offset of the object
    "random_rotation_range": (0, 3.14),     # Random rotation to be applied on the object
    "random_x_range": (-10, 10),            # Random range for x position of the object
    "random_y_range": (-10, 10),            # Random range for y position of the object
    "random_z_range": (0, 3),               # Random range for z position of the object
    "default_colour": (0.8, 0.8, 0.8, 1),   # Default colour for the ground plane
    "scale_variation_range": (1, 1.15)      # The range of the scale variation of the object
}

# Paths config
paths_config = {
    "models":   "./models",                 # The path to the models
    "images":   "./images",                 # The path to the images
    "labels":   "./labels",                 # The path to the labels
    "vis":      "./visualisations",         # The path to the visualisations
    "textures": "./textures"                # The path to the textures
}

dataset_config = {
    "train_ratio": 0.8,
    "test_ratio": 0.1,
    "val_ratio": 0.1
}

# Merge the config dictionaries into a single config dictionary
config = {
    "camera": camera_config,
    "light": light_config,
    "scene": scene_config,
    "object": object_config,
    "paths": paths_config,
    "dataset": dataset_config,
    "create_visualization": True
}