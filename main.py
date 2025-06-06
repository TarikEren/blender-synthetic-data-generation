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
from blender_utils import (generate_image,
                           add_run_separator,
                           create_logger,
                           logger,
                           check_directories,
                           find_textures,
                           get_models_and_classes)

# Configuration
from config import config

# Initialize logger
logger = create_logger()

# Add initial separator for this run
logger.info(add_run_separator())

def main(num_images: int, visualise: bool):
    """
    Main function to run the entire pipeline.

    Args:
        num_images (int): The number of images to generate.
        visualise (bool): Whether to visualise the bounding boxes. Defaults to True.
    """
    try:
        # Check if the directories exist
        check_directories()

        # If they do, set the paths
        images_dir = os.path.join(config["paths"]["images"])
        labels_dir = os.path.join(config["paths"]["labels"])
        logger.info(f"{'='*40} Directories {'='*40}")
        logger.info(f"Images Directory: {images_dir}")
        logger.info(f"Labels Directory: {labels_dir}")
        
        all_models = get_models_and_classes()
        logger.info(f"{'='*40} Models {'='*40}")
        for model in all_models:
            logger.info("Model:")
            logger.info(f"\tClass Index: {model[0]}")
            logger.info(f"\tClass Name: {model[1]}")
            logger.info(f"\tModel Path: {model[2]}")

        all_textures = find_textures()
        logger.info(f"{'='*40} Textures {'='*40}")
        for texture in all_textures:
            logger.info(f"Path: {texture}")

        # Generate the specified number of images
        for i in range(num_images):
            try:
                generate_image(index=i,
                               textures=all_textures,
                               models=all_models,
                               visualise=visualise)
            except Exception as e:
                logger.error(f"Error generating image {i}: {e}")

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
    parser.add_argument('--visualise', action=argparse.BooleanOptionalAction, default=False,
                        help='Visualise the bounding boxes (default: False)')

    try:
        # Parse arguments if provided, otherwise use defaults
        args = parser.parse_args(argv)
        logger.info(f"Parsed arguments: {args}")
        
        # Run main with better error handling
        try:
            main(args.num_images, args.visualise)
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