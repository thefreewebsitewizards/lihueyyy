import http.server
import socketserver
import os
import json
import urllib.parse

# Hybrid storage: in-memory with file backup for true persistence
def load_stats():
    """Load stats from file if exists, otherwise use defaults"""
    # TEMPORARY DEFAULT VALUES - These are fallback values only
    # When admin updates numbers, these defaults will be overridden and cleared
    # The updated values will completely replace these temporary defaults
    default_stats = {
        "instagram_followers": int(os.environ.get('INSTAGRAM_FOLLOWERS', 14416)),  # TEMPORARY - will be replaced by admin updates
        "engagement_rate": float(os.environ.get('ENGAGEMENT_RATE', 5.12))  # TEMPORARY - will be replaced by admin updates
    }
    
    try:
        with open('data.json', 'r') as f:
            stored_data = json.load(f)
            # If data.json has content, it completely replaces the temporary defaults
            if stored_data:
                return stored_data
            else:
                # If data.json is empty, use temporary defaults and save them
                save_stats(default_stats)
                return default_stats
    except (FileNotFoundError, json.JSONDecodeError):
        # Create the file with default data
        save_stats(default_stats)
        return default_stats

def save_stats(data):
    """Save stats to file for persistence - COMPLETELY REPLACES old values"""
    # This function clears all previous data and saves only the new values
    # Old/temporary values are completely overwritten and cleared
    try:
        with open('data.json', 'w') as f:
            json.dump(data, f, indent=2)
    except Exception as e:
        print(f"Warning: Could not save to file: {e}")

# Initialize stats from file or defaults
stats_data = load_stats()

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
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            self.wfile.write(json.dumps(stats_data).encode())
        else:
            super().do_GET()
    
    def do_POST(self):
        if self.path == '/api/stats':
            content_length = int(self.headers['Content-Length'])
            post_data = self.rfile.read(content_length)
            try:
                data = json.loads(post_data.decode())
                # CLEAR AND REPLACE: Update in-memory storage with new values
                # This completely replaces old values, clearing temporary defaults
                global stats_data
                stats_data = data  # Complete replacement, not merge
                # Save to file for persistence - overwrites all previous data
                save_stats(stats_data)
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