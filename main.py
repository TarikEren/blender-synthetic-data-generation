"""
Blender Bounding Box Generator - Main Driver

This script generates 3D objects in Blender, renders them from a top-down camera view,
calculates their 2D bounding boxes, and exports them in YOLO format.
"""

import os
import sys
import argparse
import logging
import bpy

# Adding the current directory to Python's module search path
current_dir = os.path.dirname(os.path.abspath(__file__))
if current_dir not in sys.path:
    sys.path.append(current_dir)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('blender_generator.log'),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)

from utils import add_run_separator

# Add initial separator for this run
logger.info(add_run_separator())


from config import general_config
from utils import generate_single_image

def main(num_images=1, output_dir=None, custom_model_path=None):
    """Main function to run the entire pipeline."""
    try:
        # Debug logging for custom model path
        logger.info("Debug Information:")
        logger.info(f"Custom Model Path: {custom_model_path}")
        logger.info(f"Custom Model Path Type: {type(custom_model_path)}")
        if custom_model_path:
            logger.info(f"Custom Model Path exists: {os.path.exists(custom_model_path)}")
        logger.info("------------------------")
        
        # Setup directories
        if output_dir is None:
            base_dir = os.getcwd()
        else:
            base_dir = output_dir
            
        images_dir = os.path.join(base_dir, general_config["images_dir"])
        labels_dir = os.path.join(base_dir, general_config["labels_dir"])
        
        # Create directories if they don't exist
        os.makedirs(images_dir, exist_ok=True)
        os.makedirs(labels_dir, exist_ok=True)
        
        logger.info(f"Starting generation of {num_images} images")
        if custom_model_path:
            logger.info(f"Using custom model: {custom_model_path}")
        logger.info(f"Images will be saved to: {images_dir}")
        logger.info(f"Labels will be saved to: {labels_dir}")
        
        # Generate the specified number of images
        for i in range(num_images):
            try:
                generate_single_image(i, images_dir, labels_dir, custom_model_path)
            except Exception as e:
                logger.error(f"Error generating image {i}: {str(e)}")
                # Try to clean up any dangling references
                for obj in bpy.data.objects:
                    try:
                        bpy.data.objects.remove(obj, do_unlink=True)
                    except:
                        pass
                continue
        
        logger.info(f"Complete! Generated {num_images} images in {images_dir}")
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
    parser.add_argument('--output-dir', type=str, default=None, 
                        help='Directory to save output (default: script directory)')
    parser.add_argument('--custom-model', type=str, default=None,
                        help='Path to custom 3D model to import (supports .obj, .fbx, .blend)')
    
    try:
        # Parse arguments if provided, otherwise use defaults
        args = parser.parse_args(argv)
        logger.info(f"Parsed arguments: {args}")
        
        # Run main with better error handling
        try:
            main(args.num_images, args.output_dir, args.custom_model)
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