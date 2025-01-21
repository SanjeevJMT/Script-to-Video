from bs4 import BeautifulSoup
import json
import requests
import os
import re
import time

class ImageDownloader:
    """
    Downloads images from Google Images for given search terms.
    """

    def __init__(self):
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.36'
        }
    def create_images(self, prompts, topic):
        width=1080
        height=1920
        model='flux' 
        seed=None
        for idx, prompt in enumerate(prompts, 1):
            prompt = topic+" "+prompt
            url = f"https://image.pollinations.ai/prompt/{prompt}?width={width}&height={height}&model={model}&seed={seed}"
            response = requests.get(url)
            filename = f'{idx:02d}.jpg'
            filepath = os.path.join('temp', 'images', filename) 
            with open(filepath, 'wb') as file:
                file.write(response.content)
                print(f"created using POllinationAI: {filepath}")
    def download_images(self, search_terms, num_results_per_term=1, max_retries=5):
        """
        Downloads images for given search terms.

        Args:
            search_terms: List of search keywords.
            num_results_per_term: Number of images to download per term.
            max_retries: Maximum number of retries for failed downloads.
        """

        for idx, term in enumerate(search_terms, 1):
            hd_term=term+ " HD vertical image "
            
            print(f"\nSearching for '{hd_term}'...")
            
            # Get image URLs
            urls = get_image_urls(hd_term)
            
            if urls:
                print("\nVerifying URLs...")
                verified_urls = verify_image_urls(urls)

                #create file name
                filename = f'{idx:02d}_{term}.jpg'
                filepath = os.path.join('temp', 'images', filename) 
                retries = 0
                
                #Download Image 
                try:
                    response = requests.get(verified_urls[0], headers=self.headers)
                    response.raise_for_status()
                    with open(filepath, 'wb') as f:
                        f.write(response.content)
                    print(f"Downloaded: {filepath}")
                    break
                except Exception as e:
                        print(f"Error downloading {verified_urls[0]}: {e}")
                        retries += 1
                        time.sleep(2)  # Wait for a short time before retrying

                
                #print(f"\nTop {len(verified_urls)} verified image URLs for '{search_term}':")
                #for i, url in enumerate(verified_urls, 1):
                    #print(f"{i}. {url}")
            else:
                print("No image URLs found.")
            #########
    def get_image_urls(query, num_images=5):
        """
        Get image URLs directly from Google Images
        
        Args:
            query (str): Search query for images
            num_images (int): Number of images to retrieve
        
        Returns:
            list: List of image URLs
        """
        
        # Format the search URL
        search_url = f"https://www.google.com/search?q={query}&tbm=isch"
        
        # Headers to mimic a browser request
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
            'Connection': 'keep-alive',
        }
        
        try:
            # Make the request
            print("Fetching search results...")
            response = requests.get(search_url, headers=headers, timeout=10)
            response.raise_for_status()
            
            print("Parsing response...")
            # Find image URLs using regex
            image_urls = []
            pattern = r'https?://[^"\']+(?:jpg|jpeg|png|gif)'
            matches = re.findall(pattern, response.text, re.IGNORECASE)
            
            # Filter and clean URLs
            for url in matches:
                # Skip small thumbnails and Google's own URLs
                if 'gstatic.com' not in url and 'google.com' not in url:
                    if url not in image_urls:  # Avoid duplicates
                        image_urls.append(url)
                        print(f"Found image URL: {url}")
                        if len(image_urls) >= num_images:
                            break
            
            return image_urls
            
        except Exception as e:
            print(f"Error occurred: {str(e)}")
            return []
    def verify_image_urls(urls):
        """
        Verify that the URLs actually point to accessible images
        
        Args:
            urls (list): List of image URLs to verify
        
        Returns:
            list: List of verified image URLs
        """
        verified_urls = []
        
        for url in urls:
            try:
                # Try to fetch the header of the image
                response = requests.head(url, timeout=5)
                content_type = response.headers.get('content-type', '')
                
                # Check if it's actually an image
                if 'image' in content_type:
                    verified_urls.append(url)
                    print(f"Verified URL: {url}")
                
            except Exception as e:
                print(f"Failed to verify URL {url}: {str(e)}")
                continue
        
        return verified_urls

# Example usage
if __name__ == "__main__":
    search_term = "laddu HD image"
    print(f"\nSearching for '{search_term}'...")
    
    # Get image URLs
    urls = get_image_urls(search_term)
    
    if urls:
        print("\nVerifying URLs...")
        verified_urls = verify_image_urls(urls)
        
        print(f"\nTop {len(verified_urls)} verified image URLs for '{search_term}':")
        for i, url in enumerate(verified_urls, 1):
            print(f"{i}. {url}")
    else:
        print("No image URLs found.")

# Example usage in another Python file:

# from image_downloader import ImageDownloader

# downloader = ImageDownloader()
# search_terms = ["nature", "mountains", "cats", "dogs"]
# downloader.download_images(search_terms)