import cv2
import time
import os
import requests
import threading

def download_images_from_camera(rtsp_url, save_directory, frame_interval=125, duration_seconds=300):
    if not os.path.exists(save_directory):
        os.makedirs(save_directory)

    cap = None  # Initialize cap here

    try:
        response = requests.get(rtsp_url, stream=True, timeout=10)
        response.raise_for_status()

        cap = cv2.VideoCapture(rtsp_url)  # Now cap is defined

        if not cap.isOpened():
            print(f"Error: Could not open stream. URL: {rtsp_url}")
            return

        start_time = time.time()
        end_time = start_time + duration_seconds
        frame_count = 0
        image_count = 0

        while time.time() < end_time:
            ret, frame = cap.read()

            if not ret:
                print(f"Error: Could not read frame from {rtsp_url}. Check camera connection.")
                break

            frame_count += 1

            if frame_count % frame_interval == 0:
                timestamp = time.strftime("%Y%m%d_%H%M%S")
                filename = os.path.join(save_directory, f"camera_{rtsp_url.split('src=')[1].split('&')[0]}_image_{timestamp}.jpg")
                cv2.imwrite(filename, frame)
                print(f"Downloaded image: {filename} from {rtsp_url}")

                image_count += 1

    except requests.exceptions.RequestException as e:
        print(f"Error accessing stream URL {rtsp_url}: {e}")
        return

    finally:  # Ensure cap is released even if an exception happens
        if cap is not None:
            cap.release()  # Release the capture object in the finally block

    print(f"Finished downloading images from {rtsp_url}.")  # Print this even if no images were downloaded


def process_rtsp_links(rtsp_urls, save_directory="all_cameras_images", frame_interval=125, duration_seconds=300):
    if not os.path.exists(save_directory):  # Create the main directory if it doesn't exist
        os.makedirs(save_directory)
    threads = []
    for rtsp_url in rtsp_urls:
        thread = threading.Thread(target=download_images_from_camera, args=(rtsp_url, save_directory, frame_interval, duration_seconds))
        threads.append(thread)
        thread.start()

    for thread in threads:
        thread.join()

    print("All RTSP downloads complete.")


if __name__ == "__main__":
    rtsp_urls = [
        "https://vip-hls.backend-ripik.com/api/stream.m3u8?src=3&mp4",
        "https://vip-hls.backend-ripik.com/api/stream.m3u8?src=2&mp4",
        "https://vip-hls.backend-ripik.com/api/stream.m3u8?src=1&mp4",
        "https://vip-hls.backend-ripik.com/api/stream.m3u8?src=6&mp4",
        "https://vip-hls.backend-ripik.com/api/stream.m3u8?src=4&mp4",
    ]

    process_rtsp_links(rtsp_urls)