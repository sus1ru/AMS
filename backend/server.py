from http.server import HTTPServer, BaseHTTPRequestHandler

class RequestHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.send_header("Content-Type", "text/plain")
        self.end_headers()
        self.wfile.write(b"Hello from python HTTP server")


def runserver(server_class=HTTPServer, handler_class=RequestHandler):
    server_address = ('', 8500)
    httpd = server_class(server_address, handler_class)
    print("Server running on http://localhost:8500")
    httpd.serve_forever()


if __name__ == "__main__":
    runserver()