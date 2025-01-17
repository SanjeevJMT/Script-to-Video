import os
import json
from moviepy import ImageClip, AudioFileClip, TextClip, CompositeVideoClip, concatenate_videoclips
from PIL import Image


def create_video(image_folder, audio_file, caption_file, output_folder):
    # Load audio file
    audio = AudioFileClip(audio_file)
    
    # Load captions from JSON file
    with open(caption_file, 'r') as f:
        captions = json.load(f)
    
    # Create a list to hold all the video clips
    clips = []

    # Get a list of all image files
    image_files = sorted([os.path.join(image_folder, file) for file in os.listdir(image_folder) if file.endswith('.jpg')])

    # Check if the number of images and captions match
    if len(image_files) != len(captions):
        raise ValueError("The number of images and captions do not match.")

    for image_file, caption in zip(image_files, captions):
        # Read image
        img_clip = ImageClip(image_file).with_duration(caption['end'] - caption['start']).resized(height=1080).with_position(("center", "top"))

        # Create caption clip
        caption_clip = TextClip(caption['text'], font_size=24, color='black', bg_color='white', size=(1080, 240), method='caption').with_duration(caption['end'] - caption['start']).with_position(("center", "bottom"))

        # Create a white background image
        white_background = Image.new('RGB', (1080, 1920), color='white')
        white_background.save("white_background.jpg")

        # Create a white background
        background = ImageClip("white_background.jpg").set_duration(caption['end'] - caption['start']).set_position(("center", "center"))

        # Composite image, caption, and background
        video = CompositeVideoClip([background, img_clip, caption_clip], size=(1080, 1920)).set_duration(caption['end'] - caption['start']).set_start(caption['start'])

        # Add the video clip to the list
        clips.append(video)

    # Concatenate all the clips into one video
    final_video = concatenate_videoclips(clips)

    # Set audio
    final_video = final_video.set_audio(audio)

    # Write the final video to file
    output_path = os.path.join(output_folder, "output_video.mp4")
    final_video.write_videofile(output_path, codec='libx264', fps=24)

# Example usage
image_folder = "temp/images"
audio_file = "temp/audio/audio.wav"
caption_file = "temp/caption/captions.json"
output_folder = "output"

create_video(image_folder, audio_file, caption_file, output_folder)