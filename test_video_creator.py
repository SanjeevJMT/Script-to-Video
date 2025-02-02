import unittest
from video_creator import VideoCreator
from unittest.mock import patch, MagicMock
import os

class TestVideoCreator(unittest.TestCase):

    @patch('video_creator.Image.open')
    @patch('video_creator.glob.glob')
    @patch('video_creator.AudioFileClip')
    def test_create_image_video(self, mock_audiofileclip, mock_glob, mock_image_open):
        # Setup
        mock_audiofileclip.return_value.duration = 120  # Mock audio duration
        mock_glob.return_value = ['image1.jpg', 'image2.jpg']  # Mock image files
        mock_image_open.side_effect = [MagicMock(), IOError]  # First image opens, second raises IOError

        video_creator = VideoCreator()
        
        # Mock methods to avoid actual file operations
        video_creator.parse_srt = MagicMock(return_value=[])
        video_creator.create_text_clips = MagicMock(return_value=[])
        
        # Create a temporary directory for output
        temp_output_path = 'temp_output.mp4'
        
        # Call the method
        video_creator.create_image_video(
            image_folder='test_images',
            audio_path='test_audio.wav',
            output_path=temp_output_path,
            subtitles_path='test_subtitles.srt'
        )
        
        # Assertions
        mock_audiofileclip.assert_called_once_with('test_audio.wav')
        mock_glob.assert_called()
        self.assertEqual(mock_image_open.call_count, 2)  # Ensure both images were attempted to be opened
        mock_image_open.assert_any_call('image1.jpg')
        mock_image_open.assert_any_call('image2.jpg')
        
        # Clean up
        if os.path.exists(temp_output_path):
            os.remove(temp_output_path)

if __name__ == '__main__':
    unittest.main()