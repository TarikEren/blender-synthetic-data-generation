# Blender Bounding Box Generator

This project enables the user to create `synthetic data` labeled with `2D bounding boxes`.

## Features

- Runs Blender in headless mode
- Creates random 3D scenes with given models
- Positions objects without collisions
- Uses different lighting setups for visual variety
- Calculates accurate 2D bounding boxes for each object
- Exports bounding boxes in YOLO format
- Optionally creates visualization images to verify bounding box accuracy

## Project Structure

The project has been organized into separate files for better maintainability:

TODO: CHANGE
- **main.py**: Driver script that handles command-line arguments and orchestrates the generation process
- **utils.py**: Utility functions for scene setup, object creation, bounding box calculation, and visualization

## Requirements

- Git
- Blender 4 or newer
- Python 3.7+
- OpenCV (`cv2`) for visualization

## Installation

1. Make sure Blender is installed on your system
2. Start up a terminal instance at wherever you want.
3. Clone the repository using the following command:
```bash
git clone https://github.com/TarikEren/blender-synthetic-data-generation.git
```

## Usage
Your terminal should be able to run command `blender` without any issues to start using the program.

After making sure blender works fine run the following command

```bash
blender --background --python main.py
```

to start generating data with the provided `config.py` file

### Output

The script generates the following output:

- **./images/image_XXX.png**: Rendered scenes
- **./images/vis/vis_XXX.png**: Visualization images with bounding boxes
- **./labels/image_XXX.txt**: YOLO format bounding box coordinates

### YOLO Format

The bounding box format used is:
```
<class_id> <x_center> <y_center> <width> <height>
```

TODO: ADD DETAILS
Where:
- `class_id` is an integer (0-4) representing the object type:
- All other values are normalized to [0,1]
- (0,0) is the top-left corner of the image

## Customization

TODO: CHANGE

You can modify various aspects of the generator:

- Edit `config.json` to change various settings 
- Edit `utils.py` to change object types, materials, lighting setups, etc.
- Adjust the number of objects per scene in `create_objects` function (default: 7)
- Change render settings in `setup_scene` function
- Modify camera position and field of view in `create_camera` function 