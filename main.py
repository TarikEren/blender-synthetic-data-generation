"""
Blender Bounding Box Generator - Main Driver

This script generates 3D objects in Blender, renders them from a top-down camera view,
calculates their 2D bounding boxes, and exports them in YOLO format.
"""

import os
import argparse
import bpy
import sys

# Add the current directory to Python's module search path
sys.path.append(os.path.dirname(os.path.realpath(__file__)))

# Import the generate_single_image function from utils
from utils import generate_single_image

def main(num_images=1, output_dir=None):
    """Main function to run the entire pipeline.
    
    Args:
        num_images: Number of images to generate (default: 10)
        output_dir: Base directory for output (default: script directory)
    """
    # Setup directories
    if output_dir is None:
        base_dir = os.path.dirname(bpy.data.filepath) or os.getcwd()
    else:
        base_dir = output_dir
        
    images_dir = os.path.join(base_dir, "images")
    labels_dir = os.path.join(base_dir, "labels")
    
    # Create directories if they don't exist
    os.makedirs(images_dir, exist_ok=True)
    os.makedirs(labels_dir, exist_ok=True)
    
    print(f"Starting generation of {num_images} images")
    print(f"Images will be saved to: {images_dir}")
    print(f"Labels will be saved to: {labels_dir}")
    
    # Generate the specified number of images
    for i in range(num_images):
        generate_single_image(i, images_dir, labels_dir)
    
    print(f"Complete! Generated {num_images} images in {images_dir}")
    print(f"Labels saved to {labels_dir}")

if __name__ == "__main__":
    # Handle Blender's argument passing
    # When blender is called with: blender --background --python main.py -- --num-images 20
    # Only the arguments after -- will be passed to the script's argv
    argv = sys.argv
    
    if "--" in argv:
        # Get arguments after --
        argv = argv[argv.index("--") + 1:]
    else:
        # No script arguments provided
        argv = []
    
    # Add command line argument support
    parser = argparse.ArgumentParser(description='Generate Blender scenes with bounding boxes in YOLO format')
    parser.add_argument('--num-images', type=int, default=10, 
                        help='Number of images to generate (default: 10)')
    parser.add_argument('--output-dir', type=str, default=None, 
                        help='Directory to save output (default: script directory)')
    
    # Parse arguments if provided, otherwise use defaults
    try:
        args = parser.parse_args(argv)
        main(args.num_images, args.output_dir)
    except:
        # If argument parsing fails, use defaults
        main() 