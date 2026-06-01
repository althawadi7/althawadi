#!/usr/bin/env python3
"""Serve the site locally at http://localhost:8000/ (root domain layout)."""

import http.server
import socketserver
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PORT = 8000


class LocalHandler(http.server.SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=str(ROOT), **kwargs)

    def end_headers(self) -> None:
        self.send_header("Cache-Control", "no-store")
        super().end_headers()


def main() -> None:
    handler = LocalHandler
    for port in (PORT, PORT + 1):
        try:
            with socketserver.TCPServer(("", port), handler) as httpd:
                print(f"Serving {ROOT}")
                print(f"Open: http://localhost:{port}/")
                print(f"News: http://localhost:{port}/news/")
                print("Press Ctrl+C to stop.")
                httpd.serve_forever()
            return
        except OSError as exc:
            if port == PORT + 1:
                raise SystemExit(f"Could not bind to port {PORT} or {PORT + 1}: {exc}") from exc
            print(f"Port {PORT} is in use. Trying {PORT + 1}...")


if __name__ == "__main__":
    main()
