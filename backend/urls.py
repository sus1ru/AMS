from backend.auth.views import user_list_view, user_register_view
from backend.config import settings
from backend.core.router import url_router

def root_view():
    return {
        'urls': [
            f'http://{settings.server_host}:{settings.server_port}{k}'
            for k in url_router.URL_MAPPINGS
        ]
    }, 200

url_router.add('/', 'GET', root_view)
url_router.add('/users', 'GET', user_list_view)
url_router.add('/register', 'POST', user_register_view)
