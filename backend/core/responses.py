def success_response(
    message="Success",
    data=None,
    status_code=200,
    pagination=None,
):
    return {
        "success": True,
        "message": message,
        "data": data,
        "pagination": pagination,
    }, status_code


def error_response(message="Error", errors=None, status_code=400):
    return {
        "success": False,
        "message": message,
        "errors": errors,
    }, status_code