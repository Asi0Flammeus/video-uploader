"""
Configuration loader for PeerTube uploader.
"""
import os
# Optionally load environment variables from a .env file if python-dotenv is installed
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    # python-dotenv is not installed; environment variables must be set externally
    pass

class Config:
    """
    Load and store PeerTube configuration from environment variables.
    Required variables:
      - UPLOAD_URL
      - PEERTUBE_INSTANCE
      - CLIENT_ID
      - CLIENT_SECRET
      - USERNAME
      - PASSWORD
      - VERIFY_SSL (optional, defaults to true)
    """
    def __init__(self):
        # Load and normalize URLs (remove trailing slash if present)
        _upload = os.getenv("UPLOAD_URL")
        self.upload_url = _upload.rstrip("/") if _upload else _upload
        _instance = os.getenv("PEERTUBE_INSTANCE")
        self.instance_url = _instance.rstrip("/") if _instance else _instance
        self.client_id = os.getenv("CLIENT_ID")
        self.client_secret = os.getenv("CLIENT_SECRET")
        self.username = os.getenv("USERNAME")
        self.password = os.getenv("PASSWORD")
        # SSL verification flag
        self.verify_ssl = os.getenv("VERIFY_SSL", "true").lower() in ("true", "1", "yes")

        missing = [
            name for name in (
                "UPLOAD_URL",
                "PEERTUBE_INSTANCE",
                "CLIENT_ID",
                "CLIENT_SECRET",
                "USERNAME",
                "PASSWORD",
            )
            if os.getenv(name) is None
        ]
        if missing:
            raise ValueError(f"Missing required environment variables: {', '.join(missing)}")