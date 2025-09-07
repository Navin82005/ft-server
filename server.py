import datetime
import threading
from flask import Flask, request, send_file, jsonify
from flask_cors import CORS
import os
import sqlite3

from config import DB_PATH, DRIVE_PATH
from tools.indexing import build_file_index

app = Flask(__name__)
CORS(app)

# Global flags and thread
indexing_done = False
indexing_thread = None

def index_worker():
    """Background thread to build index"""
    global indexing_done
    start_time = datetime.datetime.now()
    build_file_index()
    complete_time = datetime.datetime.now()
    print(complete_time - start_time, "took to index files")
    indexing_done = True


def start_indexing():
    """Start indexing thread only if not running"""
    global indexing_thread
    if indexing_thread is None or not indexing_thread.is_alive():
        indexing_thread = threading.Thread(target=index_worker, daemon=True)
        indexing_thread.start()


def find_files_in_drive(query):
    """Search for files in the SQLite index by exact filename"""
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    cur.execute("SELECT path FROM files WHERE name = ?", (query.lower(),))
    matches = [row[0] for row in cur.fetchall()]
    conn.close()
    return matches

@app.route('/files')
def list_files():
    try:
        conn = sqlite3.connect(DB_PATH)
        cur = conn.cursor()
        cur.execute("SELECT name, path FROM files")
        rows = cur.fetchall()
        conn.close()

        files = []
        for name, path in rows:
            try:
                size = os.path.getsize(path)
            except OSError:
                size = 0
            files.append({"name": name, "size": size, "path": os.path.relpath(path, DRIVE_PATH)})

        return jsonify({"files": files})
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.before_request
def check_index_ready():
    """Block requests until index is ready"""
    global indexing_done
    if not indexing_done:
        return jsonify({"status": "Indexing in progress. Please try again later."}), 503

@app.route('/download')
def download_file_using_path():
    """Serve file for download using query param ?filepath="""
    try:
        # Get query param
        filepath = request.args.get("filepath")
        if not filepath:
            return jsonify({"error": "Missing 'filepath' query parameter"}), 400

        # Extract just the filename for lookup
        filename = os.path.basename(filepath)
        matches = find_files_in_drive(filename)

        if not matches:
            return jsonify({"error": "File not found"}), 404

        if len(matches) > 1:
            return jsonify({
                "error": "Multiple files found",
                "choices": [
                    os.path.relpath(path, DRIVE_PATH) for path in matches
                ]
            }), 300

        file_path = matches[0]
        return send_file(
            file_path,
            as_attachment=True,
            download_name=os.path.basename(file_path)
        )

    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/download/<path:filename>')
def download_file(filename):
    try:
        matches = find_files_in_drive(filename)

        if not matches:
            return jsonify({"error": "File not found"}), 404

        if len(matches) > 1:
            return jsonify({
                "error": "Multiple files found",
                "choices": [
                    os.path.relpath(path, DRIVE_PATH) for path in matches
                ]
            }), 300

        file_path = matches[0]
        return send_file(
            file_path,
            as_attachment=True,
            download_name=os.path.basename(file_path)
        )

    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    start_indexing()  # start the indexing thread safely
    app.run(host='0.0.0.0', port=8080, debug=True)
