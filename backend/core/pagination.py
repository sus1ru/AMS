from backend.config import settings


def get_pagination(request, total):
    page = int(request.query_params.get("page", 1))
    limit = int(request.query_params.get("limit", 10))

    total_pages = (total + limit - 1) // limit
    offset = (page - 1) * limit

    base_url = f"http://{settings.server_host}:{settings.server_port}{request.path_only}"

    next_link = None
    previous_link = None

    if page < total_pages:
        next_link = f"{base_url}?page={page + 1}&limit={limit}"

    if page > 1:
        previous_link = f"{base_url}?page={page - 1}&limit={limit}"

    return {
        "limit": limit,
        "offset": offset,
        "total": total,
        "next": next_link,
        "previous": previous_link,
    }