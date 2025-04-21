import os
import pytest

from peertube_uploader.client import PeerTubeClient
from peertube_uploader.config import Config

class DummyConfig:
    """Minimal dummy config for testing PeerTubeClient."""
    def __init__(self):
        self.upload_url = "http://test-upload"
        self.instance_url = "http://test-instance"
        self.client_id = "id"
        self.client_secret = "secret"
        self.username = "user"
        self.password = "pass"
        self.verify_ssl = False

def test_upload_video_file_not_found(tmp_path, monkeypatch):
    cfg = DummyConfig()
    client = PeerTubeClient(cfg)
    # Ensure TokenManager does not fail before file check
    # Monkey-patch token_manager methods
    monkeypatch.setattr(client.token_manager, 'get_valid_token', lambda: 'dummy-token')
    non_existing = tmp_path / "no_video.mp4"
    with pytest.raises(FileNotFoundError):
        client.upload_video(str(non_existing), "Title", "Desc", channel_id="123")