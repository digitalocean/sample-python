# -*- coding: utf-8 -*-
import os
import http.server
import socketserver
import locale
from sammy import sammy_ascii
from http import HTTPStatus

locale.setlocale(locale.LC_ALL, 'en_US.UTF-8')

class Handler(http.server.SimpleHTTPRequestHandler):
    def do_GET(self):
        self.send_response(HTTPStatus.OK)
        self.end_headers()
        msg = 'Hello! you requested %s' % (self.path)
        self.wfile.write(msg.encode())


print(sammy_ascii)

port = int(os.getenv('PORT', 80))
print('Listening on port %s 🚀' % (port))
httpd = socketserver.TCPServer(('', port), Handler)
httpd.serve_forever()