import os
import pytest

from peertube_uploader.finder import find_mp4_files

def test_find_mp4_files(tmp_path):
    # Create nested directory structure
    subdir = tmp_path / "subdir"
    subdir.mkdir()
    # Create .mp4 files with different cases
    file1 = tmp_path / "video1.MP4"
    file1.write_bytes(b"")
    file2 = subdir / "video2.mp4"
    file2.write_bytes(b"")
    # Create a non-mp4 file
    non_video = subdir / "file.txt"
    non_video.write_text("not a video")

    results = list(find_mp4_files(str(tmp_path)))
    # Paths should match exactly (order may vary)
    assert str(file1) in results
    assert str(file2) in results
    # No non-mp4 files
    assert all(path.lower().endswith('.mp4') for path in results)
    assert len(results) == 2