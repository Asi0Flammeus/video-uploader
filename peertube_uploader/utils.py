"""
Utility functions for generating video metadata.
"""
import os

def generate_title(file_path):
    """
    Generate a title for the video based on the file path.
    Currently uses the file name without extension.
    """
    return os.path.splitext(os.path.basename(file_path))[0]

def generate_description(file_path):
    """
    Generate a description for the video based on the file path.
    Currently returns an empty string. Extend with custom logic as needed.
    """
    return ""