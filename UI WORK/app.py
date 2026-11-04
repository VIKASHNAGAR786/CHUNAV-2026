"""
=============================================================================
             JAINAGAR CHUNAV 2026 - DESKTOP & MOBILE APPLICATION
 Ultra-fast Offline Election App powered by Edge WebView2 / Native Webview
 Candidate: Pradhyumna Nagar (प्रद्युम्न नागर)
=============================================================================
"""

import os
import sys
import json
import threading
from http.server import SimpleHTTPRequestHandler, HTTPServer
from urllib.parse import urlparse, parse_qs

# Ensure UTF-8 output on Windows
if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding='utf-8')
        sys.stderr.reconfigure(encoding='utf-8')
    except Exception:
        pass

import webview
from database import Database
from promotion_data import CANDIDATE

APP_DIR = os.path.dirname(os.path.abspath(__file__))
WWW_DIR = os.path.join(APP_DIR, "www")
DB_PATH = os.path.join(APP_DIR, "jainagar_chunav.db")

db = Database(DB_PATH)


class JayanagarAPI:
    """Python-to-JavaScript RPC API bridge."""

    def search_voters(self, query: str = "", ward: int = 0, limit: int = 150):
        ward_filter = ward if ward and ward > 0 else None
        return db.search_voters(query=query, ward=ward_filter, limit=limit)

    def get_voter(self, voter_id: int):
        return db.get_voter_by_id(voter_id)

    def get_family(self, ward: int, house_number: str, exclude_id: int = 0):
        return db.get_family_members(ward=ward, house_number=house_number, exclude_id=exclude_id)

    def update_status(self, voter_id: int, status: str):
        return db.update_voter_status(voter_id=voter_id, status=status)

    def get_stats(self):
        return db.get_overall_stats()

    def get_ward_summary(self):
        return db.get_ward_summary()

    def get_candidate(self):
        return CANDIDATE


class ChunavHTTPRequestHandler(SimpleHTTPRequestHandler):
    """Local HTTP Server for static assets and REST fallback."""
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=WWW_DIR, **kwargs)

    def do_GET(self):
        parsed = urlparse(self.path)
        if parsed.path == "/api/search":
            qs = parse_qs(parsed.query)
            q = qs.get("q", [""])[0]
            ward_raw = qs.get("ward", ["0"])[0]
            try:
                ward = int(ward_raw)
            except Exception:
                ward = 0
            ward_filter = ward if ward > 0 else None
            results = db.search_voters(query=q, ward=ward_filter, limit=150)
            self.send_response(200)
            self.send_header("Content-Type", "application/json; charset=utf-8")
            self.end_headers()
            self.wfile.write(json.dumps(results, ensure_ascii=False).encode('utf-8'))
            return
        elif parsed.path == "/api/stats":
            stats = db.get_overall_stats()
            self.send_response(200)
            self.send_header("Content-Type", "application/json; charset=utf-8")
            self.end_headers()
            self.wfile.write(json.dumps(stats, ensure_ascii=False).encode('utf-8'))
            return
        elif parsed.path == "/api/wards":
            wards = db.get_ward_summary()
            self.send_response(200)
            self.send_header("Content-Type", "application/json; charset=utf-8")
            self.end_headers()
            self.wfile.write(json.dumps(wards, ensure_ascii=False).encode('utf-8'))
            return

        return super().do_GET()

    def log_message(self, format, *args):
        # Suppress noisy HTTP logs in console
        pass


def start_local_server(port: int = 5055):
    server = HTTPServer(("127.0.0.1", port), ChunavHTTPRequestHandler)
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    return server


def main():
    port = 5055
    start_local_server(port)
    url = f"http://127.0.0.1:{port}/index.html"

    api = JayanagarAPI()

    print("=" * 65)
    print("      JAINAGAR CHUNAV 2026 - OFFLINE MOBILE APPLICATION")
    print("      Candidate: Pradhyumna Nagar (प्रद्युम्न नागर)")
    print("=" * 65)
    print(f"Local Server URL: {url}")
    print("Opening Native Mobile Desktop Window (430 x 860)...")
    print("Press Ctrl+C or close window to exit.\n")

    # Open smartphone-proportioned native window with Edge Chromium WebView2 engine
    window = webview.create_window(
        title="जयनगर चुनाव 2026 | प्रद्युम्न नागर",
        url=url,
        js_api=api,
        width=430,
        height=860,
        resizable=True,
        min_size=(360, 640)
    )

    webview.start(debug=False)


if __name__ == "__main__":
    main()
