"""
Custom exceptions for the Blender Object Generator.
"""

class BlenderGeneratorError(Exception):
    """Base exception class for Blender Generator errors."""
    pass

class ConfigError(BlenderGeneratorError):
    """Raised when there is an error in the configuration."""
    pass

class AssetError(BlenderGeneratorError):
    """Raised when there is an error loading or processing assets."""
    pass

class SceneError(BlenderGeneratorError):
    """Raised when there is an error in scene setup or manipulation."""
    pass

class RenderingError(BlenderGeneratorError):
    """Raised when there is an error during rendering."""
    pass

class DatasetError(BlenderGeneratorError):
    """Raised when there is an error in dataset operations."""
    pass

class ValidationError(BlenderGeneratorError):
    """Raised when input validation fails."""
    pass

class ResourceError(BlenderGeneratorError):
    """Raised when there is an error accessing or managing resources."""
    pass 