import os

from .logger_utils import logger

from config import config

def find_textures() -> list[str]:
    """
    Find all texture files in the given directory and its subdirectories.
    
    Args:
        path: Root directory to search for textures
        
    Returns:
        List of paths to texture files
    """
    texture_files = []
    texture_extensions = ['.blend']  # Focus on .blend files for now
    
    # Walk through the directory and its subdirectories
    for root, dirs, files in os.walk(config["paths"]["textures"]):
        for file in files:
            # Check if file has a texture extension
            if any(file.lower().endswith(ext) for ext in texture_extensions):
                # Get the full path to the texture file
                texture_path = os.path.join(root, file)
                # Convert to absolute path
                texture_path = os.path.abspath(texture_path)
                texture_files.append(texture_path)
    
    return texture_files

def find_models() -> list[str]:
    # TODO: Implement this function
    """
    Find all model files in the given directory and its subdirectories.
    
    Returns:
        List of paths to model files
    """
    
