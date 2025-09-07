import os
import sqlite3

from config import DB_PATH, DRIVE_PATH, SKIP_FOLDERS

def normalize_path(path: str) -> str:
    """Resolve symlinks and return absolute normalized path"""
    return os.path.realpath(os.path.abspath(os.path.expanduser(path)))


def init_db():
    """Create SQLite DB and table if not exists"""
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    cur.execute("""
        CREATE TABLE IF NOT EXISTS files (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            path TEXT NOT NULL
        )
    """)
    cur.execute("CREATE INDEX IF NOT EXISTS idx_name ON files(name)")
    conn.commit()
    conn.close()


def clear_index():
    """Clear existing index"""
    conn = sqlite3.connect(DB_PATH)
    conn.execute("DELETE FROM files")
    conn.commit()
    conn.close()


def build_file_index():
    """Scan drive once and store files in SQLite"""
    init_db()
    clear_index()
    
    print("Indexing drive...")
    print("Drives to be indexed:", DRIVE_PATH)
    print("Folders to be skipped:", SKIP_FOLDERS)

    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()

    batch = []
    seen_paths = set()  # prevent duplicates

    for root, dirs, files in os.walk(os.path.abspath(DRIVE_PATH)):
        dirs[:] = [d for d in dirs if d not in SKIP_FOLDERS]

        for file in files:
            full_path = normalize_path(os.path.join(root, file))
            if full_path in seen_paths:  # skip duplicates
                continue
            seen_paths.add(full_path)

            batch.append((file.lower(), full_path))


            if len(batch) >= 500:
                cur.executemany("INSERT INTO files (name, path) VALUES (?, ?)", batch)
                conn.commit()
                batch.clear()

    if batch:
        cur.executemany("INSERT INTO files (name, path) VALUES (?, ?)", batch)
        conn.commit()

    conn.close()


def find_files(query):
    """Search for exact filename in SQLite index"""
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    cur.execute("SELECT path FROM files WHERE name = ?", (query.lower(),))
    results = [row[0] for row in cur.fetchall()]
    conn.close()
    return results
