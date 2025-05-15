# Blender Bounding Box Generator

This project generates 3D objects in Blender, renders them from a top-down camera view, calculates their 2D bounding boxes, and exports them in YOLO format.

## Features

- Runs Blender in headless mode
- Creates random 3D scenes with varied objects
- Positions objects without collisions
- Uses different lighting setups for visual variety
- Calculates accurate 2D bounding boxes for each object
- Exports bounding boxes in YOLO format
- Creates visualization images to verify bounding box accuracy

## Project Structure

The project has been organized into separate files for better maintainability:

- **main.py**: Driver script that handles command-line arguments and orchestrates the generation process
- **/blender_utils**: Contains the utility functions
   - ***asset_utils.py*** Asset utility functions for:
      - Finding textures
      - Importing models
      - Finding models
   - ***bbox_utils.py***: Bounding box utilty functions for:
      - Bounding box calculations
      - Transforming labels into YOLO format
      - Visualising the labels for verification
   - ***camera_utils.py***: Camera utilty functions for:
      - Camera creation
      - Converting 3D world coordinates to 2D pixel coordinates
   - ***image_utils.py*** Image generation utility functions for:
      - Generating a single image
   - ***lighting_utils.py*** Lighting utility functions for:
      - Creating lighting
   - ***logger_utils.py*** Logger utility functions for:
      - Creatting a logger
   - ***object_utils.py*** Object utility functions for:
      - Object creation
      - Collision checks
      - Finding valid positions for objects
   - ***scene_utils.py***: Scene utility functions for:
      - Scene creation
      - Clearing the scene
      - Creating a textured plane

## Requirements

- Blender 2.93 or newer
- Python 3.7+
- OpenCV (`cv2`) for visualization

## Installation

1. Make sure Blender is installed on your system
2. Install OpenCV (if not already installed with Blender):
   ```
   pip install opencv-python
   ```

## Usage

### Running Headlessly

To run the program with default settings (Renders a single image):

```bash
blender --background --python main.py
```

Or you can provide a count with the following command

```bash
blender --background --python main.py -- --num-images 20
```

### Command-line Arguments

- `--num-images`    : Number of images to generate (default: 10)
- `--custom-model`  : Path to a custom model to be used

### Output

The script generates the following output:

- **./images/image_XXX.png**: Rendered scenes
- **./images/vis_XXX.png**: Visualization images with bounding boxes
- **./labels/image_XXX.txt**: YOLO format bounding box coordinates

### YOLO Format

The bounding box format used is:
```
<class_id> <x_center> <y_center> <width> <height>
```

Where:
- `class_id` is an integer (0-4) representing the object type:
- All other values are normalized to [0,1]
- (0,0) is the top-left corner of the image

## Customization

You can modify various aspects of the generator:

- Edit `utils.py` to change object types, materials, lighting setups, etc.
- Adjust the number of objects per scene in `create_objects` function (default: 7)
- Change render settings in `setup_scene` function
- Modify camera position and field of view in `create_camera` function 