import sqlite3
import os
from werkzeug.security import generate_password_hash

DB_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "grievance.db")

def get_db_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON;")
    return conn

def init_db():
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT UNIQUE NOT NULL,
                password_hash TEXT NOT NULL,
                role TEXT NOT NULL CHECK(role IN ('student', 'admin'))
            );
        """)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS complaints (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                complaint_id TEXT UNIQUE NOT NULL,
                student_id INTEGER NOT NULL,
                title TEXT NOT NULL,
                description TEXT NOT NULL,
                location TEXT NOT NULL,
                category TEXT NOT NULL,
                subcategory TEXT,
                priority TEXT NOT NULL CHECK(priority IN ('High', 'Medium', 'Low')),
                status TEXT NOT NULL DEFAULT 'Submitted' CHECK(status IN ('Submitted', 'In Progress', 'Resolved')),
                assigned_dept TEXT DEFAULT 'Unassigned',
                resolution_notes TEXT DEFAULT '',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (student_id) REFERENCES users (id) ON DELETE CASCADE
            );
        """)
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_status ON complaints(status);")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_cat ON complaints(category);")

        cursor.execute("""
            INSERT OR IGNORE INTO users (id, username, password_hash, role)
            VALUES 
            (1, 'admin', ?, 'admin'),
            (2, 'student', ?, 'student')
        """, (generate_password_hash("Admin@123"), generate_password_hash("Student@123")))
        conn.commit()

if __name__ == "__main__":
    init_db()
