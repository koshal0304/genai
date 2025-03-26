# RTSP Image Analyzer 📸📱

A Python solution for monitoring RTSP streams and detecting phone usage using Google's Gemini AI, featuring both CLI and Streamlit web interface.

![Workflow Diagram](https://via.placeholder.com/800x400.png?text=RTSP+→+Image+Capture+→+AI+Analysis+→+Visualization)

## Project Structure

```bash
project-root/
├── objectdetection.py          # Main analysis module
├── downloadimages.py           # RTSP image downloader
├── image_analysis_frontend.py  # Streamlit web interface
├── all_cameras_images/         # Stores captured images
└── compressed_images/          # Temporary compressed images

