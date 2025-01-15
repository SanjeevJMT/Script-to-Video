# Script to Video Creator

An automated Python application that converts text scripts into engaging videos by generating speech, downloading relevant images, and combining them into a professional-looking video with transitions.

## Features

- **Script Processing**
  - Supports both English and Hindi scripts
  - Automatic keyword extraction for relevant image selection
  - Male and female voice options

- **Image Management**
  - Automatic high-quality image download from multiple sources (Google Images and Unsplash)
  - Portrait orientation support
  - Smart keyword-based image selection
  - Metadata tracking for downloaded images

- **Audio Generation**
  - Text-to-speech conversion with multiple voice options
  - Language detection and support
  - High-quality WAV audio output

- **Video Creation**
  - Smooth transitions between images
  - Customizable resolution and quality settings
  - Automatic timing based on audio duration
  - Professional output in MP4 format

## Prerequisites

### System Requirements
- Python 3.7 or higher
- Sufficient disk space for temporary files
- Internet connection for image downloads and API access

### Required Python Packages
```bash
pip install -r requirements.txt
```

Or install individually:
```bash
pip install moviepy
pip install google_images_download
pip install pyttsx3
pip install gTTS
pip install nltk
pip install spacy
pip install tqdm
pip install requests
```

### Additional Setup
```bash
# Download required NLTK data
python -m nltk.downloader punkt

# Download SpaCy English model
python -m spacy download en_core_web_sm
```

## Configuration

Create a `config.json` file with your settings:

```json
{
    "unsplash_api_key": "YOUR_UNSPLASH_API_KEY",
    "output_folder": "output",
    "temp_folder": "temp",
    "image_duration": 5,
    "video_resolution": [1080, 1920],
    "image_quality": "high",
    "transition_duration": 1,
    "keep_temp_files": false
}
```

### Configuration Options

| Option | Description | Default |
|--------|-------------|---------|
| unsplash_api_key | Your Unsplash API key for image downloads | "" |
| output_folder | Directory for final video output | "output" |
| temp_folder | Directory for temporary files | "temp" |
| image_duration | Duration each image shows (seconds) | 5 |
| video_resolution | Video dimensions [width, height] | [1080, 1920] |
| image_quality | Image download quality | "high" |
| transition_duration | Duration of transitions (seconds) | 1 |
| keep_temp_files | Whether to keep temporary files | false |

## Usage

### Command Line Interface

1. Basic usage with direct script text:
```bash
python app.py --script "Your script text here" --voice male --language en
```

2. Using a script file:
```bash
python app.py --script path/to/script.txt --voice female --language hi
```

### Command Line Options

| Option | Description | Values |
|--------|-------------|--------|
| --script | Script text or file path | String |
| --voice | Voice gender for narration | male, female |
| --language | Script language | en, hi |
| --config | Path to config file | String |

### Python Module Usage

```python
from script_to_video import ScriptToVideo

# Initialize the creator
creator = ScriptToVideo('config.json')

# Create video
output_video = creator.create_video(
    script="Your script text here",
    voice_gender="male",
    language="en"
)
```

## Project Structure

```
project/
├── app.py
├── config.json
├── requirements.txt
├── README.md
├── images/
│   └── metadata/
├── output/
├── temp/
│   ├── audio/
│   └── images/
└── logs/
```

## Output

The application generates:
- MP4 video file in the specified output folder
- Detailed logs of the creation process
- Image metadata (optional)

## Error Handling

The application includes comprehensive error handling and logging:
- All errors are logged to the logs directory
- Progress information is displayed in the console
- Detailed error messages for troubleshooting

## Limitations

- Requires active internet connection for image downloads
- Google Images download may be subject to usage limits
- Speech generation quality depends on the selected engine
- Processing time varies based on script length and image count

## Contributing

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## License

This project is NOT licensed.

## Acknowledgments

- Google Images Download library
- Unsplash API for high-quality images
- MoviePy for video creation
- gTTS and pyttsx3 for text-to-speech conversion

## Support

For support and questions, please open an issue in the GitHub repository or contact the maintainers.

## Version History

- 1.0.0
  - Initial Release
  - Basic video creation functionality
  - English and Hindi language support