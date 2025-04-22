import os

from peertube_uploader.utils import (
    generate_title,
    generate_description,
    extract_course_index,
    extract_part_chapter,
    extract_language,
)

def test_generate_title(tmp_path):
    # Create a dummy mp4 file
    file_path = tmp_path / "My Video Title.mp4"
    file_path.write_bytes(b"")
    title = generate_title(str(file_path))
    assert title == "My Video Title"

def test_generate_description(tmp_path):
    file_path = tmp_path / "video.mp4"
    file_path.write_bytes(b"")
    description = generate_description(str(file_path))
    # Default implementation returns empty string
    assert description == ""

def test_extract_course_index():
    assert extract_course_index('btc101_2.1_es.txt') == 'btc101'
    assert extract_course_index('/path/to/ECO201-3.2-fr.MP4') == 'eco201'

def test_extract_part_chapter():
    assert extract_part_chapter('btc101_2.1_es.txt') == (2, 1)
    assert extract_part_chapter('cyp201-4.7-fr.txt') == (4, 7)

def test_extract_language():
    assert extract_language('btc101_2.1_es.txt') == 'es'
    assert extract_language('cyp201_4.7_fr.txt') == 'fr'
    assert extract_language('cyp201_1.1_Loic_en-US.mp4') == 'en'