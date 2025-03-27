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
- **utils.py**: Utility functions for scene setup, object creation, bounding box calculation, and visualization

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

To run Blender in headless mode with this script:

```bash
blender --background --python main.py -- --num-images 20
```

Or you can use the default settings:

```bash
blender --background --python main.py
```

### Command-line Arguments

- `--num-images`: Number of images to generate (default: 10)
- `--output-dir`: Directory to save output (default: script directory)

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
  - 0: Cube
  - 1: Sphere
  - 2: Cone
  - 3: Cylinder
  - 4: Torus
- All other values are normalized to [0,1]
- (0,0) is the top-left corner of the image

## Customization

You can modify various aspects of the generator:

- Edit `utils.py` to change object types, materials, lighting setups, etc.
- Adjust the number of objects per scene in `create_objects` function (default: 7)
- Change render settings in `setup_scene` function
- Modify camera position and field of view in `create_camera` function 