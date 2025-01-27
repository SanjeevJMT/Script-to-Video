from deep_translator import GoogleTranslator
import edge_tts
import asyncio
import subprocess
from datetime import datetime

class TextToSpeechGenerator:
    
  def detect_language(self, text):
        """Detect the language of input text"""
        try:
            return detect(text)
        except:
            # Default to English if detection fails
            return 'en'          

  def generate_speech(self, text, voice_gender='male', output_path=None,subtitles_path=None, force_language=None):
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

      if not output_path:
              timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
              output_path = f"speech_output_{timestamp}.wav"
      # Read the text from prompt.txt file
      with open('prompt.txt', 'r') as file:
          text = file.read()

      # Define the edge-tts command
      command = [
          "edge-tts",
          "--voice", "hi-IN-SwaraNeural",
          "--rate", "+30%",
          "--pitch", "+10Hz",
          "--file", "prompt.txt",
          "--write-media", output_path,
          "--write-subtitles", subtitles_path
      ]

      # Run the command
      result = subprocess.run(command, capture_output=True, text=True)

      # Print the output and any errors
      print("Output:")
      print(result.stdout)
      print("Errors:")
      print(result.stderr)
      return True , result.stdout+" "+result.stderr
      
      #if no error return true and stdout else return false and stderr
          

