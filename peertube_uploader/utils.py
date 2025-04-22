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
  
def get_chapter_name(
    course_index: str,
    part_chapter: Tuple[int, int],
    code_language: str,
) -> str:
    """
    Retrieve the chapter title for a given course, part, and language.

    course_index: directory name under PATH_TO_COURSES (e.g., 'btc101')
    part_chapter: tuple of (part_number, chapter_number)
    code_language: language code matching the markdown filename (e.g., 'en', 'fr')

    The markdown file is at {PATH_TO_COURSES}/{course_index}/{code_language}.md.
    A '+++' line demarcates front matter; parsing starts after this.
    Count level-1 headings (#) to identify the requested part,
    then within that part, count level-2 headings (##) to get the requested chapter.
    Returns the chapter title without leading '#' characters.
    """
    from .config import Config
    import os

    config = Config()
    md_path = os.path.join(config.course_path, course_index, f"{code_language}.md")
    if not os.path.isfile(md_path):
        raise FileNotFoundError(f"Course markdown not found: {md_path}")

    part_target, chapter_target = part_chapter

    # Skip front matter marked by '+++'
    with open(md_path, 'r', encoding='utf-8') as f:
        # Skip until first '+++'
        for line in f:
            if line.strip().startswith('+++'):
                break
        # Skip until closing '+++'
        for line in f:
            if line.strip().startswith('+++'):
                break

        # Now parse content headings
        part_count = 0
        for line in f:
            if line.startswith('# '):
                part_count += 1
                if part_count == part_target:
                    # Found target part; search for chapters within
                    chapter_count = 0
                    for inner in f:
                        if inner.startswith('# '):
                            # Next part encountered; stop searching
                            break
                        if inner.startswith('## '):
                            chapter_count += 1
                            if chapter_count == chapter_target:
                                return inner.lstrip('#').strip()
                    # Part found but chapter missing
                    break
    raise ValueError(
        f"Chapter {chapter_target} of part {part_target} not found in {md_path}"
    )
