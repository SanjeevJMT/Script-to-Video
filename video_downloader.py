import os
import json
import requests
from moviepy import  VideoFileClip
import subprocess

class VideoDownloader:
    def __init__(self, config_path='config.json'):
        with open(config_path, 'r') as file:
            self.config = json.load(file)
        self.api_url = self.config['api_url']
        self.api_key = self.config['api_key']
        self.headers = {
            'Authorization': self.api_key
        }
        self.temp_dir = 'temp/videos'
        os.makedirs(self.temp_dir, exist_ok=True)

    def download_videos(self, search_keywords, required_resolution=(1080, 1920)):
        """Downloads videos matching search keywords and a specific resolution.

        Args:
            search_keywords: A list of search keywords.
            required_resolution: A tuple (width, height) specifying the desired resolution.
                            Defaults to (1080, 1920).
        """

        for idx, keyword in enumerate(search_keywords):
            params = {'query': keyword, "orientation": "portrait", 'per_page': 1}  # Keep 'per_page': 1
            response = requests.get(self.api_url, headers=self.headers, params=params)

            if response.status_code == 200:
                data = response.json()
                if data['videos']:
                    video_data = data['videos'][0] # Get the whole video data so we can check all available resolutions
                    best_video_url = None
                    best_video_path = None

                    for file_data in video_data.get('video_files', []):  # Iterate through available resolutions
                        video_url = file_data.get('link')
                        if video_url:
                            resolution = self.get_video_resolution(video_url)
                            if resolution:
                                width, height = resolution
                                print(f"Found resolution: {width}x{height} for {keyword}")

                                if (width, height) == required_resolution:
                                    best_video_url = video_url
                                    best_video_path = os.path.join(self.temp_dir, f'{idx+1:02d}.mp4')
                                    break # Found our resolution, no need to check other resolutions
                            else:
                                print(f"Could not get resolution for {keyword} from URL: {video_url}")


                    if best_video_url:
                        self._download_video(best_video_url, best_video_path)
                        print(f"Downloaded video for keyword '{keyword}' with resolution {required_resolution}")
                    else:
                        print(f"No video found with resolution {required_resolution} for keyword: {keyword}")

                else:
                    print(f"No videos found for keyword: {keyword}")
            else:
                print(f"Failed to search for keyword: {keyword}. Status code: {response.status_code}")

    def get_video_resolution(self, video_url):
        """Gets the resolution of a video from a URL using ffprobe.

        Args:
            video_url: The URL of the video.

        Returns:
            A tuple (width, height) or None if the resolution could not be determined.
        """
        try:
            # Construct the ffprobe command
            command = [
                "ffprobe",
                "-v", "error",  # Only show errors
                "-select_streams", "v:0",  # Select only the video stream
                "-show_entries", "stream=width,height",  # Show width and height
                "-of", "csv=s=x:p=0",  # Output in CSV format (widthxheight)
                video_url
            ]

            result = subprocess.run(command, capture_output=True, text=True, check=True)  # Run ffprobe
            output = result.stdout.strip()

            width, height = map(int, output.split("x")) # Extract width and height
            return (width, height)

        except subprocess.CalledProcessError as e:
            print(f"Error running ffprobe: {e}")
            print(f"ffprobe stderr: {e.stderr}") # Important for debugging
            return None
        except ValueError:  # If the output is not in the expected format
            print("Unexpected ffprobe output format.")
            return None
        except FileNotFoundError:
            print("ffprobe not found. Make sure FFmpeg is installed and in your PATH.")
            return None


    def _download_video(self, url, path):
        response = requests.get(url, stream=True)
        if response.status_code == 200:
            with open(path, 'wb') as file:
                for chunk in response.iter_content(chunk_size=1024):
                    if chunk:
                        file.write(chunk)
            print(f"Downloaded video to {path}")
        else:
            print(f"Failed to download video from {url}. Status code: {response.status_code}")