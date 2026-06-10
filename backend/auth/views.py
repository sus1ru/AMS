import sqlite3

from backend.auth.serializers import UserLoginSerializer, UserRegisterSerializer
from backend.auth.sessions import create_session, delete_session
from backend.auth.utils import hash_password, verify_password
from backend.core.pagination import get_pagination
from backend.core.responses import error_response, success_response
from backend.core.router import route
from backend.database import get_connection

ALLOWED_ROLES = {"super_admin", "artist_manager", "artist"}
ALLOWED_GENDERS = {"m", "f", "o"}

@route(
    '/users',
    method='GET',
    authenticated=True
)
def user_list_view(request):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("select count(*) from users")

    total = cursor.fetchone()[0]
    pagination = get_pagination(request, total)
    limit = pagination.pop('limit')
    offset = pagination.pop('offset')

    cursor.execute("""
        SELECT
            id, first_name, last_name,
            email, phone, dob,
            gender, address, role,
            created_at, updated_at
        FROM users
        LIMIT ? OFFSET ?
    """, (limit, offset))

    rows = cursor.fetchall()
    conn.close()

    users = [
        {
            "id": row[0],
            "first_name": row[1],
            "last_name": row[2],
            "email": row[3],
            "phone": row[4],
            "dob": row[5],
            "gender": row[6],
            "address": row[7],
            "role": row[8],
            "created_at": row[9],
            "updated_at": row[10],
        } for row in rows
    ]
    return success_response(
        message="Users fetched successfully",
        data={"users": users},
        pagination=pagination,
    )

@route(
    '/register',
    method='POST',
    authenticated=False
)
def user_register_view(request):
    data = request.data

    serializer = UserRegisterSerializer(request.data)

    if not serializer.is_valid():
        return error_response(
            message=serializer.error_message,
            errors=serializer.error_dict,
        )

    data = serializer.validated_data
    hashed_password = hash_password(data["password"])

    try:
        conn = get_connection()
        cursor = conn.cursor()

        cursor.execute("""
            INSERT INTO users (
                first_name, last_name, email,
                password, phone, dob,
                gender, address, role
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            data["first_name"],
            data["last_name"],
            data["email"],
            hashed_password,
            data["phone"],
            data["dob"],
            data["gender"],
            data["address"],
            data["role"],
        ))

        conn.commit()
        return {"message": "User registered successfully"}, 201

    except sqlite3.IntegrityError:
        return error_response(
            message="Email already exists",
            errors={"error": "Email already exists"},
            status_code=409
        )

    finally:
        conn.close()

@route(
    '/login',
    method='POST',
    authenticated=False
)
def user_login_view(request):
    data = request.data
    serializer = UserLoginSerializer(request.data)

    if not serializer.is_valid():
        return error_response(
            message=serializer.error_message,
            errors={"error": serializer.error_message},
        )

    data = serializer.validated_data

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT id, email, password
        FROM users
        WHERE email = ?
    """, (data["email"],))

    user = cursor.fetchone()

    if not user:
        conn.close()
        return error_response(
            message="Invalid email or password",
            errors={"error": "Invalid email or password"},
            status_code=401,
        )

    user_id = user[0]
    stored_password = user[2]

    if not verify_password(data["password"], stored_password):
        conn.close()
        return error_response(
            message="Invalid password",
            errors={"error": "Invalid password"},
            status_code=401,
        )

    session_id = create_session(user_id)

    conn.commit()
    conn.close()

    return success_response(
        message="Logged in successfully",
        data={"session_id": session_id}
    )


@route(
    '/logout',
    method='POST',
    authenticated=True
)
def user_logout_view(request):
    user_id = request.user.get('id')
    delete_session(user_id)
    return success_response(message="Logged out successfully",)