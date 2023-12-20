import os
import http.server
import socketserver

from http import HTTPStatus


class Handler(http.server.SimpleHTTPRequestHandler):
    def __enter__(self):
        self.send_response(HTTPStatus.OK)
        self.end_headers()
        msg = 'Hello! you requested %s' % (self.path)
        self.wfile.write(msg.encode())


if __name__ == "__main__":
    port = int(os.getenv('PORT', 80))
    print('Listening on port %s' % (port))
    httpd = socketserver.TCPServer(('', port), Handler)
    httpd.serve_forever()
