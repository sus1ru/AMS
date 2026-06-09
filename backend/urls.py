from backend.config import settings
from backend.core.router import url_router

def root_view(request):
    return {
        'urls': [
            f'http://{settings.server_host}:{settings.server_port}{k}'
            for k in url_router.URL_MAPPINGS
        ]
    }, 200

url_router.add('/', 'GET', False, root_view)
