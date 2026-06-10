from backend.artists.serializers import ArtistCreateSerializer, ArtistUpdateSerializer
from backend.core.pagination import get_pagination
from backend.core.responses import error_response, success_response
from backend.core.router import route
from backend.database import get_connection


@route("/artists", method="GET", authenticated=True)
def artist_list_view(request):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("select count(*) from artists")

    total = cursor.fetchone()[0]
    pagination = get_pagination(request, total)
    limit = pagination.pop('limit')
    offset = pagination.pop('offset')

    cursor.execute("""
        SELECT
            id, name, dob, gender, address,
            first_release_year, no_of_albums_released,
            created_at, updated_at
        FROM artists
        LIMIT ? OFFSET ?
    """, (limit, offset))

    rows = cursor.fetchall()

    conn.close()

    artists = [
        {
            "id": row[0],
            "name": row[1],
            "dob": row[2],
            "gender": row[3],
            "address": row[4],
            "first_release_year": row[5],
            "no_of_albums_released": row[6],
            "created_at": row[7],
            "updated_at": row[8],
        }
        for row in rows
    ]

    return success_response(
        message="Artists fetched successfully",
        data={"users": artists},
        pagination=pagination,
    )


@route("/artists/create", method="POST", authenticated=True)
def artist_create_view(request):
    serializer = ArtistCreateSerializer(request.data)

    if not serializer.is_valid():
        return error_response(
            message=serializer.error_message,
            errors={"error": serializer.error_dict},
        )

    data = serializer.validated_data

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        INSERT INTO artists (
            name, dob, gender, address,
            first_release_year, no_of_albums_released
        ) VALUES (?, ?, ?, ?, ?, ?)
    """, (
        data["name"],
        data.get("dob"),
        data.get("gender"),
        data.get("address"),
        data.get("first_release_year"),
        data.get("no_of_albums_released") or 0,
    ))

    conn.commit()
    artist_id = cursor.lastrowid
    conn.close()

    return success_response(
        message="Artist created successfully",
        data={"id": artist_id},
        status_code=201,
    )


@route("/artists/update", method="POST", authenticated=True)
def artist_update_view(request):
    artist_id = request.data.get("id")

    if not artist_id:
        return error_response(
            message="id is required",
            errors={"error": "id is required"},
        )

    serializer = ArtistUpdateSerializer(request.data)

    if not serializer.is_valid():
        return error_response(
            message=serializer.error_message,
            errors={"error": serializer.error_dict},
        )

    data = {
        key: value
        for key, value in serializer.validated_data.items()
        if key != "id" and value is not None
    }

    if not data:
        return error_response(
            message="No fields to update",
            errors={"error": "No fields to update"},
        )

    set_clause = ", ".join([f"{key} = ?" for key in data])
    values = list(data.values()) + [artist_id]

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute(f"""
        UPDATE artists
        SET {set_clause},
            updated_at = strftime('%Y-%m-%dT%H:%M:%f+00:00', 'now')
        WHERE id = ?
    """, values)

    conn.commit()
    conn.close()

    return success_response(message="Artist updated successfully")

@route("/artists/delete", method="POST", authenticated=True)
def artist_delete_view(request):
    artist_id = request.data.get("id")

    if not artist_id:
        return error_response(
            message="id is required",
            errors={"error": "id is required"},
        )

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("DELETE FROM artists WHERE id = ?", (artist_id,))

    conn.commit()
    conn.close()

    return success_response(message="Artist deleted successfully")