from http.server import BaseHTTPRequestHandler
import json

from backend.core.exceptions import *
from backend.urls import url_router


class RequestHandler(BaseHTTPRequestHandler):
    def send_json(self, data, status_code=200) -> None:
        self.send_response(status_code)
        self.send_header("Content-Type", "application/json")
        self.end_headers()
        self.wfile.write(json.dumps(data).encode())

    def pre_process_request(self, path, incoming_method):
        if path not in url_router.URL_MAPPINGS:
            raise RouteDoesnotExist()

        view, allowed_method = url_router.map_url(self.path)

        if incoming_method != allowed_method:
            raise MethodNotAllowed()

        return view

    def process_payload(self) -> dict:
        content_length = int(self.headers.get("Content-Length", 0))
        body = self.rfile.read(content_length)

        try:
            payload = json.loads(body)
        except json.JSONDecodeError as e:
            raise InvalidPayload()

        return payload

    def do_GET(self) -> None:
        try:
            view = self.pre_process_request(self.path, 'GET')
        except MethodNotAllowed as e:
            self.send_json({"error": "Method not allowed"}, 405)
            return
        except RouteDoesnotExist as e:
            self.send_json({"error": "Route not found"}, 404)
            return

        response, status_code = view()
        self.send_json(response, status_code)

    def do_POST(self) -> None:
        try:
            view = self.pre_process_request(self.path, 'POST')
        except MethodNotAllowed as e:
            self.send_json({"error": "Method not allowed"}, 405)
            return
        except RouteDoesnotExist as e:
            self.send_json({"error": "Route not found"}, 404)
            return

        try:
            data = self.process_payload()
        except InvalidPayload as e:
            self.send_json({"error": "Invalid Payload"}, 400)

        response, status_code = view(data)
        self.send_json(response, status_code)