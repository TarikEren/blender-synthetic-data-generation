"""
Blender Bounding Box Generator Utilities

This module contains utility functions for generating 3D objects in Blender,
rendering them, calculating their 2D bounding boxes, and exporting them in YOLO format.
"""

#------------------------------------------------------------------------------
# IMPORTS
#------------------------------------------------------------------------------
import bpy
import numpy as np
import os
import math
from mathutils import Vector # type: ignore
import cv2
import random

#------------------------------------------------------------------------------
# SCENE SETUP AND MANAGEMENT
#------------------------------------------------------------------------------
def clear_scene():
    """Remove all objects, materials, meshes and lights from the scene."""
    bpy.ops.object.select_all(action='SELECT')
    bpy.ops.object.delete()
    
    # Clear all materials
    for material in bpy.data.materials:
        bpy.data.materials.remove(material)
    
    # Clear all meshes
    for mesh in bpy.data.meshes:
        bpy.data.meshes.remove(mesh)
        
    # Clear all lights
    for light in bpy.data.lights:
        bpy.data.lights.remove(light)

def setup_scene():
    """Configure scene settings for rendering."""
    # Create a new scene with all default settings
    scene = bpy.context.scene
    
    # Configure render settings
    scene.render.engine = 'CYCLES'  # Use Cycles renderer
    
    # Enable GPU rendering
    prefs = bpy.context.preferences
    cuda_prefs = prefs.addons['cycles'].preferences
    
    # Print available devices for debugging
    print("\nAvailable Devices:")
    for device in cuda_prefs.devices:
        print(f"Device: {device.name}, Type: {device.type}, Use: {device.use}")
    
    # Force CUDA compute type and refresh devices
    cuda_prefs.compute_device_type = 'CUDA'
    cuda_prefs.refresh_devices()
    
    # Enable all available CUDA devices
    for device in cuda_prefs.devices:
        if device.type == 'CUDA':
            device.use = True
            print(f"Enabled CUDA device: {device.name}")
    
    # Set render settings for faster preview
    scene.render.resolution_x = 1920
    scene.render.resolution_y = 1080
    scene.render.resolution_percentage = 100
    scene.render.filepath = '//rendered_image.png'
    
    # Optimize render settings for GPU
    scene.cycles.device = 'GPU'
    scene.cycles.tile_size = 256  # Larger tile size for GPU
    scene.cycles.samples = 128    # Reduced samples for faster preview
    scene.cycles.use_denoising = True  # Enable denoising for cleaner results
    
    # Additional GPU optimizations
    scene.cycles.use_adaptive_sampling = True
    scene.cycles.adaptive_threshold = 0.01
    scene.cycles.adaptive_min_samples = 64
    scene.cycles.use_denoising_prefilter = True
    
    # Force GPU compute
    scene.cycles.feature_set = 'EXPERIMENTAL'
    scene.cycles.use_denoising_prefilter = True
    scene.cycles.use_denoising_denoising = True
    
    # Print render settings for verification
    print("\nRender Settings:")
    print(f"Device: {scene.cycles.device}")
    print(f"Tile Size: {scene.cycles.tile_size}")
    print(f"Samples: {scene.cycles.samples}")
    print(f"Denoising: {scene.cycles.use_denoising}")
    print(f"Feature Set: {scene.cycles.feature_set}")
    
    # Adjust world settings (simple white background)
    world = bpy.data.worlds['World']
    world.use_nodes = True
    bg_node = world.node_tree.nodes['Background']
    bg_node.inputs[0].default_value = (1, 1, 1, 1)  # White background
    bg_node.inputs[1].default_value = 1.0  # Strength
    
    return scene

#------------------------------------------------------------------------------
# CAMERA FUNCTIONS
#------------------------------------------------------------------------------
def create_camera():
    """Create a camera positioned above the scene looking down."""
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

#------------------------------------------------------------------------------
# LIGHTING FUNCTIONS
#------------------------------------------------------------------------------
def setup_lighting(seed=None):
    """Create randomized lighting setup for the scene."""
    if seed is not None:
        random.seed(seed)
    
    # Delete existing lights
    for obj in bpy.data.objects:
        if obj.type == 'LIGHT':
            bpy.data.objects.remove(obj)
    
    # Determine lighting style for this scene
    lighting_style = random.choice(['three_point', 'studio', 'outdoor', 'dramatic'])
    
    if lighting_style == 'three_point':
        # Key light (main light)
        key_light = bpy.data.objects.new(name="KeyLight", object_data=bpy.data.lights.new(name="KeyLight", type='AREA'))
        key_light.location = (random.uniform(8, 12), random.uniform(-5, 5), random.uniform(10, 15))
        key_light.rotation_euler = (random.uniform(0, 0.5), random.uniform(-0.5, 0.5), random.uniform(-0.5, 0.5))
        bpy.context.collection.objects.link(key_light)
        key_light.data.energy = random.uniform(800, 1200)
        key_light.data.size = random.uniform(5, 10)
        
        # Fill light (softer, less intense)
        fill_light = bpy.data.objects.new(name="FillLight", object_data=bpy.data.lights.new(name="FillLight", type='AREA'))
        fill_light.location = (random.uniform(-12, -8), random.uniform(-5, 5), random.uniform(8, 12))
        bpy.context.collection.objects.link(fill_light)
        fill_light.data.energy = random.uniform(300, 500)
        fill_light.data.size = random.uniform(8, 15)
        
        # Back light (rim light)
        back_light = bpy.data.objects.new(name="BackLight", object_data=bpy.data.lights.new(name="BackLight", type='AREA'))
        back_light.location = (random.uniform(-3, 3), random.uniform(-12, -8), random.uniform(12, 15))
        bpy.context.collection.objects.link(back_light)
        back_light.data.energy = random.uniform(500, 700)
        back_light.data.size = random.uniform(3, 6)
        
    elif lighting_style == 'studio':
        # Soft overhead lighting
        for i in range(4):
            light = bpy.data.objects.new(name=f"StudioLight{i}", object_data=bpy.data.lights.new(name=f"StudioLight{i}", type='AREA'))
            x = random.uniform(-8, 8)
            y = random.uniform(-8, 8)
            light.location = (x, y, random.uniform(10, 15))
            bpy.context.collection.objects.link(light)
            light.data.energy = random.uniform(300, 500)
            light.data.size = random.uniform(4, 8)
            
    elif lighting_style == 'outdoor':
        # Sun light (directional)
        sun = bpy.data.objects.new(name="Sun", object_data=bpy.data.lights.new(name="Sun", type='SUN'))
        sun.location = (random.uniform(-5, 5), random.uniform(-5, 5), random.uniform(15, 20))
        sun.rotation_euler = (random.uniform(0, 0.8), random.uniform(-0.8, 0.8), random.uniform(-0.8, 0.8))
        bpy.context.collection.objects.link(sun)
        sun.data.energy = random.uniform(2, 5)
        
        # Ambient light
        ambient = bpy.data.objects.new(name="Ambient", object_data=bpy.data.lights.new(name="Ambient", type='AREA'))
        ambient.location = (0, 0, random.uniform(10, 15))
        ambient.scale = (20, 20, 1)
        bpy.context.collection.objects.link(ambient)
        ambient.data.energy = random.uniform(100, 300)
        
    elif lighting_style == 'dramatic':
        # Strong single light source
        main_light = bpy.data.objects.new(name="DramaticLight", object_data=bpy.data.lights.new(name="DramaticLight", type='SPOT'))
        main_light.location = (random.uniform(-10, 10), random.uniform(-10, 10), random.uniform(12, 18))
        main_light.rotation_euler = (random.uniform(0, 0.8), random.uniform(-0.8, 0.8), random.uniform(-0.8, 0.8))
        bpy.context.collection.objects.link(main_light)
        main_light.data.energy = random.uniform(1000, 2000)
        main_light.data.spot_size = random.uniform(0.5, 1.2)
        
        # Subtle fill light
        fill = bpy.data.objects.new(name="DramaticFill", object_data=bpy.data.lights.new(name="DramaticFill", type='AREA'))
        fill.location = (-main_light.location.x, -main_light.location.y, random.uniform(5, 10))
        bpy.context.collection.objects.link(fill)
        fill.data.energy = random.uniform(100, 200)
    
    # Reset random seed
    if seed is not None:
        random.seed()

#------------------------------------------------------------------------------
# OBJECT GENERATION
#------------------------------------------------------------------------------
def create_objects(num_objects=5, distribution_seed=None):
    """Create random 3D objects within the camera's field of view.
    
    Args:
        num_objects: Number of objects to create
        distribution_seed: Seed for random number generator
        
    Returns:
        List of created objects
    """
    # Set a random seed for this distribution if provided
    if distribution_seed is not None:
        random.seed(distribution_seed)
        
    objects = []
    object_classes = ['cube', 'sphere', 'cone', 'cylinder', 'torus']
    
    # Determine positioning strategy for this batch
    # Sometimes cluster objects, sometimes spread them out
    spread_factor = random.uniform(0.6, 1.0)  # How spread out objects are (1.0 = full spread)
    x_center_offset = random.uniform(-5, 5)   # Shift the center of distribution
    y_center_offset = random.uniform(-5, 5)
    
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
            # Randomly position within visible area with the custom distribution
            x = random.uniform(-10, 10) * spread_factor + x_center_offset
            y = random.uniform(-10, 10) * spread_factor + y_center_offset
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
    
    # Reset random seed if we changed it
    if distribution_seed is not None:
        random.seed()
        
    return objects

#------------------------------------------------------------------------------
# BOUNDING BOX CALCULATION
#------------------------------------------------------------------------------
def bpy_coords_to_pixel_coords(scene, camera, coord):
    """Convert 3D world coordinates to 2D pixel coordinates using the camera projection.
    
    Args:
        scene: The Blender scene
        camera: The camera object
        coord: 3D coordinate to project
        
    Returns:
        Tuple of (x, y) pixel coordinates
    """
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

#------------------------------------------------------------------------------
# VISUALIZATION
#------------------------------------------------------------------------------
def visualize_bounding_boxes(image_path, bbox_file, output_path):
    """Create a visualization of bounding boxes on the rendered image.
    
    Args:
        image_path: Path to the rendered image
        bbox_file: Path to the YOLO format bounding box file
        output_path: Path to save the visualization
    """
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

#------------------------------------------------------------------------------
# IMAGE GENERATION
#------------------------------------------------------------------------------
def import_custom_model(model_path):
    """Import a custom 3D model into the scene."""
    print(f"\nAttempting to import model from: {model_path}")
    
    # Clear the scene first
    clear_scene()
    
    # Import the model based on file extension
    file_ext = os.path.splitext(model_path)[1].lower()
    print(f"File extension: {file_ext}")
    
    try:
        # Store the current object names
        existing_objects = set(obj.name for obj in bpy.data.objects)
        
        # Import based on file type
        if file_ext == '.obj':
            print("Importing OBJ file...")
            try:
                # First try the new method (Blender 4.x)
                if hasattr(bpy.ops.wm, 'obj_import'):
                    bpy.ops.wm.obj_import(filepath=model_path)
                # Then try the legacy method
                elif hasattr(bpy.ops.import_scene, 'obj'):
                    bpy.ops.import_scene.obj(filepath=model_path)
                else:
                    raise ImportError("No OBJ import operator found")
            except Exception as e:
                print(f"Import error: {str(e)}")
                raise
        elif file_ext == '.fbx':
            print("Importing FBX file...")
            if hasattr(bpy.ops.wm, 'fbx_import'):
                bpy.ops.wm.fbx_import(filepath=model_path)
            else:
                bpy.ops.import_scene.fbx(filepath=model_path)
        elif file_ext == '.blend':
            print("Importing Blend file...")
            bpy.ops.wm.append(filepath=model_path)
        else:
            raise ValueError(f"Unsupported file format: {file_ext}")
        
        # Find newly added objects
        new_objects = [obj for obj in bpy.data.objects if obj.name not in existing_objects]
        print(f"New objects after import: {new_objects}")
        
        if not new_objects:
            raise ValueError("No new objects were imported")
            
        # Get the main imported object (usually the first one)
        imported_obj = new_objects[0]
        print(f"Using imported object: {imported_obj.name}")
        
        # Store the object's name for later reference
        obj_name = imported_obj.name
        
        try:
            # Set a custom property to identify this as a custom model
            bpy.data.objects[obj_name]['class_idx'] = 0
            
            # Get object dimensions before any changes
            dims = bpy.data.objects[obj_name].dimensions.copy()
            max_dim = max(dims)
            
            if max_dim > 0:  # Avoid division by zero
                # Calculate scale to make largest dimension 5 units
                scale_factor = 5.0 / max_dim
                
                # Scale and position the object
                obj = bpy.data.objects[obj_name]
                obj.scale = (scale_factor, scale_factor, scale_factor)
                
                # Reset all rotations first
                obj.rotation_euler = (0, 0, 0)
                
                # Apply 90 degrees counter-clockwise rotation around all axes
                # Note: math.pi/2 is 90 degrees
                obj.rotation_euler = (math.pi/2, math.pi/2, math.pi/2)
                
                # Update the scene to apply rotation
                bpy.context.view_layer.update()
                
                # Position slightly above ground after rotation
                obj.location = (0, 0, 2)
                
                print(f"Adjusted object scale to {scale_factor}, rotated 90 degrees on X, Y, and Z axes, and positioned at height 2")
            else:
                print("Warning: Object has zero dimensions")
            
        except Exception as e:
            print(f"Warning: Error during object adjustment: {str(e)}")
            print("Continuing with unadjusted object...")
        
        return obj_name  # Return the name instead of the object reference
        
    except Exception as e:
        print(f"Error during model import: {str(e)}")
        raise

def generate_single_image(index, images_dir, labels_dir, custom_model_path=None):
    """Generate a single image with bounding boxes."""
    print(f"\nGenerating image {index+1}")
    print(f"Custom model path: {custom_model_path}")
    
    # Convert relative paths to absolute paths
    images_dir_abs = os.path.abspath(images_dir)
    labels_dir_abs = os.path.abspath(labels_dir)
    
    if custom_model_path:
        custom_model_abs = os.path.abspath(custom_model_path)
        print(f"Absolute custom model path: {custom_model_abs}")
        print(f"Custom model file exists: {os.path.exists(custom_model_abs)}")
    
    # Create directories if they don't exist
    os.makedirs(images_dir_abs, exist_ok=True)
    os.makedirs(labels_dir_abs, exist_ok=True)
    
    # Set up filenames for this image
    image_filename = f"image_{index:03d}.png"
    label_filename = f"image_{index:03d}.txt"
    render_path = os.path.join(images_dir_abs, image_filename)
    bbox_path = os.path.join(labels_dir_abs, label_filename)
    visualization_path = os.path.join(images_dir_abs, f"vis_{index:03d}.png")
    
    try:
        # Clear the scene
        clear_scene()
        
        # Setup scene
        scene = setup_scene()
        scene.render.filepath = render_path
        
        # Create camera
        camera = create_camera()
        
        # Setup randomized lighting using the image index as seed
        setup_lighting(seed=index+100)
        
        # Import or create objects
        if custom_model_path:
            print("Using custom model path...")
            try:
                # Get file extension
                file_ext = os.path.splitext(custom_model_path)[1].lower()
                print(f"File extension: {file_ext}")
                
                # Import custom model
                if file_ext == '.obj':
                    print("Importing OBJ file...")
                    if hasattr(bpy.ops.wm, 'obj_import'):
                        bpy.ops.wm.obj_import(filepath=custom_model_path)
                    else:
                        bpy.ops.import_scene.obj(filepath=custom_model_path)
                elif file_ext == '.fbx':
                    print("Importing FBX file...")
                    if hasattr(bpy.ops.wm, 'fbx_import'):
                        bpy.ops.wm.fbx_import(filepath=custom_model_path)
                    else:
                        bpy.ops.import_scene.fbx(filepath=custom_model_path)
                elif file_ext == '.blend':
                    print("Importing Blend file...")
                    bpy.ops.wm.append(filepath=custom_model_path)
                else:
                    raise ValueError(f"Unsupported file format: {file_ext}")
                
                # Find the imported mesh objects
                mesh_objects = [obj for obj in bpy.data.objects if obj.type == 'MESH']
                if not mesh_objects:
                    raise ValueError("No mesh objects found after import")
                
                # Set up the first mesh object
                obj = mesh_objects[0]
                obj['class_idx'] = 0
                
                # Scale and position the object
                dims = obj.dimensions
                max_dim = max(dims)
                if max_dim > 0:
                    scale_factor = 5.0 / max_dim
                    obj.scale = (scale_factor, scale_factor, scale_factor)
                    
                    # Reset all rotations first
                    obj.rotation_euler = (0, 0, 0)

                    # Update the scene to apply rotation
                    bpy.context.view_layer.update()
                    
                    # Position slightly above ground after rotation
                    obj.location = (0, 0, 2)
                    
                    print(f"Adjusted object scale to {scale_factor}, rotated 90 degrees on X, Y, and Z axes, and positioned at height 2")
                else:
                    print("Warning: Object has zero dimensions")
                
            except Exception as e:
                print(f"Error importing custom model: {str(e)}")
                raise
        else:
            print("No custom model path provided, creating random objects...")
            create_objects(num_objects=7, distribution_seed=index)
        
        # Get fresh list of objects for bounding box calculation
        current_objects = [obj for obj in bpy.data.objects if obj.type == 'MESH']
        if not current_objects:
            raise ValueError("No valid objects found for bounding box calculation")
        
        # Calculate bounding boxes
        bounding_boxes = calculate_bounding_boxes(scene, camera, current_objects)
        
        # Save bounding boxes in YOLO format
        save_yolo_format(bounding_boxes, bbox_path)
        
        # Render the scene
        bpy.ops.render.render(write_still=True)
        
        # Visualize and test the bounding boxes
        if os.path.exists(render_path) and os.path.exists(bbox_path):
            visualize_bounding_boxes(render_path, bbox_path, visualization_path)
        
        print(f"Image {index+1} rendered to: {render_path}")
        print(f"Labels saved to: {bbox_path}")
        
    except Exception as e:
        print(f"Error in generate_single_image: {str(e)}")
        raise
    finally:
        # Always try to clean up
        try:
            clear_scene()
        except:
            pass 