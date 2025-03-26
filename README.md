# RTSP Image Analyzer

A Python project that downloads images from RTSP streams and analyzes them for phone usage detection using Google's Gemini AI.

## Project Structure
project-folder/
├── analyze_images.py # Main script for object detection and analysis
├── download_images.py # Script to download images from RTSP links
├── all_cameras_images/ # Folder where downloaded images are stored
└── compressed_images/ # Folder for compressed versions of images


## Features

- Downloads images from multiple RTSP streams simultaneously
- Compresses images for efficient processing
- Uses Google Gemini AI to analyze images for phone usage
- Provides detailed analysis with explanations
- Multi-threaded processing for better performance

## Prerequisites

- Python 3.7+
- Google Gemini API key
- Required Python packages (install via `pip install -r requirements.txt`)

## Installation

1. Clone this repository:
   ```bash
   git clone https://github.com/yourusername/rtsp-image-analyzer.git
   cd rtsp-image-analyzer

2. Install the required packages:

    pip install -r requirements.txt
   
4. Set up your Google Gemini API key:

   Replace AIzaSyCd-p3gedQTCUt0w4unU6udoBHVevRvdXo in analyze_images.py with your actual API key

   Or set it as an environment variable:
 
      export GEMINI_API_KEY="your-api-key-here"
## Usage
1. Download Images from RTSP Streams
   Run the download script:
   python download_images.py

This will:
 Create an all_cameras_images folder
 Download images from all configured RTSP streams
 Save images with timestamps in their filenames

2. Analyze Images for Phone Usage
 Run the analysis script:
 python analyze_images.py

This will:
  Compress images and save them in compressed_images folder
  Upload images to Gemini AI for analysis
  Return detection results with explanations
  Print the analysis results to console

## Configuration
  You can modify these parameters in the scripts:
  In download_images.py:
     rtsp_urls: List of RTSP streams to monitor
     frame_interval: Number of frames between captures (default: 125)
     duration_seconds: Total duration to capture images (default: 300 seconds)

  In analyze_images.py:
     image_folder: Path to folder containing images to analyze
     compress_folder: Path to folder for compressed images
     prompt: Customize the analysis prompt for Gemini AI

## Output Format
  The analysis script returns results in this format:
        {
      "image_1": {
        "answer": "yes",
        "explanation": "Person is holding a phone in their right hand..."
      },
      "image_2": {
        "answer": "no",
        "explanation": "No visible phone usage detected..."
      }
    }

## Performance Notes
   The script uses multi-threading for faster image processing
   Images are compressed to reduce upload time
   Gemini API has rate limits - adjust max_workers accordingly

