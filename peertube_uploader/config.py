# Disable SSL warnings for unverified HTTPS requests
import warnings
import urllib3
from urllib3.exceptions import InsecureRequestWarning

urllib3.disable_warnings(InsecureRequestWarning)
warnings.filterwarnings('ignore', message='Unverified HTTPS request')
"""
Configuration loader for PeerTube uploader.
"""
import os
# Optionally load environment variables from a .env file in the current working directory
# Optionally load .env via python-dotenv if available
try:
    from dotenv import load_dotenv
    env_path = os.path.join(os.getcwd(), '.env')
    if os.path.isfile(env_path):
        load_dotenv(env_path, override=True)
except ImportError:
    # python-dotenv not available
    pass

# Fallback: manual parsing of .env key=value lines
_env_path = os.path.join(os.getcwd(), '.env')
if os.path.isfile(_env_path):
    with open(_env_path, 'r', encoding='utf-8') as _f:
        for _line in _f:
            _line = _line.strip()
            if not _line or _line.startswith('#') or '=' not in _line:
                continue
            _key, _val = _line.split('=', 1)
            _key = _key.strip()
            _val = _val.strip()
            # Strip surrounding quotes
            if (_val.startswith('"') and _val.endswith('"')) or (_val.startswith("'") and _val.endswith("'")):
                _val = _val[1:-1].strip()
            os.environ.setdefault(_key, _val)

class Config:
    """
    Load and store PeerTube configuration from environment variables.
    Required variables: UPLOAD_URL, PEERTUBE_INSTANCE, CLIENT_ID,
    CLIENT_SECRET, USERNAME, PASSWORD. Optional VERIFY_SSL.
    Surrounding whitespace and quotes are stripped from values.
    """
    client_id: str
    client_secret: str
    username: str
    password: str
    verify_ssl: bool
    upload_url: str
    instance_url: str
    course_path: str

    def __init__(self) -> None:
        missing = []
        # Helper to read and clean env vars
        def _get_env(name, required=True, default=None):
            raw = os.getenv(name)
            if raw is None:
                if required:
                    missing.append(name)
                return default
            val = raw.strip()
            # Strip surrounding single or double quotes
            if (val.startswith('"') and val.endswith('"')) or (val.startswith("'") and val.endswith("'")):
                val = val[1:-1].strip()
            return val

        # Read required variables
        upload = _get_env("UPLOAD_URL")
        instance = _get_env("PEERTUBE_INSTANCE")
        self.client_id = _get_env("CLIENT_ID")
        self.client_secret = _get_env("CLIENT_SECRET")
        self.username = _get_env("USERNAME")
        self.password = _get_env("PASSWORD")
        # SSL verification flag
        verify_raw = _get_env("VERIFY_SSL", required=False, default="true")
        self.verify_ssl = str(verify_raw).lower() in ("true", "1", "yes")
        # Courses directory path
        courses_path = _get_env("PATH_TO_COURSES")
        self.course_path = (
            os.path.abspath(os.path.expanduser(courses_path))
            if courses_path
            else courses_path
        )

        if missing:
            raise ValueError(f"Missing required environment variables: {', '.join(missing)}")

        # Normalize URLs
        self.upload_url = upload.rstrip('/') if upload else upload
        self.instance_url = instance.rstrip('/') if instance else instance