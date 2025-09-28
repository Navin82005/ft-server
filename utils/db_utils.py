from datetime import datetime
import sqlite3

from config import DB_PATH

def init_uploaded_db():
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    cur.execute("""
        CREATE TABLE IF NOT EXISTS uploaded_files (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            original_name TEXT NOT NULL,
            saved_name TEXT NOT NULL,
            size INTEGER NOT NULL,
            path TEXT NOT NULL,
            upload_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    cur.execute("CREATE INDEX IF NOT EXISTS idx_uploaded_saved_name ON uploaded_files(saved_name)")
    conn.commit()
    conn.close()



def insert_uploaded_file(original_name, saved_name, size, path):
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    cur.execute("""
        INSERT INTO uploaded_files (original_name, saved_name, size, path, upload_time)
        VALUES (?, ?, ?, ?, ?)
    """, (original_name, saved_name, size, path, datetime.now()))
    conn.commit()
    conn.close()

