"""
Blender Bounding Box Generator - Main Driver

This script generates 3D objects in Blender, renders them from a top-down camera view,
calculates their 2D bounding boxes, and exports them in YOLO format.
"""

# Standard Library Imports
import re
import os
import sys
import argparse
from pathlib import Path
from contextlib import contextmanager

# Add the script's directory to Python's path
script_dir = os.path.dirname(os.path.abspath(__file__))
if script_dir not in sys.path:
    sys.path.append(script_dir)

# Third Party Imports
import bpy

# Local Imports
from utils.logger_utils import create_logger, logger, add_run_separator
from utils.asset_utils import get_models_and_classes, find_textures, check_directories
from utils.dataset_utils import split_images, create_dataset_paths, copy_dataset_contents, create_yolo_yaml
from utils.image_utils import generate_image

from config import config

from utils.exceptions import (
    BlenderGeneratorError,
    ConfigError,
    AssetError,
    SceneError,
    RenderingError,
    DatasetError,
    ValidationError,
    ResourceError
)

# Initialize logger
logger = create_logger()

# Add initial separator for this run
logger.info(add_run_separator())

def get_unique_classes(models: list) -> list[str]:
    """
    Extract unique class names from the models list.
    
    Args:
        models (list): List of model tuples (class_index, class_name, model_path)
        
    Returns:
        list[str]: List of unique class names
    """
    return sorted(list(set(model[1] for model in models)))

def parse_starting_index(starting_filename: str) -> int:
    """
    Parse the starting index from a filename.
    
    Args:
        starting_filename (str): The filename to parse (e.g., 'image_000000')
        
    Returns:
        int: The parsed index number
    """
    match = re.search(r'image_(\d+)', starting_filename)
    if match:
        return int(match.group(1))
    raise ValueError(f"Invalid filename format: {starting_filename}. Expected format: image_XXXXXX")

@contextmanager
def blender_context():
    """Context manager for Blender operations with cleanup."""
    try:
        yield
    finally:
        # Cleanup Blender objects
        for obj in bpy.data.objects:
            try:
                bpy.data.objects.remove(obj, do_unlink=True)
            except Exception as e:
                logger.warning(f"Failed to remove object {obj.name}: {e}")

def validate_config():
    """Validate the configuration settings."""
    try:
        # Check if all required paths exist
        for path_name, path in config["paths"].items():
            if not os.path.exists(path):
                raise ConfigError(f"Required path does not exist: {path}")
        
        # Validate dataset ratios
        ratios = [
            config["dataset"]["train_ratio"],
            config["dataset"]["test_ratio"],
            config["dataset"]["val_ratio"]
        ]
        if not all(0 <= ratio <= 1 for ratio in ratios):
            raise ConfigError("Dataset ratios must be between 0 and 1")
        if sum(ratios) != 1:
            raise ConfigError("Dataset ratios must sum to 1")
            
    except Exception as e:
        raise ConfigError(f"Configuration validation failed: {str(e)}")

def validate_inputs(num_images: int, starting_filename: str = None):
    """Validate input parameters."""
    if num_images < 1:
        raise ValidationError("Number of images must be greater than 0")
    
    if starting_filename:
        try:
            parse_starting_index(starting_filename)
        except ValueError as e:
            raise ValidationError(f"Invalid starting filename: {str(e)}")

def recover_from_error(error: Exception, current_index: int = None):
    """Attempt to recover from an error and continue processing."""
    if isinstance(error, SceneError):
        logger.warning("Attempting to recover from scene error...")
        # Clear the current scene
        bpy.ops.object.select_all(action='SELECT')
        bpy.ops.object.delete()
        return True
    
    elif isinstance(error, RenderingError):
        logger.warning("Attempting to recover from rendering error...")
        # Reset render settings to defaults
        bpy.context.scene.render.engine = 'CYCLES'
        return True
    
    elif isinstance(error, ResourceError):
        logger.warning("Attempting to recover from resource error...")
        # Clear unused data blocks
        for block in bpy.data.images:
            if block.users == 0:
                bpy.data.images.remove(block)
        return True
    
    return False

def main(num_images: int, visualise: bool, starting_filename: str = None, split: bool = False):
    """
    Main function to run the entire pipeline.

    Args:
        num_images (int): The number of images to generate.
        visualise (bool): Whether to visualise the bounding boxes.
        starting_filename (str): Optional starting filename (e.g., 'image_xxxxxx')
        split (bool): Whether to split the dataset into train, test and val splits.
    """
    try:
        # Validate inputs
        validate_inputs(num_images, starting_filename)
        
        # Validate configuration
        validate_config()

        # Check if the directories exist
        check_directories()

        # Set the paths
        images_dir = os.path.join(config["paths"]["images"])
        labels_dir = os.path.join(config["paths"]["labels"])
        logger.info(f"{'='*40} Directories {'='*40}")
        logger.info(f"Images Directory: {images_dir}")
        logger.info(f"Labels Directory: {labels_dir}")
        
        try:
            all_models = get_models_and_classes()
        except Exception as e:
            raise AssetError(f"Failed to load models: {str(e)}")

        unique_classes = get_unique_classes(all_models)
        logger.info(f"{'='*40} Classes {'='*40}")
        for class_name in unique_classes:
            logger.info(f"Class: {class_name}")
            
        logger.info(f"{'='*40} Models {'='*40}")
        for model in all_models:
            logger.info("Model:")
            logger.info(f"\tClass Index: {model[0]}")
            logger.info(f"\tClass Name: {model[1]}")
            logger.info(f"\tModel Path: {model[2]}")

        try:
            all_textures = find_textures()
        except Exception as e:
            raise AssetError(f"Failed to load textures: {str(e)}")

        logger.info(f"{'='*40} Textures {'='*40}")
        for texture in all_textures:
            logger.info(f"Path: {texture}")

        # Determine starting index
        start_index = 0
        if starting_filename:
            start_index = parse_starting_index(starting_filename)
            logger.info(f"Starting from index: {start_index}")

        # Generate the specified number of images
        with blender_context():
            for i in range(start_index, start_index + num_images):
                try:
                    generate_image(index=i,
                                textures=all_textures,
                                models=all_models,
                                visualise=visualise)
                except Exception as e:
                    logger.error(f"Error generating image {i}: {e}")
                    
                    # Attempt to recover from the error
                    if recover_from_error(e, i):
                        logger.info(f"Successfully recovered from error, continuing with next image")
                        continue
                    else:
                        logger.error(f"Failed to recover from error, skipping image {i}")
                        continue
        
        logger.info(f"Generation completed. Generated {num_images} images in {images_dir}")
        logger.info(f"Labels saved to {labels_dir}")

        if split:
            try:
                logger.info(f"{'='*40} Splitting Dataset {'='*40}")
                logger.info(f"Train Ratio: {config['dataset']['train_ratio']}")
                logger.info(f"Test Ratio: {config['dataset']['test_ratio']}")
                logger.info(f"Val Ratio: {config['dataset']['val_ratio']}")
                
                splits = split_images(train_ratio=config["dataset"]["train_ratio"],
                            test_ratio=config["dataset"]["test_ratio"],
                            val_ratio=config["dataset"]["val_ratio"],
                            images_path=Path(images_dir),
                            labels_path=Path(labels_dir))
                            
                create_dataset_paths()
                copy_dataset_contents(dataset_path=Path("dataset"),
                                    splits=splits,
                                    labels_path=Path(labels_dir))
                
                create_yolo_yaml(classes=unique_classes,
                                dataset_path=Path("dataset"))
                logger.info(f"Dataset split completed. Train: {len(splits['train'])}, Test: {len(splits['test'])}, Val: {len(splits['val'])}")
            except Exception as e:
                raise DatasetError(f"Failed to split dataset: {str(e)}")
        
    except BlenderGeneratorError as e:
        logger.error(f"Blender Generator Error: {str(e)}")
        raise
    except Exception as e:
        logger.error(f"Unexpected error in main: {str(e)}")
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
    parser.add_argument('--starting-filename', type=str,
                        help='Starting filename (e.g., image_XXXXXX)')
    parser.add_argument('--split', action=argparse.BooleanOptionalAction, default=False,
                        help='Split the dataset into train, test and val splits (default: False)')

    try:
        # Parse arguments if provided, otherwise use defaults
        args = parser.parse_args(argv)
        logger.info(f"Parsed arguments: {args}")
        
        # Run main with better error handling
        try:
            main(args.num_images, args.visualise, args.starting_filename, args.split)
        except BlenderGeneratorError as e:
            logger.error(f"Blender Generator Error: {str(e)}")
            sys.exit(1)
        except Exception as e:
            logger.error(f"Unexpected error: {str(e)}")
            sys.exit(1)
            
    except Exception as e:
        logger.error(f"Error parsing arguments: {e}")

        # If argument parsing fails, try with defaults
        try:
            main(num_images=1,
                 visualise=False,
                 starting_filename=None,
                 split=False)
        except Exception as e:
            logger.error(f"Error running main with defaults: {str(e)}")
            sys.exit(1) 