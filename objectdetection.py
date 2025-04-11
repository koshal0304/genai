import os
import mimetypes
import google.generativeai as genai
import time
import re
import tempfile
import concurrent.futures
from PIL import Image
from tenacity import retry, wait_fixed, stop_after_attempt
import logging

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Configuration
GEMINI_API_KEY = "AIzaSyCd-p3gedQTCUt0w4unU6udoBHVevRvdXo"
genai.configure(api_key=GEMINI_API_KEY)

def compress_image(image_path, compress_folder):
    """
    Compress an image and save it to the compress folder.
    
    Args:
        image_path (str): Path to the original image
        compress_folder (str): Folder to save compressed images
    
    Returns:
        str: Path to the compressed image
    """
    try:
        # Ensure compress folder exists
        os.makedirs(compress_folder, exist_ok=True)
        
        # Generate compressed image path
        compressed_path = os.path.join(
            compress_folder, 
            f"{os.path.splitext(os.path.basename(image_path))[0]}_compressed.jpg"
        )
        
        # Compress image
        with Image.open(image_path) as img:
            img = img.convert("RGB")
            img.save(compressed_path, format="JPEG", quality=70)
        
        return compressed_path
    except Exception as e:
        logger.error(f"Error compressing image {image_path}: {e}")
        return image_path

@retry(wait=wait_fixed(2), stop=stop_after_attempt(3))
def upload_to_gemini(path, mime_type=None):
    """
    Upload a file to Gemini with retry mechanism.
    
    Args:
        path (str): Path to the file to upload
        mime_type (str, optional): MIME type of the file
    
    Returns:
        uploaded file object or None
    """
    try:
        file = genai.upload_file(path, mime_type=mime_type)
        logger.info(f"Uploaded file '{file.display_name}' as: {file.uri}")
        return file
    except Exception as e:
        logger.error(f"Error uploading file {path}: {e}")
        return None

def parse_gemini_response(response_text):
    """
    Parse Gemini's response text into a structured dictionary with more robust explanation extraction.
    
    Args:
        response_text (str): Raw response from Gemini
    
    Returns:
        dict: Parsed results with image analysis
    """
    parsed_results = {}
    
    # Split response into image blocks, handle potential variations
    image_blocks = re.split(r'Image \d+:|^\*\*Image \d+:', response_text, flags=re.MULTILINE)
    
    for i, block in enumerate(image_blocks[1:], 1):  # Skip first empty split
        try:
            # Clean and prepare the block
            block = block.strip()
            
            # Determine answer (yes/no)
            answer = "yes" if re.search(r'\byes\b', block.lower()) else "no"
            
            # Extract explanation (more robust parsing)
            # Remove initial yes/no identifier
            block = re.sub(r'^(yes|no)[-:]\s*', '', block, flags=re.IGNORECASE)
            
            # Remove any markdown-like formatting
            block = re.sub(r'\*\*.*?\*\*', '', block)
            
            # Extract most meaningful explanation
            explanation = block.strip()
            
            # Fallback if explanation is empty
            if not explanation:
                explanation = "No detailed explanation provided for this image."
            
            # Store results
            parsed_results[f"image_{i}"] = {
                "answer": answer,
                "explanation": explanation
            }
        
        except Exception as e:
            logger.error(f"Error parsing image {i} explanation: {e}")
            parsed_results[f"image_{i}"] = {
                "answer": "unknown",
                "explanation": f"Parsing error: {str(e)}"
            }
    
    return parsed_results
def upload_image(image_path, compress_folder):
    """
    Upload an image after compression.
    
    Args:
        image_path (str): Path to the original image
        compress_folder (str): Folder to save compressed images
    
    Returns:
        uploaded file object or None
    """
    temp_compressed_path = None
    try:
        # Compress image
        temp_compressed_path = compress_image(image_path, compress_folder)
        
        # Determine MIME type
        mime_type, _ = mimetypes.guess_type(temp_compressed_path)
        mime_type = mime_type or 'application/octet-stream'
        
        # Upload to Gemini
        uploaded_file = upload_to_gemini(temp_compressed_path, mime_type)
        return uploaded_file
    except Exception as e:
        logger.error(f"Error uploading file {image_path}: {e}")
        return None
    finally:
        # Clean up temporary compressed file
        if temp_compressed_path and os.path.exists(temp_compressed_path):
            os.remove(temp_compressed_path)

def analyze_all_images(image_folder, compress_folder, max_images=100):
    """
    Analyze all images in a given folder.
    
    Args:
        image_folder (str): Folder containing images to analyze
        compress_folder (str): Folder to save compressed images
        max_images (int, optional): Maximum number of images to analyze. Defaults to 100.
    
    Returns:
        dict: Analysis results for each image
    """
    start_time = time.time()
    results = {}

    # Find image paths
    image_paths = [
        os.path.join(image_folder, f) 
        for f in os.listdir(image_folder) 
        if f.lower().endswith(('jpg', 'jpeg', 'png'))
    ][:max_images]

    if not image_paths:
        logger.warning("No valid image files found in the specified folder.")
        return results

    logger.info(f"Found {len(image_paths)} images to analyze")

    # Upload images concurrently
    files = []
    with concurrent.futures.ThreadPoolExecutor(max_workers=min(len(image_paths), 150)) as executor:
        futures = {
            executor.submit(upload_image, image_path, compress_folder): image_path 
            for image_path in image_paths
        }
        for future in concurrent.futures.as_completed(futures):
            uploaded_file = future.result()
            if uploaded_file:
                files.append(uploaded_file)

    if not files:
        logger.error("No files were successfully uploaded.")
        return results

    # Gemini analysis prompt
    prompt = """Analyze all the 100 images for active phone usage. Consider these indicators:
    - Holding a phone in hand
    - Looking at phone screen
    - Texting or scrolling
    - Taking photos/videos
    - Visible phone screen content

    For each image:
    1. Start with 'yes' or 'no'
    2. Provide detailed explanation
    3. Highlight any relevant visual elements

    Example format:
    Image 1: yes - [explanation]
    Image 2: no - [explanation] or all the 100 images """

    try:
        # Create Gemini chat session
        chat_session = genai.GenerativeModel(
            model_name="gemini-2.0-flash",
            generation_config={
                "temperature": 1,
                "top_p": 0.95,
                "top_k": 40,
                "max_output_tokens": 8192,
                "response_mime_type": "text/plain",
            }
        ).start_chat(
            history=[{
                "role": "user",
                "parts": files,
            }]
        )

        # Send analysis prompt
        response = chat_session.send_message(prompt)
        
        logger.info("Gemini API analysis complete")
        logger.debug(f"Raw response: {response.text}")

        # Parse results
        results = parse_gemini_response(response.text)

    except Exception as e:
        logger.error(f"Error during Gemini API call: {e}")

    # Log total time
    total_time = time.time() - start_time
    logger.info(f"Total time taken for image analysis: {total_time:.2f} seconds")

    return results

# Optional: Allow direct script execution for testing
def main():
    # Default folders for demonstration
    image_folder = "/Users/kabeer/genai/all_cameras_images"
    compress_folder = "/Users/kabeer/genai/compressed_images"
    
    # Run analysis
    results = analyze_all_images(image_folder, compress_folder)
    
    # Print results
    for image, data in results.items():
        print(f"{image}: {data['answer']} - {data['explanation']}")

if __name__ == "__main__":
    main()
