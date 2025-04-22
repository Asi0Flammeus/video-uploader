"""
Utility functions for generating video metadata.
"""
import os
import re
from typing import Tuple

def generate_title(file_path: str) -> str:
    """
    Generate a title for the video based on the file path.
    Currently uses the file name without extension.
    """
    return os.path.splitext(os.path.basename(file_path))[0]

def generate_description(file_path: str) -> str:
    """
    Generate a description for the video based on the file path.
    Currently returns an empty string. Extend with custom logic as needed.
    """
    return "test"


def extract_course_index(filename: str) -> str:
    """
    Extract the course index (3 letters and 3 digits) from the filename.
    Example: "btc101_2.1_es.txt" -> "btc101"
    """
    base = os.path.basename(filename)
    match = re.search(r'([A-Za-z]{3}\d{3})', base)
    if match:
        return match.group(1).lower()
    raise ValueError(f"Course index not found in filename: {filename}")


def extract_part_chapter(filename: str) -> Tuple[int, int]:
    """
    Extract the part and chapter numbers from the filename as a tuple (part, chapter).
    Filename contains a float pattern like "2.1" representing part.chapter.
    Example: "btc101_2.1_es.txt" -> (2, 1)
    """
    base = os.path.basename(filename)
    match = re.search(r'(\d+)\.(\d+)', base)
    if match:
        return int(match.group(1)), int(match.group(2))
    raise ValueError(f"Part and chapter not found in filename: {filename}")


def extract_language(filename: str) -> str:
    """
    Extract the language code from the filename.
    Supports codes at the end of the base name, with optional region suffix:
      Examples: 'video_es.mp4' -> 'es', 'video-en-US.mp4' -> 'en', 'video_en_US.mp4' -> 'en'.
    """
    base = os.path.basename(filename)
    name, _ = os.path.splitext(base)
    # Split on underscore to preserve hyphens for region codes
    parts = name.split('_')
    # Iterate backwards to find the first valid language code
    for part in reversed(parts):
        # Region-coded with hyphen, e.g., en-US
        if re.fullmatch(r'[A-Za-z]{2,3}-[A-Za-z]{2}', part):
            return part.split('-', 1)[0].lower()
        # Generic hyphen suffix, e.g., 2.1-es, cyp201-4.7-fr
        if '-' in part:
            suffix = part.rsplit('-', 1)[1]
            if re.fullmatch(r'[A-Za-z]{2}', suffix):
                return suffix.lower()
            # continue if suffix not valid
        # Simple two-letter code, e.g., es, fr
        if re.fullmatch(r'[A-Za-z]{2}', part):
            return part.lower()
    # No valid language code found
    raise ValueError(f"Language code not found in filename: {filename}")
