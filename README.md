RTSP Image Analyzer

A Python project that downloads images from RTSP streams and analyzes them for phone usage detection using Google's Gemini AI.

📂 Project Structure

project-folder/
├── objectdetection.py          # Main script for object detection and analysis
├── downloadimages.py           # Script to download images from RTSP links
├── image_analysis_frontend.py  # GUI interface (Streamlit-based)
├── all_cameras_images/         # Folder where downloaded images are stored
└── compressed_images/          # Folder for compressed versions of images

## ✨ Features

## Core Functionality

📸 RTSP Stream Image Downloading

🤖 AI-Powered Phone Usage Detection (via Google Gemini AI)

⚡ Multi-threaded Image Processing

📏 Automatic Image Compression

## Web Interface (Streamlit)

📤 Drag-and-drop Image Upload

📊 Interactive Visualizations (Pie Charts, Histograms)

📄 Results Export to JSON

🖼️ Image Previews with Analysis Overlay

## 📋 Prerequisites
Python 3.7+
Google Gemini API Key
Required Python packages 
Required Python packages (install via pip install -r requirements.txt)

## 🛠️ Installation

1. Clone the repository:
```
git clone https://github.com/yourusername/genai.git
cd genai
```
2. Install the required packages:
```
pip install -r requirements.txt
```
3. Set up your Google Gemini API key:

* Replace the placeholder in objectdetection.py with your actual API key:
```
GEMINI_API_KEY = "your-api-key-here"
```
* Or set it as an environment variable:
```
export GEMINI_API_KEY="your-api-key-here"
```

## 🚀 Usage

## 1. Download Images from RTSP Streams

Run the image downloader:
```
python downloadimages.py
```
  This will:

  * Create the all_cameras_images folder (if it doesn't exist)
  * Download images from all configured RTSP streams
  * Save images with timestamps in their filenames

## 2. Analyze Images for Phone Usage

* Run the object detection script:
```
python objectdetection.py
```
   This will:
   * Compress images and save them in the compressed_images folder
   * Upload images to Google Gemini AI for analysis
   * Return detection results with explanations
   * Print the analysis results to the console

## 3. Web Interface

* Launch the Streamlit-based GUI:
```
streamlit run image_analysis_frontend.py
```
  Workflow:
 *  📤 Upload images via drag-and-drop

* 🔍 View real-time analysis progress

* 📊 Explore interactive visualizations

* 📄 Export results as JSON

## ⚙️ Configuration

* You can modify these parameters in the scripts:

* In downloadimages.py:
```
rtsp_urls = ["rtsp://your_camera_url"]  # List of RTSP streams to monitor
frame_interval = 125                     # Frames between captures (default: 125)
duration_seconds = 300                   # Total capture duration (default: 300 seconds)
```
* In objectdetection.py:
```
image_folder = "all_cameras_images"       # Folder with images to analyze
compress_folder = "compressed_images"     # Folder for compressed images
prompt = "Detect phone usage in this image."  # Analysis prompt for Gemini AI
```

## 📊 Web Interface 
* analysis script returns results :

<img width="1290" alt="Screenshot 2025-03-26 at 3 47 35 PM" src="https://github.com/user-attachments/assets/8eff3551-70d1-4f3b-a5bc-199d488cf46e" />
<img width="1409" alt="Screenshot 2025-03-26 at 3 49 13 PM" src="https://github.com/user-attachments/assets/78056d48-e9d8-4bf8-b1ed-c5c97560b521" />
<img width="1395" alt="Screenshot 2025-03-26 at 3 49 25 PM" src="https://github.com/user-attachments/assets/67294d06-0cb5-4237-b806-569b31da610e" />


## 📈 Performance Notes

* 🧵 Uses multi-threading for faster image processing

* 📉 Images are compressed to reduce upload time

* ⚠️ Gemini API Rate Limits: Adjust max_workers in objectdetection.py for optimal performance


