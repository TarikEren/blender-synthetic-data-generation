import logging
from pathlib import Path
from typing import Dict

import bpy

def create_scene(config: Dict, logger: logging.Logger) -> bpy.types.Scene:
    """
    Create and configure a Blender scene based on the provided config.

    Args:
        config (Dict): Validated config dict with keys:
            - scene.name (str)
            - scene.resolution.{x,y,percentage}
            - scene.camera.{position,rotation}.{x,y,z}
            - scene.light.{position,rotation}.{x,y,z}
            - scene.engine (str)
            - scene.cycles (Dict of Cycles settings)
          paths (Dict): contains "images" directory
          output (Dict, optional): may contain "filename"
        logger (logging.Logger): for debug/info messages.

    Returns:
        bpy.types.Scene: the configured scene.
    """

    # Get the config
    scene_cfg = config["scene"]
    paths_cfg = config["paths"]
    output_cfg = config.get("output", {})

    # Ensure the Cycles add‑on is enabled so its engine is registered
    if 'cycles' not in bpy.context.preferences.addons:
        bpy.ops.preferences.addon_enable(module='cycles')

    # Grab the active scene and rename
    scene = bpy.context.scene
    scene.name = scene_cfg["name"]
    logger.info(f"Scene renamed to '{scene.name}'")

    # Set the render engine (we know it's valid via schema)
    scene.render.engine = scene_cfg.get("engine", "CYCLES")
    logger.info(f"Render engine set to {scene.render.engine}")

    # Configure GPU for Cycles
    if scene.render.engine == "CYCLES":
        prefs = bpy.context.preferences.addons['cycles'].preferences
        prefs.compute_device_type = 'CUDA'
        prefs.refresh_devices()
        cuda_devs = [d for d in prefs.devices if d.type == 'CUDA']
        if cuda_devs:
            for dev in cuda_devs:
                dev.use = True
                logger.debug(f"Enabled CUDA device: {dev.name}")
            scene.cycles.device = 'GPU'
            logger.info("Cycles device: GPU")
        else:
            scene.cycles.device = 'CPU'
            logger.info("No CUDA devices found; using CPU")

        # Apply the detailed Cycles settings from config
        cyc = scene_cfg["cycles"]
        scene.cycles.use_progressive_refine = bool(cyc["use_progressive_refine"])
        scene.cycles.tile_size              = int(cyc["tile_size"])
        scene.render.use_persistent_data    = bool(cyc["use_persistent_data"])
        scene.cycles.samples                = int(cyc["samples"])
        scene.cycles.use_adaptive_sampling  = bool(cyc["use_adaptive_sampling"])
        scene.cycles.adaptive_threshold     = float(cyc["adaptive_threshold"])
        scene.cycles.use_denoising          = bool(cyc["use_denoising"])
        scene.cycles.max_bounces            = int(cyc["max_bounces"])
        scene.cycles.diffuse_bounces        = int(cyc["diffuse_bounces"])
        scene.cycles.glossy_bounces         = int(cyc["glossy_bounces"])
        scene.cycles.sample_clamp_indirect  = float(cyc["sample_clamp_indirect"])

        # Log the Cycles settings
        logger.info(
            "Cycles settings:\n"
            f"  tile_size              = {scene.cycles.tile_size}\n"
            f"  use_persistent_data    = {scene.render.use_persistent_data}\n"
            f"  samples                = {scene.cycles.samples}\n"
            f"  use_adaptive_sampling  = {scene.cycles.use_adaptive_sampling}\n"
            f"  adaptive_threshold     = {scene.cycles.adaptive_threshold}\n"
            f"  use_denoising          = {scene.cycles.use_denoising}\n"
            f"  max_bounces            = {scene.cycles.max_bounces}\n"
            f"  diffuse_bounces        = {scene.cycles.diffuse_bounces}\n"
            f"  glossy_bounces         = {scene.cycles.glossy_bounces}\n"
            f"  sample_clamp_indirect  = {scene.cycles.sample_clamp_indirect}"
        )

    # Set the resolution
    res = scene_cfg["resolution"]
    scene.render.resolution_x         = int(res["x"])
    scene.render.resolution_y         = int(res["y"])
    scene.render.resolution_percentage= int(res["percentage"])
    logger.info(f"Resolution: {res['x']}x{res['y']} @ {res['percentage']}%")

    # Set the output path
    out_dir = Path(paths_cfg["images"])

    if not out_dir.exists():
        out_dir.mkdir(parents=True, exist_ok=True)

    # Set the output filename
    filename = output_cfg.get("filename", "render.png")

    # Set the output filepath
    scene.render.filepath = str(out_dir / filename)

    # Log the output filepath
    logger.info(f"Output filepath: {scene.render.filepath}")

    # Add and position camera
    cam_data = bpy.data.cameras.new(f"{scene.name}_Camera")
    cam_obj  = bpy.data.objects.new(f"{scene.name}_Camera", cam_data)

    # Link the camera object to the collection
    bpy.context.collection.objects.link(cam_obj)

    # Set the camera position and rotation
    cp = scene_cfg["camera"]["position"]
    cr = scene_cfg["camera"]["rotation"]
    cam_obj.location       = (cp["x"], cp["y"], cp["z"])
    cam_obj.rotation_euler = (cr["x"], cr["y"], cr["z"])

    # Set the active camera
    scene.camera = cam_obj

    # Log the camera position and rotation
    logger.info(f"Camera at {cam_obj.location}, rot {cam_obj.rotation_euler}")

    # Add and position a point light
    light_data = bpy.data.lights.new(name=f"{scene.name}_Light", type='POINT')
    light_obj  = bpy.data.objects.new(f"{scene.name}_Light", light_data)

    # Link the light object to the collection
    bpy.context.collection.objects.link(light_obj)

    # Set the light position and rotation
    lp = scene_cfg["light"]["position"]
    lr = scene_cfg["light"]["rotation"]
    light_obj.location       = (lp["x"], lp["y"], lp["z"])
    light_obj.rotation_euler = (lr["x"], lr["y"], lr["z"])
    logger.info(f"Light at {light_obj.location}, rot {light_obj.rotation_euler}")

    return scene


def clear_scene(logger: logging.Logger):
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
    
    logger.info("Scene cleared")
