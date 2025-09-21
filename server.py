#!/usr/bin/env python3
import http.server
import socketserver
import json
import os
import urllib.parse
from datetime import datetime

class MetricsHandler(http.server.SimpleHTTPRequestHandler):
    def do_GET(self):
        if self.path == '/api/metrics':
            self.handle_get_metrics()
        else:
            # Serve static files
            super().do_GET()
    
    def do_POST(self):
        if self.path == '/api/metrics':
            self.handle_update_metrics()
        else:
            self.send_error(404)
    
    def handle_get_metrics(self):
        try:
            with open('metrics.json', 'r') as f:
                metrics = json.load(f)
            
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()
            self.wfile.write(json.dumps(metrics).encode())
        except FileNotFoundError:
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