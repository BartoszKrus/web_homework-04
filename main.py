import mimetypes
from http.server import HTTPServer, BaseHTTPRequestHandler
import urllib.parse
import socketserver
import json
from datetime import datetime
import socket
import threading


class HttpHandler(BaseHTTPRequestHandler):
    def do_POST(self):
        data = self.rfile.read(int(self.headers['Content-Length']))
        data_parse = urllib.parse.unquote_plus(data.decode())
        data_dict = {key: value for key, value in [el.split('=') for el in data_parse.split('&')]}

        username = data_dict.get('username', '')
        message = data_dict.get('message', '')
        timestamp = datetime.now().isoformat()

        socket_client = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        socket_client.sendto(json.dumps({"username": username, "message": message, "timestamp": timestamp}).encode(), ("localhost", SOCKET_PORT))

        self.send_response(302)
        self.send_header('Location', '/')
        self.end_headers()

    def do_GET(self):
        pr_url = urllib.parse.urlparse(self.path)
        if pr_url.path == '/':
            self.send_html_file('index.html')
        elif pr_url.path == '/message.html':
            self.send_html_file('message.html')
        elif pr_url.path == '/logo.png':
            self.send_static('logo.png', 'image/png')
        elif pr_url.path == '/style.css':
            self.send_static('style.css', 'text/css')
        else:
            self.send_html_file('error.html', 404)

    def send_html_file(self, filename, status=200):
        self.send_response(status)
        self.send_header('Content-type', 'text/html')
        self.end_headers()
        with open(filename, 'rb') as fd:
            self.wfile.write(fd.read())

    def send_static(self):
        self.send_response(200)
        mt = mimetypes.guess_type(self.path)
        if mt:
            self.send_header("Content-type", mt[0])
        else:
            self.send_header("Content-type", 'text/plain')
        self.end_headers()
        with open(f'.{self.path}', 'rb') as file:
            self.wfile.write(file.read())

class SocketServer(socketserver.BaseRequestHandler):
    def handle(self):
        data, _ = self.request
        data = json.loads(data.decode())

        with open(DATA_FILE, 'a') as file:
            json.dump({data['timestamp']: {"username": data['username'], "message": data['message']}}, file)
            file.write('\n')

HTTP_PORT = 3000
SOCKET_PORT = 5000
DATA_FILE = "storage/data.json"

def run():
    http_server = HTTPServer(('localhost', HTTP_PORT), HttpHandler)
    http_thread = threading.Thread(target=http_server.serve_forever)
    http_thread.start()

    socket_server = socketserver.UDPServer(('localhost', SOCKET_PORT), SocketServer)
    socket_thread = threading.Thread(target=socket_server.serve_forever)
    socket_thread.start()

    try:
        http_thread.join()
        socket_thread.join()
    except KeyboardInterrupt:
        http_server.shutdown()
        socket_server.shutdown()

if __name__ == '__main__':
    run()
