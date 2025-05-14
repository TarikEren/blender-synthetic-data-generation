"""
Package utils for the Blender Object Generator.
"""

import sys
import subprocess

from utils.logger_utils import logger

def check_and_install_package(package_name):
    """Check if a package is installed, install it if missing."""
    try:
        __import__(package_name)
        logger.info(f"Package {package_name} is already installed.")
    except ImportError:
        logger.info(f"Installing required package: {package_name}")
        subprocess.check_call([sys.executable, "-m", "pip", "install", package_name])
        logger.info(f"Successfully installed {package_name}")

def install_packages():
    """Install all required packages."""
    check_and_install_package('jsonschema')

