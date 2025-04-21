#!/usr/bin/env python3
"""
Command-line tool to upload all .mp4 files in a folder (and subfolders) to PeerTube.
"""
import argparse
import sys

from peertube_uploader.config import Config
from peertube_uploader.finder import find_mp4_files
from peertube_uploader.utils import generate_title, generate_description
from peertube_uploader.client import PeerTubeClient

def main():
    parser = argparse.ArgumentParser(
        description="Upload all .mp4 files in a folder to PeerTube."
    )
    parser.add_argument(
        "path",
        help="Path to the folder to scan for .mp4 files"
    )
    args = parser.parse_args()

    try:
        config = Config()
    except Exception as e:
        print(f"Configuration error: {e}", file=sys.stderr)
        sys.exit(1)

    client = PeerTubeClient(config)
    files = list(find_mp4_files(args.path))
    total = len(files)
    if total == 0:
        print(f"No .mp4 files found in '{args.path}'.")
        sys.exit(0)

    print(f"Found {total} .mp4 file(s) in '{args.path}'. Starting upload...")

    for idx, video_path in enumerate(files, start=1):
        title = generate_title(video_path)
        description = generate_description(video_path)
        print(f"[{idx}/{total}] Uploading '{title}'...")
        try:
            result = client.upload_video(video_path, title, description)
            url = result.get("url") or result.get("ok")
            print(f"[{idx}/{total}] Upload successful: {url}")
        except Exception as exc:
            print(f"[{idx}/{total}] Upload failed: {exc}", file=sys.stderr)

    print("Upload process completed.")

if __name__ == "__main__":
    main()