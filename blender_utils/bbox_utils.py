"""
Bounding Box Utilities for Blender Bounding Box Generator

This module contains utility functions for calculating and managing bounding boxes in Blender.
"""

# Standard Library Imports
import cv2

# Local Imports
from .logger_utils import logger
from .camera_utils import bpy_coords_to_pixel_coords

# Configuration
from config import config

def calculate_bounding_boxes(scene, camera, objects):
    """Calculate 2D bounding boxes for 3D objects in the scene.
    
    Args:
        scene: The Blender scene
        camera: The camera object
        objects: List of objects to calculate bounding boxes for
        
    Returns:
        List of dictionaries containing bounding box data
    """
    bounding_boxes = []
    
    # Get render dimensions
    render = scene.render
    res_x = render.resolution_x
    res_y = render.resolution_y
    
    for obj in objects:
        # Skip all background planes
        if obj.type == 'MESH' and obj.name.startswith("Background_Plane"):
            continue
            
        # Get all vertices in world space
        vertices = []
        mesh = obj.data
        for vertex in mesh.vertices:
            # Convert vertex coordinates to world space
            world_co = obj.matrix_world @ vertex.co
            vertices.append(world_co)
        
        # Project vertices to 2D using the camera
        bbox_2d = []
        for vertex in vertices:
            co_2d = bpy_coords_to_pixel_coords(scene, camera, vertex)
            bbox_2d.append(co_2d)
        
        # Calculate min/max values for x and y coordinates
        min_x = min(point[0] for point in bbox_2d)
        max_x = max(point[0] for point in bbox_2d)
        min_y = min(point[1] for point in bbox_2d)
        max_y = max(point[1] for point in bbox_2d)
        
        # Ensure coordinates are within image bounds
        min_x = max(0, min(min_x, res_x))
        max_x = max(0, min(max_x, res_x))
        min_y = max(0, min(min_y, res_y))
        max_y = max(0, min(max_y, res_y))
        
        # Store bounding box and class index
        class_idx = obj.get('class_idx', 0)
        
        # Calculate YOLO format (x_center, y_center, width, height) normalized to [0,1]
        # YOLO format expects y to start from top, but Blender's coords start from bottom
        # So we need to invert the y coordinates: y_normalized = 1 - y_normalized
        x_center = (min_x + max_x) / 2 / res_x
        y_center = 1 - (min_y + max_y) / 2 / res_y  # Inverted y-axis
        width = (max_x - min_x) / res_x
        height = (max_y - min_y) / res_y
        
        # Add a small padding to ensure the bounding box fully contains the object
        padding = 0.01  # 1% padding
        width = min(1.0, width * (1 + padding))
        height = min(1.0, height * (1 + padding))
        
        bounding_boxes.append({
            'class_idx': class_idx,
            'x_center': x_center,
            'y_center': y_center,
            'width': width,
            'height': height,
            'min_x': min_x,
            'min_y': min_y,
            'max_x': max_x,
            'max_y': max_y
        })
    
    return bounding_boxes

def save_yolo_format(bounding_boxes, output_path):
    """Save bounding boxes in YOLO format.
    
    Args:
        bounding_boxes: List of bounding box dictionaries
        output_path: Path to save the YOLO format file
    """
    with open(output_path, 'w') as f:
        for box in bounding_boxes:
            # YOLO format: class_idx x_center y_center width height
            # All values are normalized to [0,1]
            f.write(f"{box['class_idx']} {box['x_center']:.6f} {box['y_center']:.6f} {box['width']:.6f} {box['height']:.6f}\n")

def visualize_bounding_boxes(image_path, bbox_file, output_path):
    """Create a visualization of bounding boxes on the rendered image.
    
    Args:
        image_path: Path to the rendered image
        bbox_file: Path to the YOLO format bounding box file
        output_path: Path to save the visualization
    """
    # Read the image
    img = cv2.imread(image_path)
    if img is None:
        logger.error(f"Could not read image: {image_path}")
        return
        
    # Get image dimensions
    height, width, _ = img.shape
    logger.debug(f"Image dimensions: {width}x{height}")
    
    # Read YOLO format bounding boxes
    try:
        with open(bbox_file, 'r') as f:
            lines = f.readlines()
    except Exception as e:
        logger.error(f"Error reading bbox file: {str(e)}")
        return
        
    logger.debug(f"Found {len(lines)} bounding boxes to visualize")
    
    # Colors for visualization (BGR format)
    colors = config["output"]["class_colours"]
    
    # Draw bounding boxes on the image
    for line in lines:
        parts = line.strip().split()
        if len(parts) == 5:
            try:
                class_idx = int(parts[0])
                x_center = float(parts[1]) * width
                y_center = float(parts[2]) * height
                box_width = float(parts[3]) * width
                box_height = float(parts[4]) * height
                
                # Calculate (x1, y1) and (x2, y2) coordinates
                x1 = int(x_center - box_width / 2)
                y1 = int(y_center - box_height / 2)
                x2 = int(x_center + box_width / 2)
                y2 = int(y_center + box_height / 2)
                
                # Ensure coordinates are within image bounds
                x1 = max(0, min(x1, width))
                y1 = max(0, min(y1, height))
                x2 = max(0, min(x2, width))
                y2 = max(0, min(y2, height))
                
                # Get color for this class
                color = colors[class_idx % len(colors)]
                
                # Draw rectangle
                cv2.rectangle(img, (x1, y1), (x2, y2), color, 2)
                
                # Draw class label
                class_name = config["output"]["classes"][class_idx]
                cv2.putText(img, class_name, (x1, y1 - 10), 
                           cv2.FONT_HERSHEY_SIMPLEX, 0.9, color, 2)
                
                logger.debug(f"Drew box for class {class_name} at ({x1}, {y1}) to ({x2}, {y2})")
                
            except Exception as e:
                logger.error(f"Error processing bounding box line: {str(e)}")
                continue
    
    # Save annotated image
    try:
        cv2.imwrite(output_path, img)
        logger.info(f"Saved visualization to: {output_path}")
    except Exception as e:
        logger.error(f"Error saving visualization: {str(e)}") 