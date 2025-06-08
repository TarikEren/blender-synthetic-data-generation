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
- **/models**: Directory containing .obj models. It has to conform to the format of:
```
    models/
        class1/
            model_name.obj
        class2/
            model_name.obj
            ...
```
   - The models should have their up axis set as Z and front axis X.
   - The program currently supports classes:
      - tank
      - aircraft
      - helicopter
      - armored_vehicle

      other vehicle models might result in unknown behaivour.

- **/textures**: Directory containing .blend textures
- **/images**: Directory containing the output images
- **/labels**: Directory containing the output labels
- **/visualisations**: Directory containing the label visualisations

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

- `--num-images`        : Number of images to generate (default: 10)
- `--visualise`         : Visualise the bounding boxes (default: False)
- `--starting-filename` : Starting filename of the images and labels. In the format of `image_xxxx`. The program increments the index count by one after each image. Useful if you want to append new images to your already existing dataset. (default: None)

### Output

The script generates the following output:

- **./images/image_XXX.png**: Rendered scenes
- **./labels/image_XXX.txt**: YOLO format bounding box coordinates
- **./visualisations/vis_XXX.png**: Visualization images with bounding boxes

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


## Known Issues
- The rendered aircraft models can have a acute or obtuse rotation. In that case, check your model's axes. The model's up axis should be Z and front axis should be X. This can be fixed by importing the model and exporting it with the required axis values or simply rotating the aircraft so that its nose points upwards.
- In case of `Error in main 'model_name' is not in list`, make sure that the files of the model `model_name` conforms to the directory requirements listed at the top underneath [Project Structure](#project-structure).