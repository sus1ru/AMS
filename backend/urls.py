from backend.auth.register import register_view
from backend.config import settings

class UrlRouter:
    URL_MAPPINGS = {}

    @classmethod
    def add(cls, path, method, view):
        cls.URL_MAPPINGS[path] = (view, method)

    @classmethod
    def map_url(cls, path):
        return cls.URL_MAPPINGS.get(path)

url_router = UrlRouter()
url_router.add('/register', 'POST', register_view)

def root_view():
    return {
        'urls': [
            f'http://{settings.server_host}:{settings.server_port}{k}'
            for k in url_router.URL_MAPPINGS
        ]
    }, 200

url_router.add('/', 'GET', root_view)