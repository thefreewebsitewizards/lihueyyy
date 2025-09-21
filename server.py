#!/usr/bin/env python3
import http.server
import socketserver
import json
import os
import urllib.parse
from datetime import datetime

class MetricsHandler(http.server.SimpleHTTPRequestHandler):
    def do_GET(self):
        print(f"GET request for: {self.path}")  # Debug logging
        if self.path == '/api/metrics':
            self.handle_get_metrics()
        elif self.path.startswith('/api/'):
            # Handle any other API routes with 404
            self.send_error(404, "API endpoint not found")
        else:
            # Serve static files
            super().do_GET()
    
    def do_POST(self):
        print(f"POST request for: {self.path}")  # Debug logging
        if self.path == '/api/metrics':
            self.handle_update_metrics()
        else:
            self.send_error(404)
    
    def handle_get_metrics(self):
        print("Handling GET /api/metrics")  # Debug logging
        try:
            with open('metrics.json', 'r') as f:
                metrics = json.load(f)
            
            print(f"Returning metrics: {metrics}")  # Debug logging
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()
            self.wfile.write(json.dumps(metrics).encode())
        except FileNotFoundError:
            print("metrics.json not found, returning defaults")  # Debug logging
            # Return default values if file doesn't exist
            default_metrics = {
                "instagramFollowers": "14244",
                "instagramEngagement": "5.12",
                "lastUpdated": datetime.now().isoformat()
            }
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()
            self.wfile.write(json.dumps(default_metrics).encode())
        except Exception as e:
            print(f"Error in handle_get_metrics: {e}")  # Debug logging
            self.send_error(500, str(e))
    
    def handle_update_metrics(self):
        try:
            content_length = int(self.headers['Content-Length'])
            post_data = self.rfile.read(content_length)
            data = json.loads(post_data.decode('utf-8'))
            
            # Update metrics with timestamp
            metrics = {
                "instagramFollowers": str(data.get('instagramFollowers', '14244')),
                "instagramEngagement": str(data.get('instagramEngagement', '5.12')),
                "lastUpdated": datetime.now().isoformat()
            }
            
            with open('metrics.json', 'w') as f:
                json.dump(metrics, f, indent=2)
            
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.send_header('Access-Control-Allow-Methods', 'POST, GET, OPTIONS')
            self.send_header('Access-Control-Allow-Headers', 'Content-Type')
            self.end_headers()
            self.wfile.write(json.dumps({"status": "success", "metrics": metrics}).encode())
        except Exception as e:
            self.send_error(500, str(e))
    
    def do_OPTIONS(self):
        # Handle CORS preflight requests
        self.send_response(200)
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'POST, GET, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        self.end_headers()

if __name__ == "__main__":
    PORT = int(os.environ.get('PORT', 8000))
    with socketserver.TCPServer(("", PORT), MetricsHandler) as httpd:
        print(f"Server running at http://localhost:{PORT}")
        httpd.serve_forever()