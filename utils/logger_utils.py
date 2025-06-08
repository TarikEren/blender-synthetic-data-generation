# Standard Library Imports
import sys
import logging

# Create a default logger instance
logger = logging.getLogger(__name__)

def create_logger():
    """
    Create a logger for the program.
    Returns:
        logger: The logger for the program.
    """
    # Configure logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s',
        handlers=[logging.FileHandler('blender_generator.log'), logging.StreamHandler(sys.stdout)]
    )

    # Return the logger
    return logger

def add_run_separator():
    """
    Add a visual separator to the log file to distinguish between different program runs.
    Returns:
        separator: The separator for the log file. In the format of "======== New Execution ========"
    """
    # Create the separator
    separator = "=" * 40
    run_header = " New Execution "

    # Return the separator
    return separator + run_header + separator