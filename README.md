# PeerTube Video Uploader

A command-line tool to batch upload MP4 videos to PeerTube instances with automatic metadata extraction from filenames.

## Features

- Batch upload all MP4 files from a directory (including subdirectories)
- Automatic title and description generation from filenames
- Course metadata extraction (course index, part/chapter numbers, language)
- Chapter title extraction from markdown course files
- SSL verification control
- Progress tracking during uploads

## Installation

1. Clone the repository:

```bash
git clone git@github.com:Asi0Flammeus/video-uploader.git
cd video-uploader
```

2. Install dependencies:

```bash
pip install -r requirements.txt
```

3. Install the package:

```bash
pip install -e .
```

## Configuration

Create a `.env` file in your working directory with the following variables:

```env
# Required PeerTube configuration
UPLOAD_URL=https://your-peertube-instance.com/api/v1/videos/upload
PEERTUBE_INSTANCE=https://your-peertube-instance.com
CLIENT_ID=your-client-id
CLIENT_SECRET=your-client-secret
USERNAME=your-username
PASSWORD=your-password

# Optional configuration
VERIFY_SSL=true
PATH_TO_COURSES=/path/to/course/markdown/files
```

### Required Environment Variables

- `UPLOAD_URL`: PeerTube API upload endpoint
- `PEERTUBE_INSTANCE`: Base URL of your PeerTube instance
- `CLIENT_ID`: OAuth client ID
- `CLIENT_SECRET`: OAuth client secret
- `USERNAME`: Your PeerTube username
- `PASSWORD`: Your PeerTube password

### Optional Environment Variables

- `VERIFY_SSL`: Enable/disable SSL certificate verification (default: true)
- `PATH_TO_COURSES`: Path to directory containing course markdown files for chapter title extraction

## Usage

### Command Line

```bash
upload-folder-peertube /path/to/video/folder
```

### Python Module

```python
from peertube_uploader.config import Config
from peertube_uploader.finder import find_mp4_files
from peertube_uploader.client import PeerTubeClient
from peertube_uploader.utils import generate_title, generate_description

config = Config()
client = PeerTubeClient(config)

for video_path in find_mp4_files("/path/to/videos"):
    title = generate_title(video_path)
    description = generate_description(video_path)
    result = client.upload_video(video_path, title, description)
    print(f"Uploaded: {result}")
```

## Filename Conventions

The tool extracts metadata from filenames using these patterns:

### Course Videos

- **Format**: `{course_index}_{part}.{chapter}_{language}.mp4`
- **Example**: `btc101_2.1_en-US.mp4`
  - Course: `btc101`
  - Part: `2`
  - Chapter: `1`
  - Language: `en`

### Language Codes

Supported patterns:

- `video_es.mp4` → `es`
- `video-en-US.mp4` → `en`
- `video_en_US.mp4` → `en`
- `video-2.1-fr.mp4` → `fr`

## Course Structure

If using course markdown files, organize them as:

```
/path/to/courses/
├── btc101/
│   ├── en.md
│   ├── es.md
│   └── fr.md
└── cyp201/
    ├── en.md
    └── es.md
```

Markdown files should have front matter delimited by `+++` and use:

- `#` for parts
- `##` for chapters

## Development

### Running Tests

```bash
pytest tests/
```

### Project Structure

```
peertube_uploader/
├── __init__.py
├── client.py          # PeerTube API client
├── config.py          # Configuration management
├── finder.py          # File discovery utilities
├── token_manager.py   # OAuth token handling
└── utils.py           # Metadata extraction utilities
```

