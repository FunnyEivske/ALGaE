import time
import requests
import pyttsx3
import json
import pyaudio
import numpy as np
import os

# Core Modules
from core.hardware import camera
from core import memory
from core import vision
import ollama

# Wake Word and STT
try:
    from openwakeword.model import Model as OWWModel
except ImportError:
    OWWModel = None

try:
    from vosk import Model as VoskModel, KaldiRecognizer
except ImportError:
    VoskModel = None
    KaldiRecognizer = None

# Constants
API_URL = "http://localhost:8080/api/state"
WAKE_WORD = "algae"

# TTS Engine
try:
    engine = pyttsx3.init()
    engine.setProperty('rate', 165)
except Exception as e:
    print(f"[Warning] Klarte ikke å starte stemmemotoren (pyttsx3/espeak): {e}")
    engine = None

def set_state(state, show_camera=None):
    payload = {"state": state}
    if show_camera is not None:
        payload["show_camera"] = show_camera
    try:
        requests.post(API_URL, json=payload, timeout=1)
    except:
        pass

def init_vosk():
    if VoskModel is None:
        return None
    model_path = os.path.expanduser("~/ALGaE/vosk-model")
    if not os.path.exists(model_path):
        print("[Warning] Vosk model not found at ~/ALGaE/vosk-model.")
        print("For 100% local speech-to-text, please download a lightweight Vosk model and place it there.")
        return None
    return VoskModel(model_path)

def generate_response(prompt, use_vision=False):
    # Retrieve recent memory context
    messages = memory.get_history(limit=5)
    
    # Add the current prompt
    messages.append({'role': 'user', 'content': prompt})
    
    model_name = 'gemma4-vision' if use_vision else 'gemma4'
    print(f"[Brain] Sending to {model_name}...")
    
    if use_vision:
        image_b64 = vision.capture_frame_b64()
        if image_b64:
            messages[-1]['images'] = [image_b64]

    try:
        response = ollama.chat(model=model_name, messages=messages)
        ai_reply = response['message']['content']
        
        # Save both to memory
        memory.add_message('user', prompt)
        memory.add_message('assistant', ai_reply)
        
        return ai_reply
    except Exception as e:
        print(f"[Error] {e}")
        return "I am having trouble connecting to my local brain."

def main_loop():
    print("Starting ALGaE Brain...", flush=True)
    set_state("idle", False)
    
    try:
        p = pyaudio.PyAudio()
        stream = p.open(format=pyaudio.paInt16, channels=1, rate=16000, input=True, frames_per_buffer=1280)
    except Exception as e:
        print(f"[Fatal Error] Klarte ikke å finne en fungerende mikrofon: {e}", flush=True)
        print("Sørg for at en mikrofon er koblet til! Avslutter AI-modulen.", flush=True)
        import sys
        sys.exit(1)
    
    print("Loading OpenWakeWord...")
    oww_model = None
    if OWWModel:
        try:
            oww_model = OWWModel(inference_framework="onnx")
            print("Loaded openwakeword. Note: 'algae' specific model required for exact match.")
        except Exception as e:
            print(f"[Warning] Wake word model failed to load: {e}")

    print("Loading Vosk...")
    vosk_model = init_vosk()
    recognizer = KaldiRecognizer(vosk_model, 16000) if vosk_model else None

    while True:
        try:
            # --- STAGE 1: Wake Word ---
            set_state("idle", False)
            print("Listening for wake word...")
            
            wake_detected = False
            while not wake_detected:
                data = stream.read(1280, exception_on_overflow=False)
                
                if oww_model:
                    audio_data = np.frombuffer(data, dtype=np.int16)
                    prediction = oww_model.predict(audio_data)
                    for mdl, score in prediction.items():
                        if score > 0.5:  # Threshold
                            wake_detected = True
                            break
                else:
                    # Generic input fallback
                    if input("Press Enter to simulate Wake Word (or type 'q' to quit): ") == 'q':
                        return
                    wake_detected = True

            print("[Event] Wake word detected!")
            set_state("listening")
            engine.say("Yes Eivind?")
            engine.runAndWait()
            
            # --- STAGE 2: Command Transcription ---
            print("Awaiting command...")
            user_prompt = ""
            
            if recognizer:
                recognizer.Reset()
                command_detected = False
                silence_frames = 0
                
                while not command_detected:
                    data = stream.read(4000, exception_on_overflow=False)
                    if recognizer.AcceptWaveform(data):
                        res = json.loads(recognizer.Result())
                        text = res.get('text', '')
                        if text:
                            user_prompt = text
                            command_detected = True
                    else:
                        partial = json.loads(recognizer.PartialResult())
                        if not partial.get("partial", ""):
                            silence_frames += 1
                        else:
                            silence_frames = 0
                        
                        # Break after ~3 seconds of silence
                        if silence_frames > 50:
                            break
            else:
                user_prompt = input("Enter command manually (Vosk not loaded): ")

            if user_prompt:
                print(f"[Heard] {user_prompt}")
                set_state("thinking")
                
                needs_camera = "see" in user_prompt or "look" in user_prompt
                if needs_camera:
                    set_state("watching", show_camera=True)
                    camera.start()
                    time.sleep(1) # Let camera warmup/auto-expose
                    
                response = generate_response(user_prompt, use_vision=needs_camera)
                
                if needs_camera:
                    camera.stop()
                    
                set_state("speaking", show_camera=False)
                print(f"[Algae] {response}")
                engine.say(response)
                engine.runAndWait()
                
        except KeyboardInterrupt:
            break
        except Exception as e:
            print(f"[Loop Error] {e}")

    stream.stop_stream()
    stream.close()
    p.terminate()

if __name__ == "__main__":
    main_loop()