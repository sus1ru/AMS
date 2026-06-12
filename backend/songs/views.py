import sqlite3

from backend.auth.permissions import ARTIST, ARTIST_MANAGER, SUPER_ADMIN, user_owns_artist
from backend.core.pagination import get_pagination
from backend.core.responses import error_response, success_response
from backend.core.router import route
from backend.database import get_connection
from backend.songs.serializers import SongCreateSerializer, SongUpdateSerializer


def artist_exists(cursor, artist_id):
    cursor.execute("SELECT id FROM artists WHERE id = ?", (artist_id,))
    return cursor.fetchone() is not None


@route(
    "/songs/available-artists",
    method="GET",
    authenticated=True,
    roles={SUPER_ADMIN, ARTIST_MANAGER},
)
def available_artists_list_view(request):
    conn = get_connection()
    cursor = conn.cursor()

    raw_query = "SELECT id, name FROM artists {search_filter}"

    search_q = request.query_params.get('q')
    params = []

    if search_q:
        search_filter = "WHERE name LIKE ?"
        params = [f"{search_q}%"]
    else:
        search_filter = ""

    raw_query = raw_query.format(search_filter=search_filter)
    cursor.execute(raw_query, params)
    rows = cursor.fetchall()
    conn.close()

    artists = [
        {"id": row[0], "name": row[1]}
        for row in rows
    ]

    return success_response(
        message="Available artists fetched successfully",
        data={"artists": artists},
    )


@route(
    "/songs",
    method="GET",
    authenticated=True,
    roles={SUPER_ADMIN, ARTIST_MANAGER, ARTIST}
)
def song_list_view(request):    
    conn = get_connection()
    cursor = conn.cursor()

    user_role = request.user.get("role")
    if user_role == ARTIST:
        user_id = request.user.get("id")
        cursor.execute("SELECT id FROM artists WHERE user_id = ?", (user_id,))
        artist_id = cursor.fetchone()[0]
        artist_filter = f"WHERE artist_id = {artist_id}"
    else:
        artist_filter = ""

    cursor.execute(f"SELECT count(*) FROM songs {artist_filter}")
    total = cursor.fetchone()[0]
    pagination = get_pagination(request, total)
    limit = pagination.pop("limit")
    offset = pagination.pop("offset")

    cursor.execute("""
        SELECT
            id, artist_id, title,
            album_name, genre,
            created_at, updated_at
        FROM songs
        {filter}
        LIMIT ? OFFSET ?
    """.format(filter=artist_filter), (limit, offset))

    rows = cursor.fetchall()
    conn.close()

    songs = [
        {
            "id": row[0],
            "artist_id": row[1],
            "title": row[2],
            "album_name": row[3],
            "genre": row[4],
            "created_at": row[5],
            "updated_at": row[6],
        }
        for row in rows
    ]

    return success_response(
        message="Songs fetched successfully",
        data={"songs": songs},
        pagination=pagination,
    )


@route(
    "/songs/create",
    method="POST",
    authenticated=True,
    roles={ARTIST},
)
def song_create_view(request):
    serializer = SongCreateSerializer(request.data)
    if not serializer.is_valid():
        return error_response(
            message=serializer.error_message,
            errors={"error": serializer.error_dict},
        )

    data = serializer.validated_data
    conn = get_connection()
    cursor = conn.cursor()

    if not user_owns_artist(cursor, request.user["id"], data["artist_id"]):
        conn.close()
        return error_response(
            message="Permission denied",
            errors={"error": "Permission denied"},
            status_code=403,
        )

    if not artist_exists(cursor, data["artist_id"]):
        conn.close()
        return error_response(
            message="Artist not found",
            errors={"error": "Artist not found"},
            status_code=404,
        )

    cursor.execute("""
        INSERT INTO songs (artist_id, title, album_name, genre)
        VALUES (?, ?, ?, ?)
    """, (
        data["artist_id"],
        data["title"],
        data.get("album_name"),
        data["genre"],
    ))

    conn.commit()
    song_id = cursor.lastrowid
    conn.close()

    return success_response(
        message="Song created successfully",
        data={"id": song_id},
        status_code=201,
    )


@route(
    "/songs/update",
    method="POST",
    authenticated=True,
    roles={ARTIST},
)
def song_update_view(request):
    serializer = SongUpdateSerializer(request.data)
    if not serializer.is_valid():
        return error_response(
            message=serializer.error_message,
            errors={"error": serializer.error_dict},
        )

    data = serializer.validated_data
    song_id = data.pop("id")
    update_data = {
        key: value
        for key, value in data.items()
        if value is not None
    }

    if not update_data:
        return error_response(
            message="No fields to update",
            errors={"error": "No fields to update"},
        )

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("SELECT artist_id FROM songs WHERE id = ?", (song_id,))
    song = cursor.fetchone()
    if not song:
        conn.close()
        return error_response(
            message="Song not found",
            errors={"error": "Song not found"},
            status_code=404,
        )

    current_artist_id = song[0]
    if not user_owns_artist(cursor, request.user["id"], current_artist_id):
        conn.close()
        return error_response(
            message="Permission denied",
            errors={"error": "Permission denied"},
            status_code=403,
        )

    target_artist_id = update_data.get("artist_id")
    if target_artist_id and not artist_exists(cursor, target_artist_id):
        conn.close()
        return error_response(
            message="Artist not found",
            errors={"error": "Artist not found"},
            status_code=404,
        )

    set_clause = ", ".join([f"{key} = ?" for key in update_data])
    values = list(update_data.values()) + [song_id]

    try:
        cursor.execute(f"""
            UPDATE songs
            SET {set_clause},
                updated_at = strftime('%Y-%m-%dT%H:%M:%f+00:00', 'now')
            WHERE id = ?
        """, values)
    except sqlite3.IntegrityError:
        conn.close()
        return error_response(
            message="Invalid song data",
            errors={"error": "Invalid song data"},
        )

    conn.commit()
    conn.close()

    return success_response(message="Song updated successfully")


@route(
    "/songs/delete",
    method="POST",
    authenticated=True,
    roles={ARTIST},
)
def song_delete_view(request):
    song_id = request.data.get("id")
    if not song_id:
        return error_response(
            message="id is required",
            errors={"error": "id is required"},
        )

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("SELECT artist_id FROM songs WHERE id = ?", (song_id,))
    song = cursor.fetchone()
    if not song:
        conn.close()
        return error_response(
            message="Song not found",
            errors={"error": "Song not found"},
            status_code=404,
        )

    if not user_owns_artist(cursor, request.user["id"], song[0]):
        conn.close()
        return error_response(
            message="Permission denied",
            errors={"error": "Permission denied"},
            status_code=403,
        )

    cursor.execute("DELETE FROM songs WHERE id = ?", (song_id,))
    if cursor.rowcount == 0:
        conn.close()
        return error_response(
            message="Song not found",
            errors={"error": "Song not found"},
            status_code=404,
        )

    conn.commit()
    conn.close()

    return success_response(message="Song deleted successfully")
