from backend.core.responses import error_response


SUPER_ADMIN = "super_admin"
ARTIST_MANAGER = "artist_manager"
ARTIST = "artist"

USER_READ_ROLES = {SUPER_ADMIN}
USER_WRITE_ROLES = {SUPER_ADMIN}

ARTIST_READ_ROLES = {SUPER_ADMIN, ARTIST_MANAGER}
ARTIST_WRITE_ROLES = {ARTIST_MANAGER}

def has_role(user, allowed_roles):
    return user and user.get("role") in allowed_roles


def require_roles(request, allowed_roles):
    if not has_role(request.user, allowed_roles):
        return error_response(
            message="Permission denied",
            errors={"error": "Permission denied"},
            status_code=403,
        )

    return None

def user_owns_artist(cursor, user_id, artist_id):
    cursor.execute("""
        SELECT id
        FROM artists
        WHERE id = ?
          AND user_id = ?
    """, (artist_id, user_id))

    return cursor.fetchone() is not None