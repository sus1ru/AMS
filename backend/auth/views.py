import sqlite3

from backend.auth.sessions import create_session, delete_session
from backend.auth.utils import hash_password, verify_password
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

    cursor.execute("""
        SELECT
            id, first_name, last_name,
            email, phone, dob,
            gender, address, role,
            created_at, updated_at
        FROM users
    """)

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

    return {"users": users}, 200

@route(
    '/register',
    method='POST',
    authenticated=False
)
def user_register_view(request):
    data = request.data
    required_fields = ["first_name", "last_name", "email", "password", "role"]

    for field in required_fields:
        if not data.get(field):
            return {"error": f"{field} is required"}, 400

    if data["role"] not in ALLOWED_ROLES:
        return {"error": "Invalid role"}, 400

    if data.get("gender") and data["gender"] not in ALLOWED_GENDERS:
        return {"error": "Invalid gender"}, 400

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
        return {"error": "Email already exists"}, 409

    finally:
        conn.close()

@route(
    '/login',
    method='POST',
    authenticated=False
)
def user_login_view(request):
    data = request.data
    if not data.get("email"):
        return {"error": "email is required"}, 400

    if not data.get("password"):
        return {"error": "password is required"}, 400

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
        return {"error": "Invalid email or password"}, 401

    user_id = user[0]
    stored_password = user[2]

    if not verify_password(data["password"], stored_password):
        conn.close()
        return {"error": "Invalid email or password"}, 401

    session_id = create_session(user_id)

    conn.commit()
    conn.close()

    return {
        "message": "Logged in successfully",
        "session_id": session_id
    }, 200


@route(
    '/logout',
    method='POST',
    authenticated=True
)
def user_logout_view(request):
    user_id = request.user.get('id')
    delete_session(user_id)
    return {
        "message": "Logged out successfully",
    }, 200