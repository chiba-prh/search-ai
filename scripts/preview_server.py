#!/usr/bin/env python3
"""Simple HTTP server to preview generated Obsidian markdown files."""

import http.server
import os
import sys
from pathlib import Path

if sys.stdout.encoding != "utf-8":
    sys.stdout.reconfigure(encoding="utf-8")

PORT = int(os.environ.get("PORT", 8080))
SERVE_DIR = Path(os.environ.get("OUTPUT_DIR", "output"))


def main():
    if not SERVE_DIR.exists():
        SERVE_DIR.mkdir(parents=True, exist_ok=True)
        print(f"Created output directory: {SERVE_DIR}")

    os.chdir(SERVE_DIR)
    handler = http.server.SimpleHTTPRequestHandler
    server = http.server.HTTPServer(("0.0.0.0", PORT), handler)
    print(f"🌐 Preview server running at http://localhost:{PORT}")
    print(f"   Serving files from: {SERVE_DIR.resolve()}")
    print("   Press Ctrl+C to stop")

    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\nServer stopped.")
        sys.exit(0)


if __name__ == "__main__":
    main()
