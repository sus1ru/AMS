import secrets
import sqlite3

from backend.auth.utils import hash_password, verify_password
from backend.database import get_connection

ALLOWED_ROLES = {"super_admin", "artist_manager", "artist"}
ALLOWED_GENDERS = {"m", "f", "o"}

def user_list_view():
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


def user_register_view(data):
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
