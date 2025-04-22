"""
Client for uploading videos to PeerTube.
"""
import os
import requests
import urllib3
import warnings

from .token_manager import TokenManager

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
warnings.filterwarnings('ignore', message='Unverified HTTPS request')

class PeerTubeClient:
    """
    Upload videos to a PeerTube instance using OAuth authentication.
    """
    def __init__(self, config):
        self.config = config
        self.token_manager = TokenManager(config)

    def get_channel_id(self):
        """
        Fetch the user's first video channel ID.
        """
        token = self.token_manager.get_valid_token()
        url = f"{self.config.instance_url}/api/v1/users/me"
        headers = {
            "Authorization": f"Bearer {token}",
            "Accept": "application/json",
        }
        # Disable SSL verification to avoid certificate errors
        resp = requests.get(url, headers=headers, verify=False)
        resp.raise_for_status()
        data = resp.json()
        channels = data.get("videoChannels")
        if not channels:
            raise Exception("No video channels available for user")
        return channels[0].get("id")

    def upload_video(self, video_path, title, description="", channel_id=None):
        """
        Upload a single video file to PeerTube.

        Args:
            video_path (str): Path to the .mp4 file.
            title (str): Title of the video.
            description (str): Description of the video.
            channel_id (str|int): Optional channel ID; fetched if not provided.
z
        Returns:
            dict: JSON response from PeerTube with upload details.

        Raises:
            FileNotFoundError: If the video file does not exist.
            Exception: For HTTP or API errors.
        """
        if not os.path.isfile(video_path):
            raise FileNotFoundError(f"Video file not found: {video_path}")

        if channel_id is None:
            channel_id = self.get_channel_id()

        token = self.token_manager.get_valid_token()
        # Single-request upload: build multipart/form-data
        url = f"{self.config.upload_url}/api/v1/videos/upload"
        headers = {"Authorization": f"Bearer {token}"}
        # Prepare form fields as multipart entries
        fields = {
            "name": title,
            "description": description,
            "privacy": 1,
            "channelId": channel_id,
        }
        multipart = {}
        # Add form fields (None filename to signal form field)
        for key, val in fields.items():
            multipart[key] = (None, str(val))
        # Add the video file
        filename = os.path.basename(video_path)
        with open(video_path, "rb") as f:
            multipart["videofile"] = (filename, f, "video/mp4")
            # Execute request (SSL verification disabled)
            resp = requests.post(
                url,
                headers=headers,
                files=multipart,
                verify=False,
            )
        # Handle response: if success, return JSON, else raise with payload
        if resp.status_code not in (200, 201):
            # Attempt to extract JSON error, fallback to text
            try:
                detail = resp.json()
            except Exception:
                detail = resp.text
            raise Exception(f"Upload failed: HTTP {resp.status_code} - {detail}")
        return resp.json()
