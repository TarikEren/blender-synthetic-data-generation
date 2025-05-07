import os
import sys
import json
import subprocess

from utils.logger_utils import logger
from schemas.config_schema import config_schema

def check_and_install_package(package_name):
    """Check if a package is installed, install it if missing."""
    try:
        __import__(package_name)
    except ImportError:
        logger.info(f"Installing required package: {package_name}")
        subprocess.check_call([sys.executable, "-m", "pip", "install", package_name])
        logger.info(f"Successfully installed {package_name}")

# Check for required packages
check_and_install_package('jsonschema')
import jsonschema

def load_config(config_path: str = "./config.json") -> dict:
    """
    Load a JSON configuration file and return the contents as a dictionary.
    Args:
        config_path (str): The path to the JSON configuration file. ("./config.json" by default)
    Returns:
        config (dict): The contents of the JSON configuration file as a dictionary.
    """
    if not os.path.exists(config_path):
        logger.error(f"The configuration file at {config_path} does not exist.")
        raise FileNotFoundError(f"The configuration file at {config_path} does not exist.")
    
    # Validate the configuration
    try:
        with open(config_path, 'r') as file:
            config = json.load(file)

        jsonschema.validate(instance=config, schema=config_schema)
        logger.info("JSON configuration is valid and all required keys exist.")
    except jsonschema.ValidationError as e:
        # jsonschema provides detailed error messages
        logger.error(f"JSON configuration validation failed: {e.message}")
        raise jsonschema.ValidationError(f"JSON configuration validation failed: {e.message}")
    except Exception as e:
        # Catch other potential errors during validation
        logger.error(f"An unexpected error occurred during validation: {e}")
        raise Exception(f"An unexpected error occurred during validation: {e}")
    finally:
        logger.info(f"Configuration file loading has ended.")

    return config
