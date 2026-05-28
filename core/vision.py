import base64
import ollama
from core.hardware import camera

def capture_frame_b64():
    """
    Grabs a single frame from the camera via the hardware manager 
    and converts it to base64 for Ollama.
    """
    frame = camera.get_frame()
    if frame is not None:
        import cv2
        _, buffer = cv2.imencode('.jpg', frame)
        jpg_as_text = base64.b64encode(buffer).decode('utf-8')
        return jpg_as_text
    return None

def analyze_image_with_ollama(prompt="Describe what you see."):
    """Sends the camera frame to a local vision model via Ollama."""
    
    # Grab image
    image_b64 = capture_frame_b64()
    if not image_b64:
        return "I'm sorry, I cannot access the camera right now."

    try:
        response = ollama.chat(model='gemma4-vision', messages=[
            {
                'role': 'user',
                'content': prompt,
                'images': [image_b64]
            }
        ])
        return response['message']['content']
    except Exception as e:
        return f"Error communicating with local vision model: {e}"