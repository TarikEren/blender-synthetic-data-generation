#!/usr/bin/env python3
import bpy
import numpy as np
import os
import math
import bmesh
from mathutils import Vector
import cv2
import random

# Clear existing objects
def clear_scene():
    bpy.ops.object.select_all(action='SELECT')
    bpy.ops.object.delete()
    
    # Clear all materials
    for material in bpy.data.materials:
        bpy.data.materials.remove(material)
    
    # Clear all meshes
    for mesh in bpy.data.meshes:
        bpy.data.meshes.remove(mesh)

# Set up the scene
def setup_scene():
    # Create a new scene with all default settings
    scene = bpy.context.scene
    
    # Configure render settings
    scene.render.engine = 'CYCLES'  # Use Cycles renderer
    scene.render.resolution_x = 1920
    scene.render.resolution_y = 1080
    scene.render.resolution_percentage = 100
    scene.render.filepath = '//rendered_image.png'
    
    # Adjust world settings (simple white background)
    world = bpy.data.worlds['World']
    world.use_nodes = True
    bg_node = world.node_tree.nodes['Background']
    bg_node.inputs[0].default_value = (1, 1, 1, 1)  # White background
    bg_node.inputs[1].default_value = 1.0  # Strength
    
    return scene

# Create a camera at position (0,0,50) looking down
def create_camera():
    bpy.ops.object.camera_add(location=(0, 0, 50))
    camera = bpy.context.active_object
    
    # Point camera straight down (negative Z-axis)
    camera.rotation_euler = (0, 0, 0)
    
    # Set camera parameters (adjust FOV as needed)
    camera_data = camera.data
    camera_data.lens = 35  # Focal length in mm
    camera_data.clip_start = 0.1
    camera_data.clip_end = 100
    
    # Set this camera as the active/scene camera
    bpy.context.scene.camera = camera
    
    return camera

# Create random objects within the camera's field of view
def create_objects(num_objects=5):
    objects = []
    object_classes = ['cube', 'sphere', 'cone', 'cylinder', 'torus']
    
    # Helper function to check collision with existing objects
    def is_colliding(position, obj_type, existing_objects):
        # Determine object radius based on type (approximate)
        if obj_type == 'cube':
            radius = 1.0  # Half of size 2
        elif obj_type == 'sphere':
            radius = 1.0
        elif obj_type == 'cone':
            radius = 1.0
        elif obj_type == 'cylinder':
            radius = 1.0
        elif obj_type == 'torus':
            radius = 1.5
        
        # Add some padding for better spacing
        radius += 0.5
        
        # Check distance to all existing objects
        for obj in existing_objects:
            obj_pos = obj.location
            # Get approximate radius of existing object
            obj_radius = 1.5  # Default for safety
            
            # Calculate distance between centers
            distance = math.sqrt(
                (position[0] - obj_pos[0])**2 + 
                (position[1] - obj_pos[1])**2 + 
                (position[2] - obj_pos[2])**2
            )
            
            # If distance is less than sum of radii, they collide
            if distance < (radius + obj_radius):
                return True
                
        # No collision found
        return False
    
    for i in range(num_objects):
        # Try to find a non-colliding position
        max_attempts = 50
        attempt = 0
        colliding = True
        
        # Randomly choose an object type
        obj_type = random.choice(object_classes)
        
        x, y, z = 0, 0, 0
        
        # Keep trying until we find a non-colliding position
        while colliding and attempt < max_attempts:
            # Randomly position within visible area (adjust x,y range to match camera FOV)
            x = random.uniform(-10, 10)
            y = random.uniform(-10, 10)
            z = random.uniform(0, 3)  # Height above ground
            
            # Check if this position would collide with existing objects
            colliding = is_colliding((x, y, z), obj_type, objects)
            attempt += 1
        
        # If we couldn't find a non-colliding position after max attempts,
        # just use the last position we tried and continue
        
        # Create the object based on type
        if obj_type == 'cube':
            bpy.ops.mesh.primitive_cube_add(size=2, location=(x, y, z))
            obj = bpy.context.active_object
            obj['class_idx'] = 0
        elif obj_type == 'sphere':
            bpy.ops.mesh.primitive_uv_sphere_add(radius=1, location=(x, y, z))
            obj = bpy.context.active_object
            obj['class_idx'] = 1
        elif obj_type == 'cone':
            bpy.ops.mesh.primitive_cone_add(radius1=1, location=(x, y, z))
            obj = bpy.context.active_object
            obj['class_idx'] = 2
        elif obj_type == 'cylinder':
            bpy.ops.mesh.primitive_cylinder_add(radius=1, location=(x, y, z))
            obj = bpy.context.active_object
            obj['class_idx'] = 3
        elif obj_type == 'torus':
            bpy.ops.mesh.primitive_torus_add(location=(x, y, z))
            obj = bpy.context.active_object
            obj['class_idx'] = 4
        
        # Add random rotation
        obj.rotation_euler = (
            random.uniform(0, 3.14),
            random.uniform(0, 3.14),
            random.uniform(0, 3.14)
        )
        
        # Create a random colored material
        mat = bpy.data.materials.new(name=f"Material_{i}")
        mat.use_nodes = True
        principled_bsdf = mat.node_tree.nodes.get('Principled BSDF')
        if principled_bsdf:
            principled_bsdf.inputs[0].default_value = (
                random.uniform(0.1, 1),
                random.uniform(0.1, 1),
                random.uniform(0.1, 1),
                1
            )
        
        # Assign material to object
        if obj.data.materials:
            obj.data.materials[0] = mat
        else:
            obj.data.materials.append(mat)
        
        objects.append(obj)
    
    # Create a plane for the ground
    bpy.ops.mesh.primitive_plane_add(size=40, location=(0, 0, 0))
    ground = bpy.context.active_object
    
    # Add a material to the ground
    mat = bpy.data.materials.new(name="Ground_Material")
    mat.use_nodes = True
    principled_bsdf = mat.node_tree.nodes.get('Principled BSDF')
    if principled_bsdf:
        principled_bsdf.inputs[0].default_value = (0.8, 0.8, 0.8, 1)  # Gray
    
    # Assign material to ground
    if ground.data.materials:
        ground.data.materials[0] = mat
    else:
        ground.data.materials.append(mat)
    
    return objects

# Calculate 2D bounding boxes for objects in the scene
def calculate_bounding_boxes(scene, camera, objects):
    bounding_boxes = []
    
    # Get render dimensions
    render = scene.render
    res_x = render.resolution_x
    res_y = render.resolution_y
    
    for obj in objects:
        # Get the 8 corners of the object's bounding box in world space
        bbox_corners = [obj.matrix_world @ Vector(corner) for corner in obj.bound_box]
        
        # Project 3D points to 2D using the camera
        bbox_2d = []
        for corner in bbox_corners:
            co_2d = bpy_coords_to_pixel_coords(scene, camera, corner)
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

# Helper function to convert 3D coordinates to 2D pixel coordinates
def bpy_coords_to_pixel_coords(scene, camera, coord):
    render = scene.render
    res_x = render.resolution_x
    res_y = render.resolution_y
    
    # Convert world coordinates to camera view coordinates
    co_local = camera.matrix_world.inverted() @ coord
    
    # Convert camera coordinates to normalized device coordinates
    if co_local.z == 0:
        # Avoid division by zero
        co_local.z = 0.0001
        
    co_2d = (co_local.x / -co_local.z, co_local.y / -co_local.z)
    
    # Convert normalized device coordinates to pixel coordinates
    render_scale = render.resolution_percentage / 100
    
    # Account for camera sensor size and lens
    camera_data = camera.data
    sensor_width = camera_data.sensor_width
    sensor_height = sensor_width * res_y / res_x
    pixel_x = res_x * render_scale * (co_2d[0] * camera_data.lens / sensor_width + 0.5)
    pixel_y = res_y * render_scale * (co_2d[1] * camera_data.lens / sensor_height + 0.5)
    
    return (pixel_x, pixel_y)

# Save bounding boxes in YOLO format
def save_yolo_format(bounding_boxes, output_path):
    with open(output_path, 'w') as f:
        for box in bounding_boxes:
            # YOLO format: class_idx x_center y_center width height
            # All values are normalized to [0,1]
            f.write(f"{box['class_idx']} {box['x_center']:.6f} {box['y_center']:.6f} {box['width']:.6f} {box['height']:.6f}\n")

# Create a visualization to test if bounding boxes are correct
def visualize_bounding_boxes(image_path, bbox_file, output_path):
    # Read the image
    img = cv2.imread(image_path)
    
    # Get image dimensions
    height, width, _ = img.shape
    
    # Read YOLO format bounding boxes
    with open(bbox_file, 'r') as f:
        lines = f.readlines()
    
    # Colors for visualization
    colors = [
        (0, 0, 255),    # Red for class 0 (cube)
        (0, 255, 0),    # Green for class 1 (sphere)
        (255, 0, 0),    # Blue for class 2 (cone)
        (255, 255, 0),  # Cyan for class 3 (cylinder)
        (255, 0, 255)   # Magenta for class 4 (torus)
    ]
    
    # Draw bounding boxes on the image
    for line in lines:
        parts = line.strip().split()
        if len(parts) == 5:
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
            
            # Draw rectangle and class label
            color = colors[class_idx % len(colors)]
            cv2.rectangle(img, (x1, y1), (x2, y2), color, 2)
            cv2.putText(img, f"Class {class_idx}", (x1, y1 - 10), 
                        cv2.FONT_HERSHEY_SIMPLEX, 0.9, color, 2)
    
    # Save annotated image
    cv2.imwrite(output_path, img)

# Main function to run the entire pipeline
def main():
    # Setup paths
    output_dir = os.path.dirname(bpy.data.filepath) or os.getcwd()
    render_path = os.path.join(output_dir, "rendered_image.png")
    bbox_path = os.path.join(output_dir, "bounding_boxes.txt")
    visualization_path = os.path.join(output_dir, "visualization.png")
    
    # Generate absolute paths
    render_path_abs = bpy.path.abspath(render_path)
    
    # Clear the scene
    clear_scene()
    
    # Setup scene
    scene = setup_scene()
    scene.render.filepath = render_path
    
    # Create camera
    camera = create_camera()
    
    # Create objects
    objects = create_objects(num_objects=7)  # Adjust number of objects as needed
    
    # Calculate bounding boxes
    bounding_boxes = calculate_bounding_boxes(scene, camera, objects)
    
    # Save bounding boxes in YOLO format
    save_yolo_format(bounding_boxes, bbox_path)
    
    # Render the scene
    bpy.ops.render.render(write_still=True)
    
    # Visualize and test the bounding boxes
    visualize_bounding_boxes(render_path_abs, bbox_path, visualization_path)
    
    print(f"Scene rendered to: {render_path_abs}")
    print(f"Bounding boxes saved to: {bbox_path}")
    print(f"Visualization saved to: {visualization_path}")

# Run the script
if __name__ == "__main__":
    main() 