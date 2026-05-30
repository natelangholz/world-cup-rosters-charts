#!/usr/bin/env python3
"""
Simple HTTP server to test the dashboard locally.
Run: python serve.py
Then open: http://localhost:8000
"""
import http.server
import socketserver
import os

PORT = 8080

# Change to the project root directory
os.chdir(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

Handler = http.server.SimpleHTTPRequestHandler

with socketserver.TCPServer(("", PORT), Handler) as httpd:
    print(f"Server running at http://localhost:{PORT}/dashboard/")
    print("Press Ctrl+C to stop")
    httpd.serve_forever()

# Made with Bob
