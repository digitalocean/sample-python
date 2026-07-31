import os
import http.server
import socketserver

from http import HTTPStatus
from http.server import BaseHTTPRequestHandler, HTTPServer

class Handler(http.server.SimpleHTTPRequestHandler):
    def do_GET(self):
        self.send_response(HTTPStatus.OK)
        self.send_header("Content-Type", "text/html; charset=utf-8")
        self.end_headers()

        html_content = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <title>MBC Status</title>
            <style>
                body {{ font-family: Arial, sans-serif; text-align: center; margin-top: 50px; background-color: #f4f4f9; color: #333; }}
                h1 {{ color: #0066cc; }}
                p {{ font-size: 1.2em; }}
            </style>
        </head>
        <body>
            <h1>Hello Buddy!!!!!</h1>
            <p>MBC HERE ON 30TH JUL AGAIN NOW 31ST JULY</p>
            <p><strong>Path requested:</strong> {self.path}</p>
        </body>
        </html>
        """
        self.wfile.write(html_content.encode("utf-8"))

# To run the server
if __name__ == "__main__":
    server = HTTPServer(("localhost", 8080), MyHandler)
    print("Server running on http://localhost:8080")
    server.serve_forever()

# port = int(os.getenv('PORT', 80))
# print('Listening on port %s' % (port))
# httpd = socketserver.TCPServer(('', port), Handler)
# httpd.serve_forever()
