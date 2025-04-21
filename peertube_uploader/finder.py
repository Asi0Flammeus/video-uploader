"""
Utilities for finding .mp4 files in directories.
"""
import os

def find_mp4_files(directory):
    """
    Recursively find all .mp4 files in the given directory.
    Yields full file paths.
    """
    for root, dirs, files in os.walk(directory):
        for name in files:
            if name.lower().endswith(".mp4"):
                yield os.path.join(root, name)