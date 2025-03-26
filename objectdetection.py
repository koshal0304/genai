import os
import mimetypes
import google.generativeai as genai
import time
import re
import tempfile
import concurrent.futures
from PIL import Image
from tenacity import retry, wait_fixed, stop_after_attempt


genai.configure(api_key="AIzaSyCd-p3gedQTCUt0w4unU6udoBHVevRvdXo")

##API_KEY = "AIzaSyCd-p3gedQTCUt0w4unU6udoBHVevRvdXo"


def compress_image(image_path, compress_folder):
    try:
        if not os.path.exists(compress_folder):
            os.makedirs(compress_folder)  
            
        compressed_path = os.path.join(compress_folder, f"{os.path.basename(image_path)}_compressed.jpg")
        with Image.open(image_path) as img:
            img = img.convert("RGB")
            img.save(compressed_path, format="JPEG", quality=10)
        
        return compressed_path
    except Exception as e:
        print(f"Error compressing image {image_path}: {e}")
        return image_path


@retry(wait=wait_fixed(2), stop=stop_after_attempt(3))
def upload_to_gemini(path, mime_type=None):
    try:
        # Simulate the actual upload to Gemini (replace with real API call)
        file = genai.upload_file(path, mime_type=mime_type)  # Ensure API setup
        print(f"Uploaded file '{file.display_name}' as: {file.uri}")
        return file
    except Exception as e:
        print(f"Error uploading file {path}: {e}")
        return None


def parse_gemini_response(response_text):
    image_explanations = response_text.split("**Image ")
    parsed_results = {}

    for i, image_exp in enumerate(image_explanations):
        if image_exp.strip():
            match = re.match(r"(\d+):", image_exp.strip())  
            if match:
                image_number = match.group(1)
                parts = image_exp.split("\n", 1)
                if len(parts) >= 2:
                    answer_line = parts[0].strip()
                    explanation_text = parts[1].strip()
                    answer = "yes" if "yes" in answer_line.lower() else "no"
                    explanation_text = re.sub(r"\*\*.*\*\*", "", explanation_text).strip()

                    # Skip entries with empty explanations
                    if explanation_text:
                        parsed_results[f"image_{image_number}"] = {
                            "answer": answer,
                            "explanation": explanation_text
                        }
    return parsed_results


def upload_image(image_path, compress_folder):
    temp_compressed_path = None
    try:
        temp_compressed_path = compress_image(image_path, compress_folder)
        mime_type, _ = mimetypes.guess_type(temp_compressed_path)
        if mime_type is None:
            mime_type = 'application/octet-stream'
        uploaded_file = upload_to_gemini(temp_compressed_path, mime_type)
        return uploaded_file
    except Exception as e:
        print(f"Error uploading file {image_path}: {e}")
        return None
    finally:
        
        if temp_compressed_path and os.path.exists(temp_compressed_path):
            os.remove(temp_compressed_path)


def analyze_all_images(image_folder, compress_folder):
    start_time = time.time()
    results = {}

    
    image_paths = [os.path.join(image_folder, f) for f in os.listdir(image_folder) if f.lower().endswith(('jpg', 'jpeg', 'png'))]
    if not image_paths:
        print("No valid image files found in the specified folder.")
        return results

    
    print("Uploading images...")
    files = []
    with concurrent.futures.ThreadPoolExecutor(max_workers=150) as executor:
        futures = {executor.submit(upload_image, image_path, compress_folder): image_path for image_path in image_paths}
        for future in concurrent.futures.as_completed(futures):
            uploaded_file = future.result()
            if uploaded_file:
                files.append(uploaded_file)

    if not files:
        print("No files were successfully uploaded.")
        return results

    
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

    Example format like the following:
    Image 1: yes - [explanation]
    Image 2: no - [explanation] for all the 100 images """

    try:
        
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

        # Send message to Gemini API with the prompt
        response = chat_session.send_message(prompt)
        
        
        print("Raw response from Gemini API:")
        print(response.text)

        
        results = parse_gemini_response(response.text)

    except Exception as e:
        print(f"Error during Gemini API call: {e}")

    total_time = time.time() - start_time
    print(f"Total time taken for analyze_all_images: {total_time:.2f} seconds")
    return results

# Example usage:
image_folder = "/Users/kabeer/genai/all_cameras_images"  
compress_folder = "/Users/kabeer/genai/compressed_images" 
results = analyze_all_images(image_folder, compress_folder)
print(results)