import requests
import re
import time
import os
from yt_dlp import YoutubeDL
import urllib3
import warnings
import json

# Disable SSL verification warnings
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
warnings.filterwarnings('ignore', message='Unverified HTTPS request')

# Configuration
UPLOAD_URL = "https://upload.peertube.planb.network"
PEERTUBE_INSTANCE = "https://peertube.planb.network"
CLIENT_ID = "2o4ppa8psgqt6x4aq6d2q4f15h7b6tav"
CLIENT_SECRET = "uGiV5QtUAReyUwbUX6vLxkx9hEKel7ol"
USERNAME = "root"
PASSWORD = "aVaM3bKQu5qDj7KYt2"

class TokenManager:
    def __init__(self):
        self.access_token = None
        self.refresh_token = None
        self.token_expires = 0
        self.refresh_token_expires = 0

    def test_server_connection(self):
        try:
            response = requests.get(PEERTUBE_INSTANCE, verify=False)
            print(f"Server connection test status: {response.status_code}")
            return response.status_code == 200
        except Exception as e:
            print(f"Server connection test failed: {str(e)}")
            return False

    def get_new_tokens(self):
        print("\nAttempting to get new tokens...")
        print(f"Using instance: {PEERTUBE_INSTANCE}")
        print(f"Client ID: {CLIENT_ID}")
        print(f"Username: {USERNAME}")

        if not self.test_server_connection():
            print("Failed to connect to server. Please check the server URL and your connection.")
            return False

        try:
            headers = {
                'Content-Type': 'application/x-www-form-urlencoded',
                'Accept': 'application/json'
            }

            data = {
                "client_id": CLIENT_ID,
                "client_secret": CLIENT_SECRET,
                "grant_type": "password",
                "response_type": "code",
                "username": USERNAME,
                "password": PASSWORD
            }

            print("\nSending token request...")
            response = requests.post(
                f"{PEERTUBE_INSTANCE}/api/v1/users/token",
                headers=headers,
                data=data,
                verify=False
            )
            
            print(f"Response status code: {response.status_code}")
            print(f"Response headers: {json.dumps(dict(response.headers), indent=2)}")
            print(f"Response content: {response.text}")
            
            if response.status_code == 200:
                self.update_tokens(response.json())
                print("Successfully obtained new tokens")
                return True
            else:
                print(f"Failed to get tokens. Status code: {response.status_code}")
                return False

        except requests.exceptions.RequestException as e:
            print(f"Network error while getting tokens: {str(e)}")
            return False
        except json.JSONDecodeError as e:
            print(f"Error parsing JSON response: {str(e)}")
            return False
        except Exception as e:
            print(f"Unexpected error while getting tokens: {str(e)}")
            return False

    def refresh_access_token(self):
        print("\nAttempting to refresh access token...")
        try:
            headers = {
                'Content-Type': 'application/x-www-form-urlencoded',
                'Accept': 'application/json'
            }

            response = requests.post(
                f"{PEERTUBE_INSTANCE}/api/v1/users/token",
                headers=headers,
                data={
                    "client_id": CLIENT_ID,
                    "client_secret": CLIENT_SECRET,
                    "grant_type": "refresh_token",
                    "refresh_token": self.refresh_token
                },
                verify=False
            )
            
            print(f"Refresh token response status: {response.status_code}")
            
            if response.status_code == 200:
                self.update_tokens(response.json())
                print("Successfully refreshed token")
                return True
            else:
                print(f"Failed to refresh token. Response: {response.text}")
                return False

        except Exception as e:
            print(f"Error refreshing token: {str(e)}")
            return False

    def update_tokens(self, data):
        try:
            current_time = time.time()
            self.access_token = data['access_token']
            self.refresh_token = data['refresh_token']
            self.token_expires = current_time + data['expires_in']
            self.refresh_token_expires = current_time + data['refresh_token_expires_in']
            
            print("Token information updated successfully")
            print(f"Token expires in: {data['expires_in']} seconds")
            print(f"Refresh token expires in: {data['refresh_token_expires_in']} seconds")
        
        except KeyError as e:
            print(f"Error updating tokens - missing key in response: {str(e)}")
            raise

    def get_valid_token(self):
        current_time = time.time()
        
        if not self.access_token or current_time >= self.refresh_token_expires:
            if not self.get_new_tokens():
                raise Exception("Failed to get new tokens")
            return self.access_token

        if current_time >= self.token_expires:
            if not self.refresh_access_token():
                if not self.get_new_tokens():
                    raise Exception("Failed to refresh token and get new tokens")
            
        return self.access_token

class VideoProcessor:
    def __init__(self):
        self.token_manager = TokenManager()

    def print_progress(self, current, total, phase, title, error=None):
        percentage = (current / total) * 100
        if error:
            print(f"ERROR [{phase}] ({current}/{total}) - {percentage:.1f}% - {title}")
            print(f"→ Error details: {error}")
        else:
            print(f"[{phase}] ({current}/{total}) - {percentage:.1f}% - {title}")

    def get_channel_id(self):
        try:
            headers = {
                'Authorization': f'Bearer {self.token_manager.get_valid_token()}',
                'Accept': 'application/json'
            }
            
            print("\nFetching channel ID...")
            response = requests.get(
                f"{PEERTUBE_INSTANCE}/api/v1/users/me",
                headers=headers,
                verify=False
            )
            
            print(f"Channel ID response status: {response.status_code}")
            print(f"Channel ID response: {response.text}")
            
            if response.status_code == 200:
                user_data = response.json()
                if 'videoChannels' in user_data and len(user_data['videoChannels']) > 0:
                    channel_id = user_data['videoChannels'][0]['id']
                    print(f"Successfully retrieved channel ID: {channel_id}")
                    return channel_id
                else:
                    print("No video channels found in user data")
            else:
                print(f"Failed to get channel ID. Status code: {response.status_code}")
                
        except Exception as e:
            print(f"Error getting channel ID: {str(e)}")
        return None

    def video_exists(self, title, channel_id):
        try:
            headers = {
                'Authorization': f'Bearer {self.token_manager.get_valid_token()}',
                'Accept': 'application/json'
            }
            
            params = {
                'search': title,
                'channelId': channel_id
            }
            
            response = requests.get(
                f"{PEERTUBE_INSTANCE}/api/v1/videos",
                headers=headers,
                params=params,
                verify=False
            )
            
            if response.status_code == 200:
                data = response.json()
                exists = any(video['name'].lower() == title.lower() for video in data.get('data', []))
                if exists:
                    print(f"Video '{title}' already exists")
                return exists
            else:
                print(f"Error checking video existence. Status code: {response.status_code}")
                return False
                
        except Exception as e:
            print(f"Error checking video existence: {str(e)}")
            return False

    def download_youtube_video(self, youtube_id):
        print(f"\nAttempting to download YouTube video: {youtube_id}")
        ydl_opts = {
            'format': 'bestvideo[ext=mp4]+bestaudio[ext=m4a]/best[ext=mp4]/best',
            'merge_output_format': 'mp4',
            'outtmpl': f'{youtube_id}.mp4',
            'quiet': True,
            'nocheckcertificate': True
        }
        
        try:
            with YoutubeDL(ydl_opts) as ydl:
                ydl.download([f'https://www.youtube.com/watch?v={youtube_id}'])
                print(f"Successfully downloaded video: {youtube_id}")
                return f'{youtube_id}.mp4', None
        except Exception as e:
            print(f"Error downloading video: {str(e)}")
            return None, str(e)

    def upload_video(self, video_path, title, description, channel_id):
        try:
            print(f"\nAttempting to upload video: {title}")
            headers = {
                'Authorization': f'Bearer {self.token_manager.get_valid_token()}'
            }
            
            data = {
                'name': title,
                'description': description,
                'privacy': 1,
                'channelId': channel_id
            }
            
            with open(video_path, 'rb') as f:
                files = {
                    'videofile': ('video.mp4', f, 'video/mp4')
                }
                
                print("Sending upload request...")
                response = requests.post(
                    f"{UPLOAD_URL}/api/v1/videos/upload",
                    headers=headers,
                    data=data,
                    files=files,
                    verify=False
                )
                
                print(f"Upload response status: {response.status_code}")
                print(f"Upload response: {response.text}")
                
                if response.status_code in (200, 201):
                    print("Upload successful")
                    return response.json(), None
                return None, f"HTTP Error {response.status_code}"
                    
        except Exception as e:
            print(f"Error during upload: {str(e)}")
            return None, str(e)

    def parse_markdown_file(self, file_path):
        print(f"\nParsing markdown file: {file_path}")
        try:
            with open(file_path, 'r', encoding='utf-8') as file:
                content = file.read()
            
            videos = []
            youtube_id_blocks = re.finditer(r'- YouTube ID: ([^\n]+)', content)
            
            for match in youtube_id_blocks:
                youtube_id = match.group(1).strip()
                start_pos = match.end()
                next_block = content[start_pos:content.find('## Folder:', start_pos) if content.find('## Folder:', start_pos) != -1 else len(content)]
                
                title_match = re.search(r'title: (.+)', next_block)
                title = title_match.group(1).strip() if title_match else ''
                
                description_match = re.search(r'description: *\n(.*?)(?=\n\n|$)', next_block, re.DOTALL)
                description = description_match.group(1).strip() if description_match else ''
                
                videos.append({
                    'youtube_id': youtube_id,
                    'title': title,
                    'description': description
                })
            
            print(f"Found {len(videos)} videos in markdown file")
            return videos
            
        except FileNotFoundError:
            print(f"Error: File not found at path: {file_path}")
            return []
        except Exception as e:
            print(f"Error parsing markdown file: {str(e)}")
            return []

    def process_videos(self):
        print("\nStarting video processing...")
        
        # Initialize token
        print("Initializing token...")
        self.token_manager.get_valid_token()
        
        # Get channel ID
        channel_id = self.get_channel_id()
        if not channel_id:
            print("Could not get channel ID. Aborting.")
            return
        
        print(f"Using channel ID: {channel_id}")
        
        # Get videos from markdown file
        videos = self.parse_markdown_file('../logs/channels-info.md')
        if not videos:
            print("No videos found to process. Aborting.")
            return

        total_videos = len(videos)
        
        for index, video in enumerate(videos, 1):
            if self.video_exists(video['title'], channel_id):
                print(f"SKIPPED ({index}/{total_videos}) - {video['title']} (Already exists)")
                continue
            
            # Download phase
            self.print_progress(index, total_videos, "DOWNLOADING", video['title'])
            video_path, error = self.download_youtube_video(video['youtube_id'])
            
            if error:
                self.print_progress(index, total_videos, "DOWNLOAD FAILED", video['title'], error)
                continue

            if video_path and os.path.exists(video_path):
                try:
                    # Upload phase
                    self.print_progress(index, total_videos, "UPLOADING", video['title'])
                    result, error = self.upload_video(
                        video_path=video_path,
                        title=video['title'],
                        description=video['description'],
                        channel_id=channel_id
                    )
                    
                    if result:
                        self.print_progress(index, total_videos, "COMPLETED", video['title'])
                    else:
                        self.print_progress(index, total_videos, "UPLOAD FAILED", video['title'], error)
                    
                finally:
                    try:
                        os.remove(video_path)
                        print(f"Cleaned up temporary file: {video_path}")
                    except Exception as e:
                        print(f"Error cleaning up file {video_path}: {str(e)}")

def main():
    try:
        print("\nStarting PeerTube video processor...")
        processor = VideoProcessor()
        processor.process_videos()
        print("\nProcess completed!")
    except Exception as e:
        print(f"Fatal error: {str(e)}")

if __name__ == "__main__":
    main()

