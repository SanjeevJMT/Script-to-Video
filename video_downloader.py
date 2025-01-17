import os
import json
import requests

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

    def download_videos(self, search_keywords):
        for idx, keyword in enumerate(search_keywords):
            params = {'query': keyword,"orientation": "portrait", 'per_page': 1}
            response = requests.get(self.api_url, headers=self.headers, params=params)
            if response.status_code == 200:
                data = response.json()
                if data['videos']:
                    video_url = data['videos'][0]['video_files'][0]['link']
                    video_path = os.path.join(self.temp_dir, f'{idx+1:02d}.mp4')
                    self._download_video(video_url, video_path)
                else:
                    print(f"No videos found for keyword: {keyword}")
            else:
                print(f"Failed to search for keyword: {keyword}. Status code: {response.status_code}")

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