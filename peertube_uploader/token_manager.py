"""
Manage OAuth tokens for PeerTube API.
"""
import time
import requests
from typing import Dict, Any
from .config import Config

class TokenManager:
    """
    Handles obtaining and refreshing access tokens for PeerTube.
    """
    def __init__(self, config: Config) -> None:
        self.config: Config = config
        self.access_token: Any = None
        self.refresh_token: Any = None
        self.token_expires: float = 0.0
        self.refresh_token_expires: float = 0.0

    def _request_tokens(self, data: Dict[str, str]) -> Dict[str, Any]:
        url = f"{self.config.instance_url}/api/v1/users/token"
        headers = {
            "Content-Type": "application/x-www-form-urlencoded",
            "Accept": "application/json",
        }
        # Disable SSL verification to avoid certificate errors
        response = requests.post(
            url,
            headers=headers,
            data=data,
            verify=False,
        )
        if response.status_code != 200:
            raise Exception(f"Token request failed: {response.status_code} {response.text}")
        return response.json()

    def get_new_tokens(self) -> None:
        """
        Obtain new access and refresh tokens using user credentials.
        """
        # Password grant: include response_type before credentials to match PeerTube API expectations
        data = {
            "client_id": self.config.client_id,
            "client_secret": self.config.client_secret,
            "grant_type": "password",
            "response_type": "code",
            "username": self.config.username,
            "password": self.config.password,
        }
        token_data = self._request_tokens(data)
        self._update_tokens(token_data)

    def refresh_access_token(self) -> None:
        """
        Refresh the access token using the refresh token.
        """
        data = {
            "client_id": self.config.client_id,
            "client_secret": self.config.client_secret,
            "grant_type": "refresh_token",
            "refresh_token": self.refresh_token,
        }
        token_data = self._request_tokens(data)
        self._update_tokens(token_data)

    def _update_tokens(self, data: Dict[str, Any]) -> None:
        now = time.time()
        self.access_token = data.get("access_token")
        self.refresh_token = data.get("refresh_token")
        self.token_expires = now + data.get("expires_in", 0)
        self.refresh_token_expires = now + data.get("refresh_token_expires_in", 0)

    def get_valid_token(self) -> str:
        """
        Return a valid access token, obtaining or refreshing as needed.
        """
        now = time.time()
        # If no token or expired, refresh or obtain new
        if not self.access_token or now >= self.token_expires:
            if self.refresh_token and now < self.refresh_token_expires:
                self.refresh_access_token()
            else:
                self.get_new_tokens()
        return self.access_token