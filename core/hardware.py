import cv2
import threading
import time

class CameraManager:
    def __init__(self):
        self.cap = None
        self.lock = threading.Lock()
        self.is_running = False
        self.last_frame = None

    def start(self):
        with self.lock:
            if not self.is_running:
                print("[Hardware] Starting camera...")
                self.cap = cv2.VideoCapture(0)
                self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
                self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
                self.is_running = True
                
                # Start background thread to keep buffer clear
                threading.Thread(target=self._capture_loop, daemon=True).start()

    def _capture_loop(self):
        while self.is_running:
            if self.cap and self.cap.isOpened():
                ret, frame = self.cap.read()
                if ret:
                    with self.lock:
                        self.last_frame = frame
            time.sleep(0.03)

    def stop(self):
        with self.lock:
            if self.is_running:
                print("[Hardware] Stopping camera...")
                self.is_running = False
                if self.cap:
                    self.cap.release()
                    self.cap = None
                self.last_frame = None

    def get_frame(self):
        with self.lock:
            if self.last_frame is not None:
                return self.last_frame.copy()
            return None

    def get_jpeg_bytes(self):
        frame = self.get_frame()
        if frame is not None:
            ret, jpeg = cv2.imencode('.jpg', frame)
            if ret:
                return jpeg.tobytes()
        return None

# Global singleton
camera = CameraManager()
