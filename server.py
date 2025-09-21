import http.server
import socketserver
import os
import json
import urllib.parse

class MyHTTPRequestHandler(http.server.SimpleHTTPRequestHandler):
    def end_headers(self):
        self.send_header('Cache-Control', 'no-cache, no-store, must-revalidate')
        self.send_header('Pragma', 'no-cache')
        self.send_header('Expires', '0')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        super().end_headers()
    
    def do_OPTIONS(self):
        self.send_response(200)
        self.end_headers()
    
    def do_GET(self):
        if self.path == '/api/stats':
            try:
                with open('data.json', 'r') as f:
                    data = json.load(f)
                self.send_response(200)
                self.send_header('Content-type', 'application/json')
                self.end_headers()
                self.wfile.write(json.dumps(data).encode())
            except FileNotFoundError:
                # Create default data file if it doesn't exist
                default_data = {
                    "instagram_followers": 14244,
                    "engagement_rate": 5.12
                }
                with open('data.json', 'w') as f:
                    json.dump(default_data, f, indent=2)
                self.send_response(200)
                self.send_header('Content-type', 'application/json')
                self.end_headers()
                self.wfile.write(json.dumps(default_data).encode())
        else:
            super().do_GET()
    
    def do_POST(self):
        if self.path == '/api/stats':
            content_length = int(self.headers['Content-Length'])
            post_data = self.rfile.read(content_length)
            try:
                data = json.loads(post_data.decode())
                with open('data.json', 'w') as f:
                    json.dump(data, f, indent=2)
                self.send_response(200)
                self.send_header('Content-type', 'application/json')
                self.end_headers()
                self.wfile.write(json.dumps({'success': True}).encode())
            except Exception as e:
                self.send_response(500)
                self.end_headers()
                self.wfile.write(f'Error: {str(e)}'.encode())
        else:
            self.send_response(404)
            self.end_headers()

# Get port from environment variable (Render sets this automatically)
PORT = int(os.environ.get('PORT', 8000))

# Set working directory to current directory (for Render deployment)
current_dir = os.path.dirname(os.path.abspath(__file__))
os.chdir(current_dir)

with socketserver.TCPServer(("", PORT), MyHTTPRequestHandler) as httpd:
    print(f"Server running on port {PORT}")
    httpd.serve_forever()