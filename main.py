"""
Driver for the Blender Object Generator.
Responsible for parsing the arguments, creating the logger, and running the program.
"""

import os
import sys

# Add the current directory to the Python path (For relative imports)
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Import the utils
from utils import create_logger, add_run_separator, load_config, create_scene, clear_scene

def main():
    """
    Main function for the Blender Object Generator.
    """
    # Configure logging
    logger = create_logger()

    # Add initial separator for this run
    logger.info(add_run_separator())

    # Load the configuration
    config = load_config()

    # Create the scene
    scene = create_scene(config, logger)

    # Clear the scene
    clear_scene(logger)


# Run the main function
if __name__ == "__main__":
    main()
