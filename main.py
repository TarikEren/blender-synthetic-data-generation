"""
Driver for the Blender Object Generator.
Responsible for parsing the arguments, creating the logger, and running the program.
"""

import os
import sys

# Add the current directory to the Python path (For relative imports)
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Import the config
from config import config

# Import the utils
from utils import (
    create_logger,
    add_run_separator,
    create_scene,
    clear_scene,
    get_textures,
    get_models,
    install_packages
)

def main():
    """
    Main function for the Blender Object Generator.
    """
    # Install the required packages
    install_packages()

    # Configure logging
    logger = create_logger()

    # Add initial separator for this run
    logger.info(add_run_separator())

    # Create the scene
    scene = create_scene(config)

    # Clear the scene
    clear_scene()

    # Get the textures
    textures = get_textures(config)

    # Get the models
    models = get_models(config)


# Run the main function
if __name__ == "__main__":
    main()
