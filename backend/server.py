from http.server import HTTPServer

from backend.database import setup_db
from backend.config import settings
from backend.core.request_handler import RequestHandler

def init_server():
    import backend.auth.views
    setup_db()

def runserver(server_class=HTTPServer, handler_class=RequestHandler):
    init_server()
    server_address = (settings.server_host, settings.server_port)
    httpd = server_class(server_address, handler_class)
    print(f"Server running on http://{settings.server_host}:{settings.server_port}")
    httpd.serve_forever()


if __name__ == "__main__":
    runserver()