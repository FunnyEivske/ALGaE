import http.server
import socketserver
import json
import os
import time

# Import hardware manager
from core.hardware import camera

# Configuration
PORT = 8080
current_state = "idle"
show_camera_pip = False

class GemmaVisualizerHandler(http.server.SimpleHTTPRequestHandler):
    def do_GET(self):
        global show_camera_pip
        
        if self.path == '/':
            self.path = '/gemma-visualizer.html'
            return http.server.SimpleHTTPRequestHandler.do_GET(self)
            
        elif self.path == '/api/state':
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()
            response_data = {
                "state": current_state,
                "show_camera": show_camera_pip
            }
            self.wfile.write(json.dumps(response_data).encode('utf-8'))
            
        elif self.path.startswith('/api/camera_stream'):
            self.send_response(200)
            self.send_header('Content-type', 'multipart/x-mixed-replace; boundary=frame')
            self.end_headers()
            try:
                while True:
                    frame_bytes = camera.get_jpeg_bytes()
                    if frame_bytes:
                        self.wfile.write(b'--frame\r\n')
                        self.send_header('Content-Type', 'image/jpeg')
                        self.send_header('Content-Length', str(len(frame_bytes)))
                        self.end_headers()
                        self.wfile.write(frame_bytes)
                        self.wfile.write(b'\r\n')
                    time.sleep(0.05) 
            except Exception as e:
                pass 
                
        else:
            return http.server.SimpleHTTPRequestHandler.do_GET(self)

    def do_POST(self):
        global current_state, show_camera_pip
        
        if self.path == '/api/state':
            content_length = int(self.headers['Content-Length'])
            post_data = self.rfile.read(content_length)
            
            try:
                data = json.loads(post_data)
                if "state" in data:
                    new_state = data.get("state")
                    valid_states = ["idle", "listening", "thinking", "speaking", "watching", "updating"]
                    if new_state in valid_states:
                        current_state = new_state
                
                if "show_camera" in data:
                    show_camera_pip = bool(data.get("show_camera"))
                
                self.send_response(200)
                self.send_header('Content-type', 'application/json')
                self.end_headers()
                self.wfile.write(json.dumps({"success": True}).encode('utf-8'))
                
            except Exception as e:
                self.send_response(400)
                self.end_headers()
                self.wfile.write(b'{"error": "Invalid JSON"}')
        else:
            self.send_error(404, "Endpoint not found.")

if __name__ == "__main__":
    with socketserver.TCPServer(("", PORT), GemmaVisualizerHandler) as httpd:
        print(f"Server running on http://localhost:{PORT}")
        try:
            httpd.serve_forever()
        except KeyboardInterrupt:
            print("\nShutting down server.")