import os
from moviepy import ImageClip, AudioFileClip, concatenate_videoclips, CompositeVideoClip, VideoFileClip , TextClip
#from moviepy.video.fx.transition_sequence import TransitionSequence----- no longer supported
from moviepy.video import fx as vfx
import glob
import numpy as np
from PIL import Image
from tqdm import tqdm
import logging
import traceback
import re

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class VideoCreator:
    # Supported image formats
    SUPPORTED_IMAGE_FORMATS = ('.jpg', '.jpeg', '.png', '.gif', '.bmp', '.webp')
    # Supported video formats
    SUPPORTED_VIDEO_FORMATS = ('.mp4')
    
    # Available transition effects
    TRANSITIONS = {
        #'fade': lambda clip: (FadeIn(clip, 0.5), FadeOut(clip, 0.5)),
        'slide_left': lambda clip: clip.set_position(lambda t: (max(0, 500-1000*t), 0)),
        'slide_right': lambda clip: clip.set_position(lambda t: (min(0, -500+1000*t), 0)),
        'zoom_in': lambda clip: clip.resize(lambda t: 1 + 0.5*t),
        'zoom_out': lambda clip: clip.resize(lambda t: 2 - 0.5*t)
    }
    
    def __init__(self):
        self.progress_bar = None
    
    def create_image_video(self, 
                    image_folder, 
                    audio_path, 
                    output_path, 
                    subtitles_path,
                    transition_duration=2,
                    transition_effect='zoom_in',
                    resolution=(1080, 1920),
                    fps=30,
                    bitrate="8000k"):
        """
        Create a video from images and audio with enhanced features.
        
        Parameters:
        image_folder (str): Path to folder containing images
        audio_path (str): Path to WAV audio file
        output_path (str): Path where the output MP4 will be saved
        transition_duration (int): Duration for each image in seconds
        transition_effect (str): Type of transition ('fade', 'slide_left', 'slide_right', 'zoom_in', 'zoom_out')
        resolution (tuple): Output video resolution (width, height)
        fps (int): Frames per second
        bitrate (str): Video bitrate (higher = better quality)
        """
        try:
            logger.info("Starting video creation process...")
            
            # Load audio Subs and get its duration
            logger.info("Loading audio file...")
            audio = AudioFileClip(audio_path)
            audio_duration = audio.duration
            subtitles_path =subtitles_path
            

            # Get list of all supported images in the folder
            image_files = []
            for format in self.SUPPORTED_IMAGE_FORMATS:
                image_files.extend(glob.glob(os.path.join(image_folder, f"*{format}")))
            
            if not image_files:
                raise ValueError(f"No supported images found. Supported formats: {self.SUPPORTED_IMAGE_FORMATS}")
            
            # Sort images to ensure consistent ordering
            image_files.sort()
            logger.info(f"Found {len(image_files)} images")
            image_duration= audio_duration/len(image_files)
            
            # Create progress bar for image processing
            progress_bar = tqdm(total=len(image_files), desc="Processing images")
            
            # Create video clips from images with transitions
            image_clips = []
            for image_path in image_files:
                # Verify image and resize to target resolution
                with Image.open(image_path) as img:
                    img = img.resize(resolution, Image.LANCZOS)
                    img=img.convert('RGB')  # Convert to RGB mode
                    # Extract the base name of the image file
                    base_name = os.path.basename(image_path)
                    # Create the new path in the temp/images directory
                    resized_image_path = os.path.join('temp/images', 'resized_' + base_name)
                    # Save the resized image to the new path
                    img.save(resized_image_path)
                # Create video clip from image
                logger.info("Creating video clip from image..."+resized_image_path)
                clip = ImageClip(resized_image_path).with_duration(image_duration)  # Set duration for each image
                zoomed_clip= clip.with_effects([vfx.Resize(lambda t : 1 + 0.05*t)]) #zoom clip over time
                image_clips.append(zoomed_clip)
                    
                # Update the progress bar
                progress_bar.update(1)

            # Close the progress bar
            progress_bar.close()

            #Load Subtitles 
            subtitles =self.parse_srt(subtitles_path) 
            # Create text clips from subtitles
            subtitle_clips = self.create_text_clips(subtitles, video_size=resolution)

            #add Fixed watermark Textclip
            watermark_clip = TextClip(font ="Arial.ttf", text="MakeAIvideo.in", font_size=70, color='black',bg_color='rgb(255, 179, 255)', stroke_color='black', stroke_width=2, size=(500, None), method='caption', vertical_align='bottom')
            watermark_clip = watermark_clip.with_start(0).with_duration(audio_duration).with_position(('right','bottom'))

            #apply zoom effects in image clips   
            # zoomed_clips = [
            #     CompositeVideoClip([
            #         #clip.with_effects([vfx.Resize(lambda t : 1.3 + 0.3*np.sin(3*t/2))]) ----- working zoom in out
            #         clip.with_effects([vfx.Resize(lambda t : 1 + 0.05*t)])
            #         ])
            #     for clip in image_clips
            # ]


            final_clip = concatenate_videoclips(image_clips, padding=0)
            # Combine the blank video and text clips
            final_videoclip = CompositeVideoClip([final_clip] + subtitle_clips + [watermark_clip])

            # final_clip = concatenate_videoclips(zoomed_clips, padding=0)
            
            # If video is shorter than audio, loop the video
            if final_videoclip.duration < audio_duration:
                n_loops = int(audio_duration / final_videoclip.duration) + 1
                logger.info(f"Looping video {n_loops} times to match audio duration")
                final_videoclip = concatenate_videoclips([final_videoclip] * n_loops)
            
            # Trim video to match audio duration
            final_clip = final_videoclip.with_duration(audio_duration)

            
            
            # Set audio
            final_clip = final_clip.with_audio(audio)
            
            logger.info("Writing output file... This may take a while.")
            # Write output file with progress bar
            final_clip.write_videofile(
                output_path,
                fps=fps,
                codec='libx264',
                audio_codec='aac',
                bitrate=bitrate,
                logger=None  # Disable moviepy's logger as we're using our own
            )
            
            # Clean up
            final_clip.close()
            audio.close()
            
            logger.info(f"Video successfully created at: {output_path}")
            
        except Exception as e:
            logger.error(f"Video creator: An error occurred: in {traceback.extract_tb(e.__traceback__)[0]}:\n{str(e)}") 
            raise
    def create_text_clips(self, subtitles, video_size):
        text_clips = []
        for start_time, end_time, text in subtitles:
            duration = end_time - start_time
            text_clip = TextClip(font ="DkBergelmir-GYBP.ttf", text=text, font_size=60,margin=(10,10), color='white',bg_color='white', stroke_color='black', stroke_width=2, size=(video_size[0], None), method='caption', vertical_align='bottom')
            text_clip = text_clip.with_start(start_time).with_duration(duration).with_position(('center', int(video_size[1] * 0.7)))
            text_clips.append(text_clip)
        return text_clips
    def parse_srt(self, srt_file):
        with open(srt_file, 'r') as file:
            content = file.read()

        pattern = re.compile(r'(\d+)\n(\d{2}:\d{2}:\d{2},\d{3}) --> (\d{2}:\d{2}:\d{2},\d{3})\n(.*?)\n\n', re.DOTALL)
        matches = pattern.findall(content)

        subtitles = []
        for match in matches:
            index, start_time, end_time, text = match
            start_time = self.convert_to_seconds(start_time)
            end_time = self.convert_to_seconds(end_time)
            subtitles.append((start_time, end_time, text.replace('\n', ' ')))

        return subtitles

    def convert_to_seconds(self, time_str):
        """Convert time format 'HH:MM:SS,SSS' to seconds."""
        h, m, s = time_str.split(':')
        s, ms = s.split(',')
        return int(h) * 3600 + int(m) * 60 + int(s) + int(ms) / 1000    

    def create_clip_video(self, 
                 video_folder='/temp/videos', 
                 audio_path='/temp/audio', 
                 output_path='/output', 
                 transition_duration=2,
                 transition_effect='zoom_in',
                 target_resolution=(1080, 1920),
                 fps=30,
                 bitrate="8000k"):
        """
        Create a video from video clips and audio with enhanced features.
        
        Parameters:
        video_folder (str): Path to folder containing video clips
        audio_path (str): Path to WAV audio file
        output_path (str): Path where the output MP4 will be saved
        transition_duration (int): Duration for each video clip in seconds
        transition_effect (str): Type of transition ('fade', 'slide_left', 'slide_right', 'zoom_in', 'zoom_out')
        resolution (tuple): Output video resolution (width, height)
        fps (int): Frames per second
        bitrate (str): Video bitrate (higher = better quality)
        """
        try:
            logger.info("Starting video creation process...")
            
            # Load audio and get its duration
            logger.info("Loading audio file...")
            audio = AudioFileClip(audio_path)
            audio_duration = audio.duration
            
            # Get list of all supported video clips in the folder
            video_files = []
            for format in self.SUPPORTED_VIDEO_FORMATS:
                video_files.extend(glob.glob(os.path.join(video_folder, f"*{format}")))
            
            if not video_files:
                raise ValueError(f"No supported video clips found. Supported formats: {self.SUPPORTED_VIDEO_FORMATS}")
            
            # Sort video clips to ensure consistent ordering
            video_files.sort()
            logger.info(f"Found {len(video_files)} video clips")
            
            # Create progress bar for video clip processing
            progress_bar = tqdm(total=len(video_files), desc="Processing video clips")
            
            # Create video clips with transitions
            video_clips = []
            for video_path in video_files:
                # Create video clip from file
                # Calculate the resize factor
                width, height = target_resolution
                logger.info("Loading video clip... " + video_path)
                clip = VideoFileClip(video_path) #.target_resolution(width=width, height=height)  # Resize to target resolution
                clip = clip.with_duration(min(clip.duration, transition_duration))  # Set duration for each video clip
                video_clips.append(clip)
                    
                # Update the progress bar
                progress_bar.update(1)

            # Close the progress bar
            progress_bar.close()
                
            # Create transition clips (e.g., crossfade)
            final_clips = []
            for i in range(len(video_clips) - 1):
                final_clips.append(video_clips[i])
                transition = video_clips[i].crossfadeout(transition_duration)
                final_clips.append(transition)       
            final_clips.append(video_clips[-1])  # Add the last video clip
            
            logger.info("Compositing video clips...")
            
            # Concatenate all video clips
            final_clip = concatenate_videoclips(final_clips, method="compose")
            
            # If video is shorter than audio, loop the video
            if final_clip.duration < audio_duration:
                n_loops = int(audio_duration / final_clip.duration) + 1
                logger.info(f"Looping video {n_loops} times to match audio duration")
                final_clip = concatenate_videoclips([final_clip] * n_loops)
            
            # Trim video to match audio duration
            final_clip = final_clip.subclip(0, audio_duration)
            
            # Set audio
            final_clip = final_clip.set_audio(audio)
            
            logger.info("Writing output file... This may take a while.")
            # Write output file with progress bar
            final_clip.write_videofile(
                output_path,
                fps=fps,
                codec='libx264',
                audio_codec='aac',
                bitrate=bitrate,
                logger=None  # Disable moviepy's logger as we're using our own
            )
            
            # Clean up
            final_clip.close()
            audio.close()
            
            logger.info(f"Video successfully created at: {output_path}")
            
        except Exception as e:
            logger.error(f"Video creator: An error occurred: in {traceback.extract_tb(e.__traceback__)[0]}:\n{str(e)}") 
            raise



