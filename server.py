from http.server import HTTPServer, SimpleHTTPRequestHandler
import json
import subprocess
import os
import urllib.parse

class ZeoliteHandler(SimpleHTTPRequestHandler):
    def do_POST(self):
        if self.path == '/process':
            content_length = int(self.headers['Content-Length'])
            post_data = self.rfile.read(content_length).decode('utf-8')
            params = json.loads(post_data)
            cif_name = params.get('cif')
            
            if not cif_name:
                self.send_error(400, "Missing CIF name")
                return

            cif_path = os.path.join("all-cif", cif_name)
            print(f"Server: Processing {cif_path}...")
            
            try:
                # Run the topology processor
                result = subprocess.run(
                    ["python", "process_topology.py", cif_path],
                    capture_output=True, text=True, check=True
                )
                print(result.stdout)
                
                self.send_response(200)
                self.send_header('Content-type', 'application/json')
                self.send_header('Access-Control-Allow-Origin', '*')
                self.end_headers()
                self.wfile.write(json.dumps({"status": "success", "file": cif_name}).encode())
            except Exception as e:
                print(f"Error processing: {str(e)}")
                self.send_error(500, str(e))
        else:
            self.send_error(404)

    def do_OPTIONS(self):
        self.send_response(200)
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        self.end_headers()

if __name__ == '__main__':
    port = 8001
    server = HTTPServer(('localhost', port), ZeoliteHandler)
    print(f"Backend listener started on port {port}...")
    server.serve_forever()
