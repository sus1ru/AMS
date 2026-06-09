from backend.config import settings

class UrlRouter:
    URL_MAPPINGS = {}

    @classmethod
    def add(cls, path, method, authenticated, view):
        path = f'{settings.api_version}{path}'
        cls.URL_MAPPINGS[path] = (view, method, authenticated)

    @classmethod
    def map_url(cls, path):
        return cls.URL_MAPPINGS.get(path)

url_router = UrlRouter()


def route(path, method="GET", authenticated=False):
    def decorator(func):
        url_router.add(
            path,
            method,
            authenticated,
            func
        )
        return func
    return decorator