"""
Utility functions for generating video metadata.
"""
import os
import re

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
    return "test"


def extract_course_index(filename):
    """
    Extract the course index (3 letters and 3 digits) from the filename.
    Example: "btc101_2.1_es.txt" -> "btc101"
    """
    base = os.path.basename(filename)
    match = re.search(r'([A-Za-z]{3}\d{3})', base)
    if match:
        return match.group(1).lower()
    raise ValueError(f"Course index not found in filename: {filename}")


def extract_part_chapter(filename):
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


def extract_language(filename):
    """
    Extract the language code from the filename.
    Language is the last segment before the extension, separated by non-alphanumeric characters.
    Special case: 'en-US' maps to 'en'.
    """
    base = os.path.basename(filename)
    name, _ = os.path.splitext(base)
    segments = [seg for seg in re.split(r'[^A-Za-z0-9-]+', name) if seg]
    if not segments:
        raise ValueError(f"Language code not found in filename: {filename}")
    lang = segments[-1].lower()
    if lang == 'en-us':
        return 'en'
    return lang
