import os
import pytest

from peertube_uploader.config import Config

def test_config_success(monkeypatch):
    # Set required environment variables
    monkeypatch.setenv("UPLOAD_URL", "https://upload")
    monkeypatch.setenv("PEERTUBE_INSTANCE", "https://instance")
    monkeypatch.setenv("CLIENT_ID", "id")
    monkeypatch.setenv("CLIENT_SECRET", "secret")
    monkeypatch.setenv("USERNAME", "user")
    monkeypatch.setenv("PASSWORD", "pass")
    # Optional VERIFY_SSL defaults to true
    if "VERIFY_SSL" in os.environ:
        monkeypatch.delenv("VERIFY_SSL", raising=False)

    cfg = Config()
    assert cfg.upload_url == "https://upload"
    assert cfg.instance_url == "https://instance"
    assert cfg.client_id == "id"
    assert cfg.client_secret == "secret"
    assert cfg.username == "user"
    assert cfg.password == "pass"
    assert cfg.verify_ssl is True

def test_config_missing(monkeypatch):
    # Unset all required variables
    monkeypatch.delenv("UPLOAD_URL", raising=False)
    monkeypatch.delenv("PEERTUBE_INSTANCE", raising=False)
    monkeypatch.delenv("CLIENT_ID", raising=False)
    monkeypatch.delenv("CLIENT_SECRET", raising=False)
    monkeypatch.delenv("USERNAME", raising=False)
    monkeypatch.delenv("PASSWORD", raising=False)

    with pytest.raises(ValueError) as excinfo:
        Config()
    msg = str(excinfo.value)
    assert "Missing required environment variables" in msg