import sqlite3

from backend.config import settings

ALLOWED_ROLES = ["super_admin", "artist_manager", "artist"]
ALLOWED_GENDERS = ["m", "f", "o"]
ALLOWED_GENRES = ['rnb', 'country', 'classic', 'rock', 'jazz']

def get_connection():
    conn = sqlite3.connect(settings.db_name)
    conn.execute("PRAGMA foreign_keys = ON")
    return conn


def setup_db():
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            first_name VARCHAR(255) NOT NULL,
            last_name VARCHAR(255) NOT NULL,
            email VARCHAR(255) NOT NULL UNIQUE,
            password VARCHAR(500) NOT NULL,
            phone VARCHAR(20),
            dob DATETIME,
            gender TEXT CHECK (gender IN ({genders})),
            address VARCHAR(255),
            role TEXT NOT NULL CHECK (
                role IN ({roles})
            ),
            created_at TEXT DEFAULT (strftime('%Y-%m-%dT%H:%M:%f+00:00', 'now')),
            updated_at TEXT DEFAULT (strftime('%Y-%m-%dT%H:%M:%f+00:00', 'now'))
        )
    """.format(roles=str(ALLOWED_ROLES)[1:-1], genders=str(ALLOWED_GENDERS)[1:-1]))

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS artists (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name VARCHAR(255) NOT NULL,
            dob DATETIME,
            gender TEXT CHECK (gender IN ({genders})),
            address VARCHAR(255),
            first_release_year INTEGER,
            no_of_albums_released INTEGER DEFAULT 0,
            created_at TEXT DEFAULT (strftime('%Y-%m-%dT%H:%M:%f+00:00', 'now')),
            updated_at TEXT DEFAULT (strftime('%Y-%m-%dT%H:%M:%f+00:00', 'now'))
        )
    """.format(genders=str(ALLOWED_GENDERS)[1:-1]))

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS songs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            artist_id INTEGER NOT NULL,
            title VARCHAR(255) NOT NULL,
            album_name VARCHAR(255),
            genre TEXT CHECK (
                genre IN ({genres})
            ),
            created_at TEXT DEFAULT (strftime('%Y-%m-%dT%H:%M:%f+00:00', 'now')),
            updated_at TEXT DEFAULT (strftime('%Y-%m-%dT%H:%M:%f+00:00', 'now')),

            FOREIGN KEY (artist_id) REFERENCES artists(id)
                ON DELETE CASCADE
        )
    """.format(genres=str(ALLOWED_GENRES)[1:-1]))

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS sessions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            session_id VARCHAR(255) NOT NULL UNIQUE,
            user_id INTEGER NOT NULL,
            created_at TEXT DEFAULT (strftime('%Y-%m-%dT%H:%M:%f+00:00', 'now')),
            expires_at DATETIME,
            FOREIGN KEY (user_id) REFERENCES users(id)
                ON DELETE CASCADE
        )
    """)

    conn.commit()
    conn.close()
