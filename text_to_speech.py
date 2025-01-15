import pyttsx3
from gtts import gTTS
import os
from deep_translator import GoogleTranslator
from langdetect import detect
import soundfile as sf
import numpy as np
from datetime import datetime

class TextToSpeechGenerator:
    def __init__(self):
        # Initialize pyttsx3 engine
        self.engine = pyttsx3.init()
        self.voices = self.engine.getProperty('voices')
        
    def detect_language(self, text):
        """Detect the language of input text"""
        try:
            return detect(text)
        except:
            # Default to English if detection fails
            return 'en'

    def generate_audio_pyttsx3(self, text, voice_gender='male', output_path='output.wav'):
        """
        Generate audio using pyttsx3 (better voice gender control, works offline)
        
        Parameters:
        text (str): Text to convert to speech
        voice_gender (str): 'male' or 'female'
        output_path (str): Path to save the WAV file
        """
        try:
            # Set voice gender
            voice_index = 0 if voice_gender.lower() == 'male' else 1
            if voice_index < len(self.voices):
                self.engine.setProperty('voice', self.voices[voice_index].id)
            
            # Set other properties
            self.engine.setProperty('rate', 150)    # Speed of speech
            self.engine.setProperty('volume', 0.9)  # Volume (0 to 1)
            
            # Generate and save audio
            print(f"Generating audio using pyttsx3...")
            self.engine.save_to_file(text, output_path)
            self.engine.runAndWait()
            
            return True, output_path
            
        except Exception as e:
            print(f"Error in pyttsx3 generation: {str(e)}")
            return False, str(e)

    def generate_audio_gtts(self, text, language='en', output_path='output.wav'):
        """
        Generate audio using gTTS (better language support, requires internet)
        
        Parameters:
        text (str): Text to convert to speech
        language (str): Language code ('en' for English, 'hi' for Hindi)
        output_path (str): Path to save the WAV file
        """
        try:
            # Create gTTS object
            print(f"Generating audio using gTTS...")
            tts = gTTS(text=text, lang=language, slow=False)
            
            # Save as MP3 first (gTTS only supports MP3)
            temp_mp3 = 'temp_output.mp3'
            tts.save(temp_mp3)
            
            # Convert MP3 to WAV using soundfile
            data, samplerate = sf.read(temp_mp3)
            sf.write(output_path, data, samplerate)
            
            # Remove temporary MP3 file
            os.remove(temp_mp3)
            
            return True, output_path
            
        except Exception as e:
            print(f"Error in gTTS generation: {str(e)}")
            return False, str(e)

    def generate_speech(self, text, voice_gender='male', output_path=None, force_language=None):
        """
        Main function to generate speech from text
        
        Parameters:
        text (str): Input text
        voice_gender (str): 'male' or 'female'
        output_path (str): Custom output path (optional)
        force_language (str): Force specific language ('en' or 'hi')
        
        Returns:
        tuple: (success (bool), message (str))
        """
        try:
            # Generate default output path if not provided
            if not output_path:
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                output_path = f"speech_output_{timestamp}.wav"
            
            # Detect or use forced language
            language = force_language if force_language else self.detect_language(text)
            print(f"Detected/Forced language: {language}")
            
            # For Hindi text, use gTTS (better Hindi support)
            if language == 'hi':
                return self.generate_audio_gtts(text, 'hi', output_path)
            
            # For English, use pyttsx3 (better voice gender control)
            else:
                return self.generate_audio_pyttsx3(text, voice_gender, output_path)
                
        except Exception as e:
            return False, f"Error in speech generation: {str(e)}"

def main():
    # Example usage
    generator = TextToSpeechGenerator()
    
    # Example texts
    english_text = "Hello! This is a test message in English."
    hindi_text = "नमस्ते! यह हिंदी में एक परीक्षण संदेश है।"
    
    # Generate speech for English text with male voice
    print("\nGenerating English speech with male voice...")
    success, result = generator.generate_speech(
        english_text,
        voice_gender='male',
        output_path='english_male.wav'
    )
    print(f"Success: {success}, Result: {result}")
    
    # Generate speech for English text with female voice
    print("\nGenerating English speech with female voice...")
    success, result = generator.generate_speech(
        english_text,
        voice_gender='female',
        output_path='english_female.wav'
    )
    print(f"Success: {success}, Result: {result}")
    
    # Generate speech for Hindi text
    print("\nGenerating Hindi speech...")
    success, result = generator.generate_speech(
        hindi_text,
        output_path='hindi.wav',
        force_language='hi'
    )
    print(f"Success: {success}, Result: {result}")

if __name__ == "__main__":
    main()