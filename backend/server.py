from http.server import HTTPServer, BaseHTTPRequestHandler

from backend.database import create_tables
from backend.config import settings

class RequestHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.send_header("Content-Type", "text/plain")
        self.end_headers()
        self.wfile.write(b"Hello from python HTTP server")


def runserver(server_class=HTTPServer, handler_class=RequestHandler):
    create_tables()
    server_address = (settings.server_host, settings.server_port)
    httpd = server_class(server_address, handler_class)
    print(f"Server running on http://{settings.server_host}:{settings.server_port}")
    httpd.serve_forever()


if __name__ == "__main__":
    runserver()