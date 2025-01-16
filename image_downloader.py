from bs4 import BeautifulSoup
import requests
import os
import time

def download_images(search_terms, num_results_per_term=1, max_retries=5):
  """
  Downloads images from Google Images for given search terms.

  Args:
    search_terms: List of search keywords.
    num_results_per_term: Number of images to download per search term.
    max_retries: Maximum number of retries for failed downloads.

  Returns:
    None
  """

  headers = {
      'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.36'
  }

  for term in search_terms:
    hd_term= term+' HD image portrait'
    url = f"https://www.google.com/search?q={hd_term}&tbm=isch"
    response = requests.get(url, headers=headers)
    soup = BeautifulSoup(response.content, 'html.parser')

    image_urls = []
    for img in soup.find_all('img'):
      try:
        img_url = img['src']
        if img_url.startswith('http'):
          image_urls.append(img_url)
      except KeyError:
        pass

    if not image_urls:
      print(f"No images found for: {term}")
      continue

    for i, img_url in enumerate(image_urls[:num_results_per_term]):
      filename = f'{term}_{i+1}.jpg'
      filepath = os.path.join('images', filename)
      retries = 0

      while retries < max_retries:
        try:
          response = requests.get(img_url, headers=headers)
          response.raise_for_status()
          with open(filepath, 'wb') as f:
            f.write(response.content)
          print(f"Downloaded: {filepath}")
          break
        except Exception as e:
          print(f"Error downloading {img_url}: {e}")
          retries += 1
          time.sleep(2)  # Wait for a short time before retrying

if __name__ == "__main__":
  search_terms = [
      "nature",
      "mountains",
      "cats",
      "dogs"
  ]

  if not os.path.exists('images'):
    os.makedirs('images')

  download_images(search_terms)