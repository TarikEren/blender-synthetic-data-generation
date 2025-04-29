"""
Blender Bounding Box Generator Utilities

This module contains utility functions for generating 3D objects in Blender,
rendering them, calculating their 2D bounding boxes, and exporting them in YOLO format.
"""

#------------------------------------------------------------------------------
# IMPORTS
#------------------------------------------------------------------------------
import os
import bpy
import cv2
import math
import random

from config import general_config, scene_config, camera_config, object_config, class_config

from mathutils import Vector # type: ignore

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
    scene.render.resolution_x = general_config["x_resolution"]
    scene.render.resolution_y = general_config["y_resolution"]
    scene.render.resolution_percentage = general_config["resolution_percentage"]
    scene.render.filepath = '//rendered_image.png'
    
    # Optimize render settings for GPU
    scene.cycles.device = 'GPU'
    scene.cycles.tile_size = general_config["tile_size"]            # Larger tile size for GPU
    scene.cycles.samples = general_config["sample_count"]           # Reduced samples for faster preview
    scene.cycles.use_denoising = general_config["use_denoising"]    # Enable denoising for cleaner results
    
    # Additional GPU optimizations
    scene.cycles.use_adaptive_sampling = general_config["use_adaptive_sampling"]
    scene.cycles.adaptive_threshold = general_config["adaptive_threshold"]
    scene.cycles.adaptive_min_samples = general_config["adaptive_min_samples"]
    scene.cycles.use_denoising_prefilter = general_config["use_denoising_prefilter"]
    
    # Force GPU compute
    scene.cycles.feature_set = 'EXPERIMENTAL'
    
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
    bg_node.inputs[0].default_value = scene_config["background_default_colour"]
    bg_node.inputs[1].default_value = scene_config["background_default_colour_strength"]
    
    return scene

#------------------------------------------------------------------------------
# CAMERA FUNCTIONS
#------------------------------------------------------------------------------
def create_camera():
    """Create a camera positioned above the scene looking down."""
    bpy.ops.object.camera_add(location=(0, 0, scene_config["camera_height"]))
    camera = bpy.context.active_object
    
    # Point camera straight down (negative Z-axis)
    camera.rotation_euler = (0, 0, 0)
    
    # Set camera parameters
    camera_data = camera.data
    camera_data.lens = camera_config["focal_length"]  # Focal length in mm
    camera_data.clip_start = camera_config["clip_start"]
    camera_data.clip_end = camera_config["clip_end"]  # Set clip end to twice the camera height
    
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

    lighting_types = ['three_point', 'studio', 'outdoor', 'dramatic']

    # Determine lighting style for this scene
    lighting_style = random.choice(lighting_types)
    
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
    spread_factor = random.uniform(object_config["spread_factor_range"][0],
                                   object_config["spread_factor_range"][1])  

    x_center_offset = random.uniform(object_config["x_center_offset_range"][0],
                                     object_config["x_center_offset_range"][1])
    
    y_center_offset = random.uniform(object_config["y_center_offset_range"][0],
                                     object_config["y_center_offset_range"][1])
    
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
        max_attempts = general_config["max_collision_check_amount"]
        attempt = 0
        colliding = True
        
        # Randomly choose an object type
        obj_type = random.choice(object_classes)
        
        x, y, z = 0, 0, 0
        
        # Keep trying until we find a non-colliding position
        while colliding and attempt < max_attempts:
            # Randomly position within visible area with the custom distribution
            x = random.uniform(object_config["random_x_range"][0],
                               object_config["random_x_range"][1]) * spread_factor + x_center_offset
            y = random.uniform(object_config["random_y_range"][0],
                               object_config["random_y_range"][1]) * spread_factor + y_center_offset
            z = random.uniform(object_config["random_z_range"][0],
                               object_config["random_z_range"][1])  # Height above ground
            
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
            random.uniform(object_config["random_rotation_range"][0],
                           object_config["random_rotation_range"][0]),      # x rotation
            random.uniform(object_config["random_rotation_range"][0],
                           object_config["random_rotation_range"][0]),      # y rotation
            random.uniform(object_config["random_rotation_range"][0],
                           object_config["random_rotation_range"][0]),      # z rotation
        )
        
        # Create a random colored material
        mat = bpy.data.materials.new(name=f"Material_{i}")
        mat.use_nodes = True
        principled_bsdf = mat.node_tree.nodes.get('Principled BSDF')
        if principled_bsdf:
            principled_bsdf.inputs[0].default_value = (
                random.uniform(0.1, 1),     # Red
                random.uniform(0.1, 1),     # Green
                random.uniform(0.1, 1),     # Blue
                1                           # Alpha
            )
        
        # Assign material to object
        if obj.data.materials:
            obj.data.materials[0] = mat
        else:
            obj.data.materials.append(mat)
        
        objects.append(obj)
    
    # Create a plane for the ground
    bpy.ops.mesh.primitive_plane_add(size=scene_config["ground_plane_size"],
                                     location=(0, 0, 0))
    ground = bpy.context.active_object
    
    # Add a material to the ground
    mat = bpy.data.materials.new(name="Ground_Material")
    mat.use_nodes = True
    principled_bsdf = mat.node_tree.nodes.get('Principled BSDF')
    if principled_bsdf:
        principled_bsdf.inputs[0].default_value = (
            object_config["default_config"][0],
            object_config["default_config"][1],
            object_config["default_config"][2],
            object_config["default_config"][3])
    
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
    colors = class_config["class_colours"]
    
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
            cv2.putText(img, class_config["classes"][class_idx], (x1, y1 - 10), 
                        cv2.FONT_HERSHEY_SIMPLEX, 0.9, color, 2)
    
    # Save annotated image
    cv2.imwrite(output_path, img)

#------------------------------------------------------------------------------
# IMAGE GENERATION
#------------------------------------------------------------------------------
def find_textures(path: str) -> list[str]:
    """Find all texture files in the given directory and its subdirectories.
    
    Args:
        path: Root directory to search for textures
        
    Returns:
        List of paths to texture files
    """
    texture_files = []
    texture_extensions = ['.blend']  # Focus on .blend files for now
    
    # Walk through the directory and its subdirectories
    for root, dirs, files in os.walk(path):
        for file in files:
            # Check if file has a texture extension
            if any(file.lower().endswith(ext) for ext in texture_extensions):
                # Get the full path to the texture file
                texture_path = os.path.join(root, file)
                # Convert to absolute path
                texture_path = os.path.abspath(texture_path)
                texture_files.append(texture_path)
    
    return texture_files


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
            
            denominator = random.randint(object_config["denominator_range"][0],
                                         object_config["denominator_range"][1])
            
            # Calculate scale to make largest dimension 5 units
            scale_factor = object_config["max_scale"] / denominator
            
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

            
        except Exception as e:
            print(f"Warning: Error during object adjustment: {str(e)}")
            print("Continuing with unadjusted object...")
        
        return obj_name  # Return the name instead of the object reference
        
    except Exception as e:
        print(f"Error during model import: {str(e)}")
        raise

def create_textured_plane(texture_path=None):
    """Create a 3x3 grid of planes with optional texture.
    
    Args:
        texture_path: Path to the texture file (.blend)
    """
    planes = []
    plane_size = scene_config["ground_plane_size"]  # Size of each individual plane
    spacing = plane_size  # Planes will touch perfectly
    
    # Create a plane grid
    for i in range(3):
        for j in range(3):
            # Calculate position for this plane
            x = (i - 1) * spacing  # -1, 0, 1
            y = (j - 1) * spacing  # -1, 0, 1
            
            # Create the plane
            bpy.ops.mesh.primitive_plane_add(size=plane_size, location=(x, y, 0))
            plane = bpy.context.active_object
            
            # Set plane name for easy identification
            plane.name = f"Background_Plane_{i}_{j}"
            
            # Create material
            mat = bpy.data.materials.new(name=f"Ground_Material_{i}_{j}")
            mat.use_nodes = True
            nodes = mat.node_tree.nodes
            links = mat.node_tree.links
            
            # Clear existing nodes
            nodes.clear()
            
            # Create nodes for texture setup
            material_output = nodes.new('ShaderNodeOutputMaterial')
            principled_bsdf = nodes.new('ShaderNodeBsdfPrincipled')
            
            # Link Principled BSDF to Material Output
            links.new(principled_bsdf.outputs['BSDF'], material_output.inputs['Surface'])
            
            if texture_path and os.path.exists(texture_path):
                try:
                    # Append the material from the .blend file
                    with bpy.data.libraries.load(texture_path) as (data_from, data_to):
                        # Find material names in the .blend file
                        material_names = [name for name in data_from.materials]
                        if material_names:
                            # Load the first material found
                            data_to.materials = [material_names[0]]
                    
                    if data_to.materials and data_to.materials[0] is not None:
                        # Use the loaded material instead of creating a new one
                        imported_mat = data_to.materials[0]
                        
                        # Assign the imported material to the plane
                        if plane.data.materials:
                            plane.data.materials[0] = imported_mat
                        else:
                            plane.data.materials.append(imported_mat)
                        
                        print(f"Successfully applied material from: {texture_path}")
                        planes.append(plane)
                        continue
                    
                    raise Exception("No valid materials found in the .blend file")
                    
                except Exception as e:
                    print(f"Error applying material from .blend file: {str(e)}")
                    # Fallback to default material if texture fails
                    principled_bsdf.inputs[0].default_value = object_config["default_colour"]
            else:
                # Fallback to default again
                principled_bsdf.inputs[0].default_value = object_config["default_colour"]
            
            # Assign material to plane (only if we didn't successfully import a material)
            if plane.data.materials:
                plane.data.materials[0] = mat
            else:
                plane.data.materials.append(mat)
            
            planes.append(plane)
    
    return planes

def is_colliding(position, existing_objects, min_distance=3.0):
    """Check if a position would collide with existing objects.
    
    Args:
        position: Tuple of (x, y, z) coordinates
        existing_objects: List of existing objects
        min_distance: Minimum distance required between objects
        
    Returns:
        True if collision would occur, False otherwise
    """
    for obj in existing_objects:
        # Calculate distance between centers
        distance = math.sqrt(
            (position[0] - obj.location.x)**2 + 
            (position[1] - obj.location.y)**2
        )
        if distance < min_distance:
            return True
    return False

def find_valid_position(existing_objects, 
                        max_attempts=general_config["max_collision_check_amount"]):
    """Find a valid position that doesn't collide with existing objects.
    
    Args:
        existing_objects: List of existing objects
        max_attempts: Maximum number of attempts to find a valid position
        
    Returns:
        Tuple of (x, y, z) coordinates if valid position found, None otherwise
    """
    for _ in range(max_attempts):
        # Try a random position
        x = random.uniform(-30, 30)
        y = random.uniform(-20, 20)
        z = 0
        
        if not is_colliding((x, y, z), existing_objects):
            return (x, y, z)
    
    return None

def generate_single_image(index, images_dir, labels_dir, custom_model_path=None):
    """Generate a single image with bounding boxes."""
    print(f"\nGenerating image {index+1}")
    print(f"Custom model path: {custom_model_path}")
    
    # Convert relative paths to absolute paths
    images_dir_abs = os.path.abspath(images_dir)
    labels_dir_abs = os.path.abspath(labels_dir)
    visualization_dir_abs = os.path.abspath(images_dir_abs + "/" + general_config["visualisation_dir"])
    
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
    visualization_path = os.path.join(visualization_dir_abs, f"vis_{index:03d}.png")
    
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
        
        # Get list of available textures
        texture_files = find_textures("./textures")
        print(f"INFO: Found {len(texture_files)} texture files")
        
        # Randomly select a texture if available
        texture_path = None
        if texture_files:
            texture_path = random.choice(texture_files)
            print(f"Using texture: {texture_path}")
        
        # Create textured plane
        create_textured_plane(texture_path)
        
        # Import or create objects
        if custom_model_path:
            print("Using custom model path...")
            try:
                # Get file extension
                file_ext = os.path.splitext(custom_model_path)[1].lower()
                print(f"File extension: {file_ext}")
                
                # Determine number of models to create (1-10)
                num_models = random.randint(1, 10)
                print(f"Creating {num_models} instances of the model")
                
                # Create a list to store all imported objects
                imported_objects = []
                
                for i in range(num_models):
                    # Import custom model
                    if file_ext == '.obj':
                        print(f"Importing OBJ file {i+1}...")
                        if hasattr(bpy.ops.wm, 'obj_import'):
                            bpy.ops.wm.obj_import(filepath=custom_model_path)
                        else:
                            bpy.ops.import_scene.obj(filepath=custom_model_path)
                    elif file_ext == '.fbx':
                        print(f"Importing FBX file {i+1}...")
                        if hasattr(bpy.ops.wm, 'fbx_import'):
                            bpy.ops.wm.fbx_import(filepath=custom_model_path)
                        else:
                            bpy.ops.import_scene.fbx(filepath=custom_model_path)
                    elif file_ext == '.blend':
                        print(f"Importing Blend file {i+1}...")
                        bpy.ops.wm.append(filepath=custom_model_path)
                    else:
                        raise ValueError(f"Unsupported file format: {file_ext}")
                    
                    # Find the newly imported mesh object
                    mesh_objects = [obj for obj in bpy.data.objects if obj.type == 'MESH' and obj not in imported_objects]
                    if not mesh_objects:
                        raise ValueError(f"No mesh objects found after import {i+1}")
                    
                    # Set up the mesh object
                    obj = mesh_objects[0]
                    obj['class_idx'] = 0
                    
                    # Scale the object with randomization
                    dims = obj.dimensions
                    max_dim = max(dims)
                    if max_dim > 0:
                        # Base scale factor
                        base_scale = object_config["max_scale"] / max_dim
                        
                        # Random scale variation between 1 and 1.5
                        scale_variation = random.uniform(object_config["scale_variation_range"][0],
                                                         object_config["scale_variation_range"][1])
                        
                        # Apply random scale
                        scale_factor = base_scale * scale_variation
                        obj.scale = (scale_factor, scale_factor, scale_factor)
                        
                        # Reset all rotations first
                        obj.rotation_euler = (0, 0, 0)
                        
                        # Find a valid position that doesn't collide with existing objects
                        position = find_valid_position(imported_objects)
                        if position is None:
                            print(f"Warning: Could not find valid position for object {i+1}, skipping...")
                            bpy.data.objects.remove(obj)
                            continue
                        
                        # Set the position
                        obj.location = position
                        
                        # Random rotation around Z axis only
                        obj.rotation_euler = (
                            0,
                            0,
                            random.uniform(0, 360)  # z rotation
                        )
                        
                        # Update the scene to apply transformations
                        bpy.context.view_layer.update()
                        
                        print(f"Adjusted object {i+1} scale to {scale_factor} (variation: {scale_variation})")
                        print(f"Set position: {obj.location}")
                        print(f"Set random rotation: {obj.rotation_euler}")
                    else:
                        print(f"Warning: Object {i+1} has zero dimensions")
                    
                    imported_objects.append(obj)
                
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