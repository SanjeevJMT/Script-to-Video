import os
import requests
import logging
from datetime import datetime
from urllib.parse import quote_plus
import json
from pathlib import Path
import time
from tqdm import tqdm
from google_images_download import google_images_download
import shutil

class ImageDownloader:
    def __init__(self, unsplash_api_key=None):
        """
        Initialize the ImageDownloader
        
        Parameters:
        unsplash_api_key (str): Optional Unsplash API key
        """
        self.unsplash_api_key = unsplash_api_key
        self.unsplash_base_url = "https://api.unsplash.com"
        self.google_downloader = google_images_download.googleimagesdownload()
        self.setup_logging()
        self.setup_folders()
        
    def setup_logging(self):
        """Configure logging settings"""
        log_folder = "logs"
        os.makedirs(log_folder, exist_ok=True)
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        log_file = os.path.join(log_folder, f"image_download_{timestamp}.log")
        
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler(log_file),
                logging.StreamHandler()
            ]
        )
        self.logger = logging.getLogger(__name__)
        
    def setup_folders(self):
        """Create necessary folders for images and metadata"""
        self.image_folder = "images"
        self.metadata_folder = os.path.join(self.image_folder, "metadata")
        os.makedirs(self.image_folder, exist_ok=True)
        os.makedirs(self.metadata_folder, exist_ok=True)

    def download_google_images(self, keyword, count=1, orientation="vertical"):
        """
        Download images from Google Images
        
        Parameters:
        keyword (str): Search keyword
        count (int): Number of images to download
        orientation (str): 'vertical' or 'horizontal'
        
        Returns:
        list: Paths of downloaded images
        """
        try:
            self.logger.info(f"Searching Google Images for: {keyword}")
            
            # Configure Google Images download parameters
            arguments = {
                "keywords": keyword,
                "limit": count,
                "format": "jpg",
                "size": ">2MP",  # High quality images
                "aspect_ratio": "tall" if orientation == "vertical" else "wide",
                "output_directory": self.image_folder,
                
                "no_directory": True,
                "silent_mode": True,
                "prefix": f"google_{keyword}_"
            }
            
            # Download images
            paths = self.google_downloader.download(arguments)
            
            # Process downloaded images
            downloaded_files = []
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            
            for i, (url, path) in enumerate(paths[0][keyword]):
                if path and os.path.exists(path):
                    # Create new filename
                    new_filename = f"google_{keyword}_{timestamp}_{i+1}.jpg"
                    new_path = os.path.join(self.image_folder, new_filename)
                    
                    # Move and rename file
                    shutil.move(path, new_path)
                    
                    # Create metadata
                    metadata = {
                        'source': 'google',
                        'keyword': keyword,
                        'download_time': timestamp,
                        'original_url': url,
                        'sequence': i + 1
                    }
                    
                    metadata_path = os.path.join(
                        self.metadata_folder,
                        f"{new_filename}.json"
                    )
                    
                    with open(metadata_path, 'w', encoding='utf-8') as f:
                        json.dump(metadata, f, indent=2)
                    
                    downloaded_files.append(new_path)
                    self.logger.info(f"Successfully downloaded and processed: {new_filename}")
                    
            return downloaded_files
            
        except Exception as e:
            self.logger.error(f"Error downloading from Google Images: {str(e)}")
            return []

    def download_unsplash_image(self, image_data, keyword):
        """Download a single image from Unsplash"""
        try:
            image_url = image_data['urls']['raw'] + "&q=100&w=2400"
            image_id = image_data['id']
            
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            image_filename = f"unsplash_{keyword}_{image_id}_{timestamp}.jpg"
            image_path = os.path.join(self.image_folder, image_filename)
            
            response = requests.get(image_url, stream=True)
            response.raise_for_status()
            
            total_size = int(response.headers.get('content-length', 0))
            block_size = 1024
            
            with open(image_path, 'wb') as f, tqdm(
                desc=image_filename,
                total=total_size,
                unit='iB',
                unit_scale=True,
                unit_divisor=1024,
            ) as pbar:
                for data in response.iter_content(block_size):
                    size = f.write(data)
                    pbar.update(size)
            
            metadata = {
                'source': 'unsplash',
                'id': image_id,
                'keyword': keyword,
                'download_time': timestamp,
                'photographer': image_data['user']['name'],
                'description': image_data['description'] or image_data['alt_description'],
                'width': image_data['width'],
                'height': image_data['height'],
                'likes': image_data['likes'],
                'original_url': image_data['links']['html']
            }
            
            metadata_path = os.path.join(
                self.metadata_folder,
                f"{image_filename}.json"
            )
            
            with open(metadata_path, 'w', encoding='utf-8') as f:
                json.dump(metadata, f, indent=2)
            
            return True, image_path
            
        except Exception as e:
            self.logger.error(f"Failed to download Unsplash image: {str(e)}")
            return False, None

    def download_batch(self, keywords, images_per_keyword=1, source="both", orientation="vertical"):
        """
        Download images from specified source(s)
        
        Parameters:
        keywords (list): List of search keywords
        images_per_keyword (int): Number of images per keyword
        source (str): 'google', 'unsplash', or 'both'
        orientation (str): 'vertical' or 'horizontal'
        
        Returns:
        dict: Summary of download results
        """
        results = {
            'total_requested': len(keywords) * images_per_keyword,
            'successful_downloads': 0,
            'failed_downloads': 0,
            'sources': {}
        }
        
        self.logger.info(f"Starting batch download for {len(keywords)} keywords from {source}")
        
        for keyword in keywords:
            self.logger.info(f"Processing keyword: {keyword}")
            
            # Google Images Download
            if source in ["google", "both"]:
                google_images = self.download_google_images(
                    keyword,
                    count=images_per_keyword,
                    orientation=orientation
                )
                results['sources'].setdefault('google', {'successful': 0, 'failed': 0})
                results['sources']['google']['successful'] += len(google_images)
                results['sources']['google']['failed'] += images_per_keyword - len(google_images)
                results['successful_downloads'] += len(google_images)
                results['failed_downloads'] += images_per_keyword - len(google_images)
            
            # Unsplash Download
            if source in ["unsplash", "both"] and self.unsplash_api_key:
                unsplash_params = {
                    'query': keyword,
                    'orientation': orientation,
                    'per_page': images_per_keyword,
                    'client_id': self.unsplash_api_key
                }
                
                response = requests.get(
                    f"{self.unsplash_base_url}/search/photos",
                    params=unsplash_params
                )
                
                if response.status_code == 200:
                    images = response.json()['results']
                    results['sources'].setdefault('unsplash', {'successful': 0, 'failed': 0})
                    
                    for image_data in images:
                        success, _ = self.download_unsplash_image(image_data, keyword)
                        if success:
                            results['sources']['unsplash']['successful'] += 1
                            results['successful_downloads'] += 1
                        else:
                            results['sources']['unsplash']['failed'] += 1
                            results['failed_downloads'] += 1
                        time.sleep(1)  # Respect API rate limits
            
        self.logger.info("Batch download completed")
        self.logger.info(f"Summary: {json.dumps(results, indent=2)}")
        
        return results

def main():
    # Initialize downloader (Unsplash API key is optional)
    downloader = ImageDownloader(unsplash_api_key="YOUR_UNSPLASH_API_KEY")
    
    # Example usage
    keywords = ["nature", "architecture", "people"]
    
    # Download from Google Images only
    google_results = downloader.download_batch(
        keywords,
        images_per_keyword=2,
        source="google",
        orientation="vertical"
    )
    
    # Download from both sources
    both_results = downloader.download_batch(
        keywords,
        images_per_keyword=2,
        source="both",
        orientation="vertical"
    )
    
    print("\nDownload Summary:")
    print(json.dumps(both_results, indent=2))

if __name__ == "__main__":
    main()