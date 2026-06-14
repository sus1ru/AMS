import secrets
from datetime import datetime, timedelta, UTC

from backend.database import get_connection
from backend.config import settings


def create_session(user_id):
    session_id = secrets.token_urlsafe(32)
    expires_at = datetime.now(UTC) + timedelta(hours=settings.session_ttl_hours)

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        INSERT INTO sessions (session_id, user_id, expires_at)
        VALUES (?, ?, ?)
    """, (session_id, user_id, expires_at.isoformat()))

    conn.commit()
    conn.close()

    return session_id

def delete_session(user_id):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        DELETE FROM sessions
        WHERE sessions.user_id = ?
    """, (user_id,))

    conn.commit()
    conn.close()