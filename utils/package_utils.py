import sys
import importlib
import subprocess
from typing import List, Optional

from .logger_utils import logger

def read_package_requirements(file_path: str = "packages.txt") -> List[str]:
    """
    Read package requirements from a file.
    
    Args:
        file_path (str): Path to the requirements file
        
    Returns:
        List[str]: List of package names
    """
    try:
        with open(file_path, 'r') as f:
            return [line.strip() for line in f if line.strip() and not line.startswith('#')]
    except FileNotFoundError:
        logger.error(f"Requirements file not found: {file_path}")
        return []

def check_package(package_name: str) -> bool:
    """
    Check if a package is installed.
    
    Args:
        package_name (str): Name of the package to check
        
    Returns:
        bool: True if package is installed, False otherwise
    """
    try:
        importlib.import_module(package_name)
        return True
    except ImportError:
        return False

def install_package(package_name: str) -> bool:
    """
    Install a package using pip.
    
    Args:
        package_name (str): Name of the package to install
        
    Returns:
        bool: True if installation was successful, False otherwise
    """
    try:
        # Use sys.executable which points to the current Python interpreter
        # In Blender, this will be Blender's Python
        subprocess.check_call([sys.executable, "-m", "pip", "install", package_name])
        logger.info(f"Successfully installed {package_name}")
        return True
    except subprocess.CalledProcessError as e:
        logger.error(f"Failed to install {package_name}: {str(e)}")
        return False
    except Exception as e:
        logger.error(f"Unexpected error installing {package_name}: {str(e)}")
        return False

def ensure_packages(auto_install: bool = True, requirements_file: str = "packages.txt") -> Optional[str]:
    """
    Check if required packages are installed and optionally install missing ones.
    
    Args:
        auto_install (bool): Whether to automatically install missing packages
        requirements_file (str): Path to the requirements file
        
    Returns:
        Optional[str]: Error message if any package couldn't be installed, None if all packages are available
    """
    requirements = read_package_requirements(requirements_file)
    if not requirements:
        return "No package requirements found or error reading requirements file"
    
    missing_packages = []
    
    for package in requirements:
        if not check_package(package):
            missing_packages.append(package)
    
    if not missing_packages:
        return None
        
    if not auto_install:
        return f"Missing required packages: {', '.join(missing_packages)}"
    
    for package in missing_packages:
        if not install_package(package):
            return f"Failed to install package: {package}"
    
    return None 