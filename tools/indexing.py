import os
import sqlite3
import traceback
import smtplib
from email.mime.text import MIMEText

from config import DB_PATH, DRIVE_PATH, INDEX_LOG_FILE, SKIP_FOLDERS


# Store errors during one indexing run
_indexing_errors = []

def log_error(subject: str, message: str):
    """Log error to file and memory (no email yet)"""
    with open(INDEX_LOG_FILE, "a") as f:
        f.write(subject + "\n" + message + "\n\n")
    _indexing_errors.append(f"{subject}\n{message}")


def send_error_summary():
    """Send a single email with all errors if any"""
    if not _indexing_errors:
        return  # nothing to notify

    summary = "\n\n".join(_indexing_errors)
    subject = f"Indexing completed with {len(_indexing_errors)} errors"

    try:
        from config import ADMIN_EMAIL, SMTP_SERVER, SMTP_PORT, SMTP_USER, SMTP_PASS
        msg = MIMEText(summary)
        msg["Subject"] = subject
        msg["From"] = SMTP_USER
        msg["To"] = ADMIN_EMAIL

        with smtplib.SMTP(SMTP_SERVER, SMTP_PORT) as server:
            server.starttls()
            server.login(SMTP_USER, SMTP_PASS)
            server.send_message(msg)
    except ImportError:
        pass  # email settings not configured
    except Exception as e:
        with open(INDEX_LOG_FILE, "a") as f:
            f.write("Email notification failed: " + str(e) + "\n")


def normalize_path(path: str) -> str:
    """Resolve symlinks and return absolute normalized path"""
    return os.path.realpath(os.path.abspath(os.path.expanduser(path)))


def init_db():
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
    conn = sqlite3.connect(DB_PATH)
    conn.execute("DELETE FROM files")
    conn.commit()
    conn.close()


def build_file_index():
    """Scan drive once and store files in SQLite"""
    try:
        # reset error buffer for this run
        global _indexing_errors
        _indexing_errors = []

        init_db()
        clear_index()

        print("Indexing drive...")
        print("Drive to be indexed:", DRIVE_PATH)
        print("Folders to be skipped:", SKIP_FOLDERS)

        conn = sqlite3.connect(DB_PATH)
        cur = conn.cursor()

        batch = []
        seen_paths = set()

        for root, dirs, files in os.walk(os.path.abspath(DRIVE_PATH), topdown=True):
            dirs[:] = [d for d in dirs if d not in SKIP_FOLDERS]

            for file in files:
                try:
                    full_path = normalize_path(os.path.join(root, file))
                except PermissionError as e:
                    log_error("Indexing error", f"Permission denied on {file}: {e}")
                    continue
                except Exception as e:
                    log_error("Indexing error", f"Error on file {file}: {e}")
                    continue

                if full_path in seen_paths:
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

    except Exception:
        error_msg = traceback.format_exc()
        log_error("Critical Indexing Failure", error_msg)
        raise
    finally:
        # ✅ Always send summary after indexing finishes
        send_error_summary()
