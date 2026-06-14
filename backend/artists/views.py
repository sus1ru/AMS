import csv
from datetime import datetime
import io

from backend.artists.serializers import ArtistCreateSerializer, ArtistUpdateSerializer
from backend.auth.permissions import ARTIST_MANAGER, SUPER_ADMIN
from backend.core.pagination import get_pagination
from backend.core.responses import error_response, success_response
from backend.core.router import route
from backend.database import get_connection


@route(
    "/artists/available-users",
    method="GET",
    authenticated=True,
    roles={SUPER_ADMIN, ARTIST_MANAGER},
)
def available_user_list_view(request):
    conn = get_connection()
    cursor = conn.cursor()

    raw_query = """
        SELECT
            U.id,
            U.first_name || ' ' || U.last_name as fullname,
            U.email
        FROM users U
        LEFT JOIN artists A ON U.id = A.user_id
        WHERE U.role = 'artist'
          AND A.user_id IS NULL
          {search_filter}
    """

    search_q = request.query_params.get('q')
    params = []

    if search_q:
        search_filter = "AND (U.first_name LIKE ? OR U.last_name LIKE ? OR U.email LIKE ?)"
        search_value = f"{search_q}%"
        params = [search_value, search_value, search_value]
    else:
        search_filter = ""

    raw_query = raw_query.format(search_filter=search_filter)
    cursor.execute(raw_query, params)
    rows = cursor.fetchall()
    conn.close()

    users = [
        {"id": row[0], "fullname": row[1], "email": row[2]}
        for row in rows
    ]

    return success_response(
        message="Available users fetched successfully",
        data={"users": users},
    )


@route(
    "/artists",
    method="GET",
    authenticated=True,
    roles={SUPER_ADMIN, ARTIST_MANAGER},
)
def artist_list_view(request):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("select count(*) from artists")

    total = cursor.fetchone()[0]
    pagination = get_pagination(request, total)
    limit = pagination.pop('limit')
    offset = pagination.pop('offset')

    raw_query = """
        SELECT
            artists.id, artists.user_id, artists.name, artists.dob, artists.address,
            CASE
                WHEN artists.gender = 'm' THEN 'Male'
                WHEN artists.gender = 'f' THEN 'Female'
                ELSE 'Others'
            END AS artists_gender,
            first_release_year, no_of_albums_released,
            artists.created_at, artists.updated_at,
            users.first_name || ' ' || users.last_name as user_fullname,
            users.email
        FROM artists
        LEFT JOIN users ON users.id = artists.user_id
        LIMIT ? OFFSET ?
    """
    params = (limit, offset)

    cursor.execute(raw_query, params)
    rows = cursor.fetchall()
    conn.close()

    artists = [
        {
            "id": row[0],
            "user_id": row[1],
            "name": row[2],
            "dob": row[3],
            "gender": row[4],
            "address": row[5],
            "first_release_year": row[6],
            "no_of_albums_released": row[7],
            "created_at": row[8],
            "updated_at": row[9],
            "user_fullname": row[10],
            "user_email": row[11],
        }
        for row in rows
    ]

    return success_response(
        message="Artists fetched successfully",
        data={"artists": artists},
        pagination=pagination,
    )


@route(
    "/artists/create",
    method="POST",
    authenticated=True,
    roles={ARTIST_MANAGER},
)
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

    user_id = data.get("user_id")
    if user_id:
        cursor.execute("""
            SELECT users.id
            FROM users
            LEFT JOIN artists ON artists.user_id = users.id
            WHERE users.id = ?
              AND users.role = 'artist'
              AND artists.user_id IS NULL
        """, (user_id,))

        if not cursor.fetchone():
            conn.close()
            return error_response(
                message="Selected user is not available",
                errors={"error": "Selected user is not available"},
                status_code=400,
            )

    cursor.execute("""
        INSERT INTO artists (
            user_id, name, dob, gender, address,
            first_release_year, no_of_albums_released
        ) VALUES (?, ?, ?, ?, ?, ?, ?)
    """, (
        user_id,
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


@route(
    "/artists/update",
    method="POST",
    authenticated=True,
    roles={ARTIST_MANAGER},
)
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

    updated_cols = ", ".join([f"{key} = ?" for key in data])
    values = list(data.values()) + [artist_id]

    conn = get_connection()
    cursor = conn.cursor()

    user_id = data.get("user_id")
    if user_id:
        cursor.execute("""
            SELECT users.id
            FROM users
            LEFT JOIN artists ON artists.user_id = users.id
                AND artists.id != ?
            WHERE users.id = ?
              AND users.role = 'artist'
              AND artists.user_id IS NULL
        """, (artist_id, user_id))

        if not cursor.fetchone():
            conn.close()
            return error_response(
                message="Selected user is not available",
                errors={"error": "Selected user is not available"},
                status_code=400,
            )

    cursor.execute(f"""
        UPDATE artists
        SET {updated_cols},
            updated_at = strftime('%Y-%m-%dT%H:%M:%f+00:00', 'now')
        WHERE id = ?
    """, values)

    conn.commit()
    conn.close()

    return success_response(message="Artist updated successfully")

@route(
    "/artists/delete",
    method="POST",
    authenticated=True,
    roles={ARTIST_MANAGER},
)
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
    if cursor.rowcount == 0:
        conn.close()
        return error_response(
            message="Artist not found",
            errors={"error": "Artist not found"},
            status_code=404,
        )

    conn.commit()
    conn.close()

    return success_response(message="Artist deleted successfully")

@route(
    "/artists/import",
    method="POST",
    authenticated=True,
    roles={ARTIST_MANAGER},
)
def artist_import_view(request):
    print('request.data', request.data)
    csv_file = request.data.get("file")

    if not csv_file:
        return error_response(
            message="CSV file is required",
            errors={"file": "CSV file is required"},
            status_code=400,
        )

    csv_bytes = csv_file["content"]
    csv_text = csv_bytes.decode("utf-8")
    reader = csv.DictReader(io.StringIO(csv_text))

    conn = get_connection()
    cursor = conn.cursor()
    
    artists = []
    error_count = 0

    for row in reader:
        user_id = row.get("user_id", "").strip() or None
        first_year = row.get("first_release_year", "").strip() or None
        no_of_albums = row.get("no_of_albums_released", "0").strip()

        artist_data = {
            "user_id": user_id and int(user_id),    
            "name": row["name"],
            "dob": row["dob"],
            "gender": row["gender"],
            "address": row["address"],
            "first_release_year": first_year and int(first_year),
            "no_of_albums_released": no_of_albums and int(no_of_albums),
        }
        serializer = ArtistCreateSerializer(data=artist_data)

        if not serializer.is_valid():
            error_count = error_count + 1
            print(serializer.error_message)
            continue

        artists.append(tuple(artist_data.values()))

    cursor.executemany(
        """
            INSERT INTO artists
            (
                user_id, name,
                dob, gender,
                address, first_release_year,
                no_of_albums_released
            )
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """,
        artists
    )

    conn.commit()
    conn.close()

    return success_response(
        message='File recieved successfully',
        data={
            'total': len(artists) + error_count,
            'success': len(artists),
            'error': error_count,
        },
        status_code=200,
    )

@route(
    "/artists/export",
    method="GET",
    authenticated=True,
    roles={ARTIST_MANAGER},
)
def artist_export_view(request):
    is_sample = request.query_params.get('sample') in ['true', 'True']
    if is_sample:
        rows = [{
            "id": 101,
            "user_id": 201,
            "name": "DaBaby",
            "dob": '1993-02-03',
            "gender": 'Male',
            "address": 'm',
            "first_release_year": 2012,
            "no_of_albums_released": 4,
        }]
    else:
        conn = get_connection()
        cursor = conn.cursor()

        cursor.execute("""
            SELECT
                id, user_id, name,
                dob, gender, address,
                first_release_year,
                no_of_albums_released
            FROM artists
        """)

        rows = cursor.fetchall()
        conn.close()

    output = io.StringIO()

    fieldnames = [
        "id", "user_id", "name",
        "dob", "gender", "address",
        "first_release_year",
        "no_of_albums_released",
    ]

    writer = csv.DictWriter(output, fieldnames=fieldnames)
    writer.writeheader()

    for row in rows:
        writer.writerow({
            "id": row[0],
            "user_id": row[1] or "",
            "name": row[2],
            "dob": row[3] or "",
            "gender": row[4] or "",
            "address": row[5] or "",
            "first_release_year": row[6] or "",
            "no_of_albums_released": row[7] or 0,
        })

    filename = f'artists-{datetime.now().isoformat()}.csv'

    return {
        "_type": "file",
        "filename": filename,
        "content_type": "text/csv",
        "content": output.getvalue(),
    }, 200
