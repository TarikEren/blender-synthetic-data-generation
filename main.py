"""
Blender Bounding Box Generator - Main Driver

This script generates 3D objects in Blender, renders them from a top-down camera view,
calculates their 2D bounding boxes, and exports them in YOLO format.
"""

# Standard Library Imports
import os
import sys
import argparse

# Add the script's directory to Python's path
script_dir = os.path.dirname(os.path.abspath(__file__))
if script_dir not in sys.path:
    sys.path.append(script_dir)

# Third Party Imports
import bpy

# Local Imports
from blender_utils import generate_single_image, add_run_separator, create_logger, logger

# Initialize logger
logger = create_logger()

# Configuration
from config import config

# Add initial separator for this run
logger.info(add_run_separator())

def main(num_images=1, custom_model_path=None):
    """Main function to run the entire pipeline."""
    try:
        # Debug logging for custom model path
        logger.info("Debug Information:")
        logger.info(f"Custom Model Path: {custom_model_path}")
        logger.info(f"Custom Model Path Type: {type(custom_model_path)}")
        if custom_model_path:
            logger.info(f"Custom Model Path exists: {os.path.exists(custom_model_path)}")
        logger.info("------------------------")
        
        images_dir = os.path.join(config["paths"]["images"])
        labels_dir = os.path.join(config["paths"]["labels"])
        
        # Create directories if they don't exist
        os.makedirs(images_dir, exist_ok=True)
        os.makedirs(labels_dir, exist_ok=True)
        
        logger.info(f"Starting generation of {num_images} images")
        if custom_model_path:
            logger.info(f"Using custom model: {custom_model_path}")
        logger.info(f"Images will be saved to: {images_dir}")
        logger.info(f"Labels will be saved to: {labels_dir}")
        
        # Generate the specified number of images
        print(f"GENERATION STARTED: Generating {num_images} images")
        for i in range(num_images):
            try:
                generate_single_image(i, custom_model_path)
            except Exception as e:
                logger.error(f"Error generating image {i}: {str(e)}")
                # Try to clean up any dangling references
                for obj in bpy.data.objects:
                    try:
                        bpy.data.objects.remove(obj, do_unlink=True)
                    except:
                        pass
                continue
        
        logger.info(f"Generation completed. Generated {num_images} images in {images_dir}")
        logger.info(f"Labels saved to {labels_dir}")
        
    except Exception as e:
        logger.error(f"Error in main: {str(e)}")
        raise

if __name__ == "__main__":
    # Handle Blender's argument passing
    argv = sys.argv
    
    if "--" in argv:
        # Get arguments after --
        argv = argv[argv.index("--") + 1:]
        logger.info(f"Command line arguments received: {argv}")
    else:
        # No script arguments provided
        argv = []
    
    # Add command line argument support
    parser = argparse.ArgumentParser(description='Generate Blender scenes with bounding boxes in YOLO format')
    parser.add_argument('--num-images', type=int, default=10, 
                        help='Number of images to generate (default: 10)')
    parser.add_argument('--custom-model', type=str, default=None,
                        help='Path to custom 3D model to import (supports .obj, .fbx, .blend)')
    
    try:
        # Parse arguments if provided, otherwise use defaults
        args = parser.parse_args(argv)
        logger.info(f"Parsed arguments: {args}")
        
        # Run main with better error handling
        try:
            main(args.num_images, args.custom_model)
        except Exception as e:
            logger.error(f"Error running main: {str(e)}")
            sys.exit(1)
            
    except Exception as e:
        logger.error(f"Error parsing arguments: {e}")

        # If argument parsing fails, try with defaults
        try:
            main()
        except Exception as e:
            logger.error(f"Error running main with defaults: {str(e)}")
            sys.exit(1) 