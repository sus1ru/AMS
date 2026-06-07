import sqlite3

DB_NAME = "backend/ams.db"


def get_connection():
    conn = sqlite3.connect(DB_NAME)
    conn.execute("PRAGMA foreign_keys = ON")
    return conn


def create_tables():
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
            gender TEXT CHECK (gender IN ('m', 'f', 'o')),
            address VARCHAR(255),
            role TEXT NOT NULL CHECK (
                role IN ('super_admin', 'artist_manager', 'artist')
            ),
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
            updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS artists (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name VARCHAR(255) NOT NULL,
            dob DATETIME,
            gender TEXT CHECK (gender IN ('m', 'f', 'o')),
            address VARCHAR(255),
            first_release_year INTEGER,
            no_of_albums_released INTEGER DEFAULT 0,
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
            updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS songs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            artist_id INTEGER NOT NULL,
            title VARCHAR(255) NOT NULL,
            album_name VARCHAR(255),
            genre TEXT CHECK (
                genre IN ('rnb', 'country', 'classic', 'rock', 'jazz')
            ),
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
            updated_at DATETIME DEFAULT CURRENT_TIMESTAMP,

            FOREIGN KEY (artist_id) REFERENCES artists(id)
                ON DELETE CASCADE
        )
    """)

    conn.commit()
    conn.close()