import os
import sys
import argparse
from text_to_speech import TextToSpeechGenerator
from image_downloader import ImageDownloader
from video_creator import VideoCreator
from video_downloader import VideoDownloader
import nltk
from nltk.tokenize import sent_tokenize
import spacy
import json
import logging
from datetime import datetime
from pathlib import Path
import shutil
import traceback

class ScriptToVideo:
    def __init__(self, config_path='config.json'):
        """
        Initialize the video creation application
        
        Parameters:
        config_path (str): Path to configuration file
        """
        self.setup_logging()
        self.load_config(config_path)
        self.setup_workspace()
        self.initialize_components()
        
    def setup_logging(self):
        """Configure logging settings"""
        log_folder = "logs"
        os.makedirs(log_folder, exist_ok=True)
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        log_file = os.path.join(log_folder, f"video_creation_{timestamp}.log")
        
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler(log_file),
                logging.StreamHandler()
            ]
        )
        self.logger = logging.getLogger(__name__)
        
    def load_config(self, config_path):
        """Load configuration from JSON file"""
        try:
            with open(config_path, 'r') as f:
                self.config = json.load(f)
        except FileNotFoundError:
            self.logger.warning("Config file not found. Using default settings.")
            self.config = {
                
                "output_folder": "output",
                "temp_folder": "temp",
                "image_duration": 5,
                "video_resolution": [1080, 1920],  # Portrait orientation
                "image_quality": "high",
                "transition_duration": 1
            }
            # Save default config
            with open(config_path, 'w') as f:
                json.dump(self.config, f, indent=2)
                
    def setup_workspace(self):
        """Create necessary folders"""
        self.folders = {
            'output': self.config['output_folder'],
            'temp': self.config['temp_folder'],
            'audio': os.path.join(self.config['temp_folder'], 'audio'),
            'images': os.path.join(self.config['temp_folder'], 'images'),
            'subtitles': os.path.join(self.config['temp_folder'], 'subtitles')
        }
        
        for folder in self.folders.values():
            os.makedirs(folder, exist_ok=True)
            
    def initialize_components(self):
        """Initialize all required components"""
        try:
            # Initialize NLP components
            nltk.download('punkt', quiet=True)
            self.nlp = spacy.load('en_core_web_sm')
            
            # Initialize other components
            self.speech_generator = TextToSpeechGenerator()
            self.image_downloader = ImageDownloader()
            self.video_creator = VideoCreator()
            self.video_downloader = VideoDownloader()
            
            self.logger.info("All components initialized successfully")
        except Exception as e:
            self.logger.error(f"Failed to initialize components: {str(e)}")
            raise
            
    def extract_keywords(self, text):
        """Extract relevant keywords from text for image search"""
        doc = self.nlp(text)
        keywords = []
        
        # Extract named entities
        entities = [ent.text for ent in doc.ents]
        
        # Extract noun phrases
        noun_phrases = [chunk.text for chunk in doc.noun_chunks]
        
        # Combine and clean keywords
        keywords = list(set(entities + noun_phrases))
        
        # Filter out single-character keywords and common words
        keywords = [k for k in keywords if len(k) > 1]
        
        return keywords
        
    def create_video(self, script, method='image', topic='',voice_gender='male', language='en'):
        """
        Create a video from the given script
        
        Parameters:
        script (str): The script text
        voice_gender (str): 'male' or 'female'
        language (str): 'en' or 'hi'
        
        Returns:
        str: Path to the created video
        """
        try:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            output_video = os.path.join(
                self.folders['output'],
                f"video_{timestamp}.mp4"
            )
            
            self.logger.info("Starting video creation process...")
            
            # Step 1: Generate audio from script
            self.logger.info("Generating audio and subtitles from script...")
            audio_path = os.path.join(
                self.folders['audio'],
                f"audio_{timestamp}.wav"
            )
            subtitles_path = os.path.join(
                self.folders['subtitles'],
                f"subtitles_{timestamp}.srt"
            )
            
            success, result = self.speech_generator.generate_speech(
                script,
                voice_gender=voice_gender,
                output_path=audio_path,
                subtitles_path=subtitles_path,
                force_language=language
            )
            
            if not success:
                raise Exception(f"Audio generation failed: {result}")
            
            # Step 2: Extract keywords and download images
            words = script.split()
            total_words = len(words)
            
            # Calculate the number of keywords
            full_keywords_count = total_words // 5
            remaining_words_count = total_words % 5
            
            # Initialize an empty list to store the keywords
            keywords = []
            
            # Generate keywords for every 5 words
            for i in range(full_keywords_count):
                keyword = ' '.join(words[i * 5:(i + 1) * 5])
                keywords.append(keyword)
            
            # Generate a keyword for remaining words if any
            if remaining_words_count > 0:
                keyword = ' '.join(words[full_keywords_count * 5:])
                keywords.append(keyword)
            
            self.logger.info(keywords)
                      
                           
            images_needed = len(keywords)
            
            if method=='image':
                # Download images
                download_results = self.image_downloader.download_images(
                    keywords[:images_needed],  # Use only as many keywords as needed
                    num_results_per_term=1,
                    max_retries=5
                )
                # if download_results['successful_downloads'] == 0:
                #     raise Exception("No images were downloaded successfully")
            
                # Step 3: Create video
                self.logger.info("Finally creating video...")
                
                self.video_creator.create_image_video(
                    image_folder=self.folders['images'],
                    audio_path=audio_path,
                    output_path=output_video,
                    transition_duration=self.config['transition_duration'],
                    resolution=self.config['video_resolution']
                )
            elif method=='video':
                # Download pexel videoClips
                download_results = self.video_downloader.download_videos(keywords) 
            else :
                #Download AI Image
                self.image_downloader.create_images(keywords , topic)


                # Step 3: Create video
                self.logger.info("Finally creating video...")
                
                self.video_creator.create_image_video(
                    image_folder=self.folders['images'],
                    audio_path=audio_path,
                    subtitles_path=subtitles_path,
                    output_path=output_video,
                    transition_duration=self.config['transition_duration'],
                    resolution=self.config['video_resolution']
                ) 

            
            
            
            
            # Step 4: Cleanup temporary files
            if not self.config.get('keep_temp_files', False):
                self.logger.info("Cleaning up temporary files...")
                shutil.rmtree(self.folders['temp'])
                self.setup_workspace()
            
            self.logger.info(f"Video created successfully: {output_video}")
            return output_video
            
        except Exception as e:
            self.logger.error(f"Video creation failed in {traceback.extract_tb(e.__traceback__)[0]}:\n{str(e.__cause__)}") 
            raise

def main():
    parser = argparse.ArgumentParser(description='Create video from script')
    parser.add_argument('--script', type=str, help='Script text or path to script file')
    parser.add_argument('--method', choices=['video', 'image'], default='AIimage', help='video/image for video creation')
    parser.add_argument('--topic', type=str, default='', help='topic of script for  video creation')
    parser.add_argument('--voice', choices=['male', 'female'], default='male',
                      help='Voice gender for text-to-speech')
    parser.add_argument('--language', choices=['en', 'hi'], default='en',
                      help='Script language')
    parser.add_argument('--config', type=str, default='config.json',
                      help='Path to configuration file')
    
    args = parser.parse_args()
    
    try:
        # Initialize video creator
        creator = ScriptToVideo(args.config)
        
        # Get script from file or command line
        if os.path.isfile(args.script):
            with open(args.script, 'r', encoding='utf-8') as f:
                script = f.read()
        else:
            script = args.script
        
        # Create video
        output_video = creator.create_video(
            script,
            method=args.method,
            topic=args.topic,
            voice_gender=args.voice,
            language=args.language
        )
        
        print(f"\nVideo created successfully!")
        print(f"Output: {output_video}")
        
    except Exception as e:
        print(f"\nError: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    main()