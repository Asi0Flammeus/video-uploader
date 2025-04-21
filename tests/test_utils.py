import os

from peertube_uploader.utils import generate_title, generate_description

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