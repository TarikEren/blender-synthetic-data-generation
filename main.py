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
from blender_utils import (generate_single_image,
                           add_run_separator,
                           create_logger,
                           logger,
                           check_directories,
                           find_models,
                           find_textures)

# Configuration
from config import config

# Initialize logger
logger = create_logger()

# Add initial separator for this run
logger.info(add_run_separator())

def main(num_images: int):
    """
    Main function to run the entire pipeline.

    Args:
        num_images (int): The number of images to generate.
    """
    try:
        # Check if the directories exist
        check_directories()

        all_models = find_models()
        all_textures = find_textures()
        logger.info(f"Textures found: {all_textures}")
        logger.info(f"Models found: {all_models}")

        # If they do, set the paths
        images_dir = os.path.join(config["paths"]["images"])
        labels_dir = os.path.join(config["paths"]["labels"])

        
        # Generate the specified number of images
        for i in range(num_images):
            try:
                generate_single_image(index=i,
                                       textures=all_textures,
                                       models=all_models)
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
    parser.add_argument('--num-images', type=int, default=1, 
                        help='Number of images to generate (default: 1)')

    try:
        # Parse arguments if provided, otherwise use defaults
        args = parser.parse_args(argv)
        logger.info(f"Parsed arguments: {args}")
        
        # Run main with better error handling
        try:
            main(args.num_images)
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