general_config = {
    "x_resolution": 1920,                   # x resolution of the image
    "y_resolution": 1080,                   # y resolution of the image
    "resolution_percentage": 100,           # Controls the resolution scaling of the final rendered image
    "max_collision_check_amount": 50,       # Count of maximum collision checks before yielding
    "tile_size": 256,                       # Sets the tile size for GPU rendering
    "sample_count": 128,                    # Controls the number of samples per pixel
    "use_denoising": True,                  # Enables denoising to reduce noise in the final render
    "use_adaptive_sampling": True,          # Enables adaptive sampling
    "adaptive_threshold": 0.01,             # Sets the threshold for adaptive sampling
    "adaptive_min_samples": 64,             # Defines minimum samples before adaptive sampling kicks in
    "use_denoising_prefilter": True,        # Enables denoising prefilter for better noise reduction
    "images_dir": "images",                 # Path to save the images to
    "labels_dir": "labels",                 # Path to save the labels to
    "visualisation_dir": "vis"              # Path to save the visualisations to (Note: The path must exist)
}

#------------------------------------------------------------------------------
# SCENE CONFIG
#------------------------------------------------------------------------------
scene_config = {
    "camera_height": 90,                        # Height of the camera
    "ground_plane_size": 40,                    # Size of each ground planes
    "ground_plane_col": 3,                      # The column size of the ground plane grid
    "ground_plane_row": 3,                      # The row size of the ground plane grid
    "background_default_colour": (1, 1, 1, 1),  # Default colour of the background
    "background_default_colour_strength": 1,
}

#------------------------------------------------------------------------------
# OBJECT CONFIG
#------------------------------------------------------------------------------
object_config = {
    "spread_factor_range": (0.6, 1.0),      # How spread out objects are (1.0 = full spread)
    "x_center_offset_range": (-5, 5),       # x offset of the object
    "y_center_offset_range": (-5, 5),       # y offset of the object
    "random_rotation_range": (0, 3.14),     # Random rotation to be applied on the object
    "random_x_range": (-10, 10),            # Random range for x position of the object
    "random_y_range": (-10, 10),            # Random range for y position of the object
    "random_z_range": (0, 3),               # Random range for z position of the object
    "default_colour": (0.8, 0.8, 0.8, 1),   # Default colour for the ground plane in case no textures were provided
    "max_scale": 5.0,                       # Maximum scale value of the provided custom model
    "denominator_range": (1, 20),           # The range of the denominator which will divide the max scale value to generate randomised scale values
    "scale_variation_range": (1, 1.15)      # The range of the scale variation of the object
}

#------------------------------------------------------------------------------
# CAMERA CONFIG
#------------------------------------------------------------------------------
camera_config = {
    "focal_length": 35,                             # Focal length of the camera
    "clip_start": 0.1,                              # Sets the near clipping plane (minimum distance from camera where objects will be rendered)
    "clip_end": scene_config["camera_height"] * 2   # Sets the far clipping plane (maximum distance from camera where objects will be rendered)
}

class_config = {
    "class_colours": [                      # Colours for each class 
        (0, 0, 255),    # Red for class 0
        (0, 255, 0),    # Green for class 1
        (255, 0, 0),    # Blue for class 2
        (255, 255, 0),  # Cyan for class 3
        (255, 0, 255)   # Magenta for class 4
    ],
    "classes": [                            # Names for each class
        "Aircraft",     # Used "aircraft" as this project is made for 
                        # generating aircraft imagery.
        "class1",
        "class2",
        "class3",
        "class4"
    ]
}