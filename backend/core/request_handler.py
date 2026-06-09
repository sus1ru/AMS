from http.cookies import SimpleCookie
from http.server import BaseHTTPRequestHandler
import json

from backend.config import settings
from backend.core.exceptions import *
from backend.core.middleware import (
    get_session_user_middleware,
    session_cookie_middleware
)
from backend.urls import url_router


class RequestHandler(BaseHTTPRequestHandler):
    def setup_response(self):
        self.response_headers = {
            "Content-Type": "application/json",
            "Access-Control-Allow-Credentials": "true",
            "Access-Control-Allow-Headers": "Content-Type",
        }
        if (origin:=self.headers.get("Origin")) in settings.cors_allowed_origin:
            self.response_headers["Access-Control-Allow-Origin"] = origin

    def set_header(self, key, value):
        self.response_headers[key] = value

    def get_cookie(self, name):
        cookie_header = self.headers.get("Cookie")

        if not cookie_header:
            return None

        cookies = SimpleCookie()
        cookies.load(cookie_header)

        if name not in cookies:
            return None

        return cookies[name].value

    def pre_process_request(self, path, incoming_method):
        self.setup_response()

        if path not in url_router.URL_MAPPINGS:
            self.response_headers["Access-Control-Allow-Methods"] = "OPTIONS"
            raise RouteDoesnotExist()

        view, allowed_method, authenticated = url_router.map_url(self.path)

        if incoming_method not in ('OPTIONS', allowed_method):
            raise MethodNotAllowed()

        self.response_headers["Access-Control-Allow-Methods"] = f"{allowed_method}, OPTIONS"

        if incoming_method == 'OPTIONS':
            return view, allowed_method, authenticated

        self.user = None

        if authenticated:
            user = get_session_user_middleware(self)

            if not user:
                raise UnauthorizedException()
            else:
                self.user = user

        return view, allowed_method, authenticated

    def do_OPTIONS(self):
        try:
            _, _, _ = self.pre_process_request(self.path, 'OPTIONS')
        except RouteDoesnotExist:
            pass

        self.send_response(204)
        for key, value in self.response_headers.items():
            if key != 'Content-Type':
                self.send_header(key, value)

        self.end_headers()

    def send_json(self, data, status_code=200):
        self.send_response(status_code)

        for key, value in self.response_headers.items():
            print('send_json key value', key, value)
            self.send_header(key, value)

        self.end_headers()
        self.wfile.write(json.dumps(data).encode())

    def do_GET(self) -> None:
        try:
            view, _, _ = self.pre_process_request(self.path, 'GET')
        except MethodNotAllowed:
            self.send_json({"error": "Method not allowed"}, 405)
            return
        except RouteDoesnotExist:
            self.send_json({"error": "Route not found"}, 404)
            return
        except UnauthorizedException:
            self.send_json({"error": "Authentication is required"}, 401)
            return

        response, status_code = view(self)
        response, status_code = session_cookie_middleware(
            self,
            response,
            status_code
        )
        self.send_json(response, status_code)

    def process_payload(self) -> dict:
        content_length = int(self.headers.get("Content-Length", 0))
        if content_length == 0:
            return {}

        body = self.rfile.read(content_length)

        try:
            payload = json.loads(body)
        except json.JSONDecodeError:
            raise InvalidPayload()

        return payload

    def do_POST(self) -> None:
        try:
            view, _, _ = self.pre_process_request(self.path, 'POST')
        except MethodNotAllowed:
            self.send_json({"error": "Method not allowed"}, 405)
            return
        except RouteDoesnotExist:
            self.send_json({"error": "Route not found"}, 404)
            return
        except UnauthorizedException:
            self.send_json({"error": "Authentication is required"}, 401)
            return

        try:
            self.data = self.process_payload()
        except InvalidPayload:
            self.send_json({"error": "Invalid Payload"}, 400)
            return

        response, status_code = view(self)
        response, status_code = session_cookie_middleware(
            self,
            response,
            status_code
        )
        self.send_json(response, status_code)
