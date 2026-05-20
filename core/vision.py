 
import cv2
import requests
import base64
import os

def capture_frame():
    """
    Grabs a single frame from the camera to send to Gemma Vision.
    Because server.py might be hogging the camera, in a real setup, 
    you would either read from /dev/video0 here, OR pull a snapshot 
    directly from the server.py stream!
    """
    # Try to grab a frame directly from webcam
    cap = cv2.VideoCapture(0)
    ret, frame = cap.read()
    cap.release()
    
    if ret:
        # Convert to base64 for Ollama
        _, buffer = cv2.imencode('.jpg', frame)
        jpg_as_text = base64.b64encode(buffer).decode('utf-8')
        return jpg_as_text
    return None

def analyze_image_with_ollama(prompt="Describe what you see."):
    """Sends the camera frame to a local vision model via Ollama."""
    
    # 1. Grab image
    image_b64 = capture_frame()
    if not image_b64:
        return "I'm sorry, I cannot access the camera right now."

    # 2. Setup Ollama payload (Assuming a model like llava or gemma-vision exists locally)
    payload = {
        "model": "llava", # Change this to your actual quantized vision model
        "prompt": prompt,
        "images": [image_b64],
        "stream": False
    }

    try:
        response = requests.post("http://localhost:11434/api/generate", json=payload)
        response_data = response.json()
        return response_data.get("response", "I could not analyze the image.")
    except Exception as e:
        return f"Error communicating with local vision model: {e}"