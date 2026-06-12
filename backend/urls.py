from backend.config import settings
from backend.core.responses import success_response
from backend.core.router import url_router

def root_view(request):
    return success_response(
        message="All available routes",
        data={
            'urls': [
                f'http://{settings.server_host}:{settings.server_port}{k}'
                for k in url_router.URL_MAPPINGS
            ]
        }
    )

url_router.add(
    '/',
    method='GET',
    authenticated=False,
    view=root_view,
    roles=None,
)
