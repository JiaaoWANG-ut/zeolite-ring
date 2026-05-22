"""
Legacy local development server (optional).

Serves static files and exposes POST /process for on-the-fly topology generation.
Production uses precomputed JSON in data/topology/ on Cloudflare Pages.
"""

from http.server import HTTPServer, SimpleHTTPRequestHandler
import json
import subprocess
import os

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


class ZeoliteHandler(SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=ROOT, **kwargs)

    def do_POST(self):
        if self.path == "/process":
            content_length = int(self.headers["Content-Length"])
            post_data = self.rfile.read(content_length).decode("utf-8")
            params = json.loads(post_data)
            cif_name = params.get("cif")

            if not cif_name:
                self.send_error(400, "Missing CIF name")
                return

            cif_path = os.path.join(ROOT, "all-cif", cif_name)
            print(f"Server: Processing {cif_path}...")

            try:
                result = subprocess.run(
                    ["python3", os.path.join(ROOT, "process_topology.py"), cif_path],
                    cwd=ROOT,
                    capture_output=True,
                    text=True,
                    check=True,
                )
                print(result.stdout)

                self.send_response(200)
                self.send_header("Content-type", "application/json")
                self.send_header("Access-Control-Allow-Origin", "*")
                self.end_headers()
                self.wfile.write(json.dumps({"status": "success", "file": cif_name}).encode())
            except Exception as exc:
                print(f"Error processing: {exc}")
                self.send_error(500, str(exc))
        else:
            self.send_error(404)

    def do_OPTIONS(self):
        self.send_response(200)
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "POST, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type")
        self.end_headers()


if __name__ == "__main__":
    port = 8001
    server = HTTPServer(("localhost", port), ZeoliteHandler)
    print(f"Dev server started on http://localhost:{port}")
    print("Open landing.html via a static server, or browse files directly.")
    server.serve_forever()
