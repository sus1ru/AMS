from backend.database import get_connection
from backend.config import settings

def get_session_user_middleware(request):
    session_id = request.get_cookie("session_id")
    if not session_id:
        return None

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT
            users.id, users.first_name, users.last_name,
            users.email, users.role
        FROM sessions
        JOIN users ON users.id = sessions.user_id
        WHERE sessions.session_id = ?
          AND sessions.expires_at > datetime('now')
    """, (session_id,))

    row = cursor.fetchone()
    conn.close()

    if not row:
        return None

    return {
        "id": row[0],
        "first_name": row[1],
        "last_name": row[2],
        "email": row[3],
        "role": row[4],
    }


def session_cookie_middleware(request, response, status_code):
    if request.path == f"{settings.api_version}/login" and status_code == 200:
        session_id = response.pop("session_id", None)

        if session_id:
            request.set_header(
                "Set-Cookie",
                f"session_id={session_id}; HttpOnly; Path=/; SameSite=Lax"
            )

    if request.path == f"{settings.api_version}/logout" and status_code == 200:
        request.set_header(
            "Set-Cookie",
            "session_id=; HttpOnly; Path=/; Max-Age=0; SameSite=Lax"
        )

    return response, status_code
