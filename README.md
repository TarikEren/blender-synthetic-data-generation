# Blender Bounding Box Generator

This script generates 3D objects in Blender, renders them from a top-down camera view, calculates their 2D bounding boxes, and exports them in YOLO format.

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
blender --background --python blender_bbox_generator.py
```

### What the Script Does

1. Clears any existing scene
2. Sets up a new scene with appropriate render settings
3. Creates a camera at position (0, 0, 50) looking straight down
4. Generates random 3D objects (cubes, spheres, cones, cylinders, and tori)
5. Calculates 2D bounding boxes for each object
6. Saves bounding boxes in YOLO format (class_idx, x_center, y_center, width, height)
7. Renders the scene as an image
8. Creates a visualization that shows the bounding boxes overlaid on the rendered image

### Output Files

The script generates three files in the same directory:

1. `rendered_image.png` - The rendered scene
2. `bounding_boxes.txt` - YOLO format bounding boxes
3. `visualization.png` - Image with bounding boxes overlaid for verification

## YOLO Format

The bounding box format used is:
```
<class_id> <x_center> <y_center> <width> <height>
```

Where:
- `class_id` is an integer (0-4) representing the object type
- All other values are normalized to [0,1]
- (0,0) is the top-left corner of the image

## Customization

You can modify the script to:
- Change the number of objects by editing the `num_objects` parameter in the `main()` function
- Adjust camera position and field of view
- Change render resolution
- Add more object types 