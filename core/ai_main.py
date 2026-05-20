import time
import requests
import ollama
import speech_recognition as sr
import pyttsx3

# Constants for the Visualizer API
API_URL = "http://localhost:8080/api/state"
WAKE_WORD = "algae"

# Initialize Text-to-Speech Engine
engine = pyttsx3.init()
engine.setProperty('rate', 165) # Speaking speed
# To change voice to female or different accent, you can configure engine.setProperty('voice', voices[x].id)

def set_state(state, show_camera=None):
    """Tells the visualizer to change its animation state."""
    payload = {"state": state}
    if show_camera is not None:
        payload["show_camera"] = show_camera
        
    try:
        requests.post(API_URL, json=payload)
    except Exception as e:
        print(f"[Error] Could not connect to visualizer: {e}")

def listen_to_mic(recognizer, mic, prompt="Listening..."):
    """Listens to the physical microphone and converts speech to text."""
    with mic as source:
        recognizer.adjust_for_ambient_noise(source, duration=0.5)
        print(f"[Mic] {prompt}")
        try:
            audio = recognizer.listen(source, timeout=5, phrase_time_limit=10)
            text = recognizer.recognize_google(audio)
            print(f"[Heard] {text}")
            return text.lower()
        except sr.WaitTimeoutError:
            return ""
        except sr.UnknownValueError:
            return ""
        except sr.RequestError as e:
            print(f"[Error] Speech recognition service error: {e}")
            return ""

def generate_response(prompt, use_vision=False):
    """Calls the real local Ollama Gemma 4 model."""
    model_name = 'gemma4-vision' if use_vision else 'gemma4'
    print(f"[Brain] Sending to {model_name}: {prompt}")
    
    try:
        # In a fully fleshed out vision scenario, you would grab a frame using cv2 here 
        # and attach it to the images array.
        response = ollama.chat(model=model_name, messages=[
            {
                'role': 'user',
                'content': prompt,
            },
        ])
        return response['message']['content']
    except Exception as e:
        print(f"[Error] Failed to connect to Ollama: {e}")
        return "System error. My connection to the local brain failed."

def main_loop():
    """The real main brain loop for ALGaE."""
    print("Starting ALGaE Brain...")
    set_state("idle", False)
    
    recognizer = sr.Recognizer()
    mic = sr.Microphone()
    
    while True:
        # 1. Listen for the wake word
        heard_text = listen_to_mic(recognizer, mic, "Waiting for wake word 'Algae'...")
        
        if WAKE_WORD in heard_text:
            print("[Event] Wake word detected!")
            set_state("listening")
            
            # Speak to acknowledge
            engine.say("Yes Eivind?")
            engine.runAndWait()
            
            # 2. Listen for the actual command
            user_prompt = listen_to_mic(recognizer, mic, "Awaiting command...")
            
            if user_prompt:
                # 3. Process the request (Thinking)
                set_state("thinking")
                
                # Check if the user is asking it to look at something
                needs_camera = "see" in user_prompt or "look" in user_prompt
                if needs_camera:
                    set_state("watching", show_camera=True)
                    
                response = generate_response(user_prompt, use_vision=needs_camera)
                
                # 4. Deliver the response (Speaking)
                if not needs_camera:
                    set_state("speaking")
                    
                print(f"[Algae] {response}")
                
                # Actually speak the response out loud
                engine.say(response)
                engine.runAndWait()
                
            # 5. Return to normal
            set_state("idle", show_camera=False)

if __name__ == "__main__":
    try:
        main_loop()
    except KeyboardInterrupt:
        print("Shutting down ALGaE...")