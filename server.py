import os
import http.server
import socketserver

from http import HTTPStatus


class Handler(http.server.SimpleHTTPRequestHandler):
    def do_GET(self):
        self.send_response(HTTPStatus.OK)
        self.end_headers()
        msg = f'Hello! you requested {self.path}'
        self.wfile.write(msg.encode())


port = int(os.getenv('PORT', 80))
print(f'Listening on port {port}')
httpd = socketserver.TCPServer(('', port), Handler)
httpd.serve_forever()
