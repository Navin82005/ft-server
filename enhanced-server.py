import datetime
import threading
from flask import Flask, request, send_file, jsonify
from flask_cors import CORS
import os
import sqlite3


from config import DB_PATH, DRIVE_PATH, UPLOAD_FOLDER
from tools.indexing import build_file_index


import uuid
from werkzeug.utils import secure_filename


app = Flask(__name__)
CORS(app)


os.makedirs(UPLOAD_FOLDER, exist_ok=True)


# Global flags and thread
indexing_done = False
indexing_thread = None


def index_worker():
    global indexing_done
    """Background thread to build index"""
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
    """Search for files in the SQLite index by partial filename match"""
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    # Use LIKE for partial matching instead of exact match
    cur.execute("SELECT name, path FROM files WHERE name LIKE ? ORDER BY name", (f"%{query.lower()}%",))
    matches = cur.fetchall()
    conn.close()
    return matches


def get_file_stats(file_path):
    """Get file statistics safely"""
    try:
        stat = os.stat(file_path)
        return {
            'size': stat.st_size,
            'modified': datetime.datetime.fromtimestamp(stat.st_mtime).isoformat(),
            'created': datetime.datetime.fromtimestamp(stat.st_ctime).isoformat()
        }
    except OSError:
        return {'size': 0, 'modified': None, 'created': None}


@app.route('/files')
def list_files():
    try:
        conn = sqlite3.connect(DB_PATH)
        cur = conn.cursor()
        cur.execute("SELECT name, path FROM files LIMIT 100")  # Limit for performance
        rows = cur.fetchall()
        conn.close()

        files = []
        for name, path in rows:
            stats = get_file_stats(path)
            files.append({
                "name": name, 
                "size": stats['size'], 
                "path": os.path.relpath(path, DRIVE_PATH),
                "modified": stats['modified']
            })

        return jsonify({"files": files, "count": len(files)})
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route('/search')
def search_files():
    """Search for files by query parameter"""
    try:
        query = request.args.get('q', '').strip()
        if not query:
            return jsonify({"error": "Query parameter 'q' is required"}), 400
        
        if len(query) < 2:
            return jsonify({"error": "Query must be at least 2 characters"}), 400
            
        matches = find_files_in_drive(query)
        
        results = []
        for name, path in matches:
            stats = get_file_stats(path)
            results.append({
                "name": name,
                "size": stats['size'],
                "path": os.path.relpath(path, DRIVE_PATH),
                "modified": stats['modified'],
                "full_path": path
            })
        
        return jsonify({
            "query": query,
            "results": results,
            "count": len(results)
        })
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.before_request
def check_index_ready():
    """Block requests until index is ready"""
    global indexing_done
    if not indexing_done and request.endpoint not in ['upload_file', None]:
        return jsonify({"status": "Indexing in progress. Please try again later."}), 503


@app.route('/status')
def get_status():
    """Get server status"""
    global indexing_done
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    cur.execute("SELECT COUNT(*) FROM files")
    total_files = cur.fetchone()[0]
    conn.close()
    
    return jsonify({
        "indexing_complete": indexing_done,
        "total_files": total_files,
        "upload_folder": UPLOAD_FOLDER
    })


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
                    os.path.relpath(path, DRIVE_PATH) for name, path in matches
                ]
            }), 300

        file_path = matches[0][1]  # Get path from tuple
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
                    os.path.relpath(path, DRIVE_PATH) for name, path in matches
                ]
            }), 300

        file_path = matches[0][1]  # Get path from tuple
        return send_file(
            file_path,
            as_attachment=True,
            download_name=os.path.basename(file_path)
        )

    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/upload", methods=["POST"])
def upload_file():
    """Enhanced file upload with better validation and response"""
    try:
        # Check if files were sent
        if "file" not in request.files:
            return jsonify({"error": "No file part in request"}), 400

        files = request.files.getlist("file")
        
        if not files or all(f.filename == "" for f in files):
            return jsonify({"error": "No files selected"}), 400

        uploaded_files = []
        errors = []

        for f in files:
            if f and f.filename and f.filename.strip():
                try:
                    # Validate file size (e.g., 100MB limit)
                    f.seek(0, os.SEEK_END)
                    file_size = f.tell()
                    f.seek(0)
                    
                    if file_size > 100 * 1024 * 1024:  # 100MB
                        errors.append(f"File '{f.filename}' exceeds 100MB limit")
                        continue
                    
                    # Generate unique filename
                    original_filename = secure_filename(f.filename)
                    name, ext = os.path.splitext(original_filename)
                    unique_filename = f"{name}_{uuid.uuid4().hex[:8]}{ext}"
                    
                    filepath = os.path.join(UPLOAD_FOLDER, unique_filename)
                    f.save(filepath)
                    
                    uploaded_files.append({
                        "original_name": f.filename,
                        "saved_name": unique_filename,
                        "size": file_size,
                        "path": filepath
                    })
                    
                except Exception as e:
                    errors.append(f"Error uploading '{f.filename}': {str(e)}")

        if uploaded_files:
            response_data = {
                "message": f"Successfully uploaded {len(uploaded_files)} file(s)",
                "uploaded": uploaded_files
            }
            if errors:
                response_data["warnings"] = errors
            return jsonify(response_data), 200
        else:
            return jsonify({
                "error": "No files were uploaded successfully",
                "details": errors
            }), 400

    except Exception as e:
        return jsonify({"error": f"Upload failed: {str(e)}"}), 500


@app.route("/uploaded-files")
def list_uploaded_files():
    """List files in the upload folder"""
    try:
        if not os.path.exists(UPLOAD_FOLDER):
            return jsonify({"files": [], "count": 0})
            
        files = []
        for filename in os.listdir(UPLOAD_FOLDER):
            filepath = os.path.join(UPLOAD_FOLDER, filename)
            if os.path.isfile(filepath):
                stats = get_file_stats(filepath)
                files.append({
                    "name": filename,
                    "size": stats['size'],
                    "modified": stats['modified'],
                    "path": filepath
                })
        
        # Sort by modification time, newest first
        files.sort(key=lambda x: x['modified'] or '', reverse=True)
        
        return jsonify({"files": files, "count": len(files)})
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500


if __name__ == "__main__":
    # Prevent double-start in debug mode
    if os.environ.get("WERKZEUG_RUN_MAIN") == "true" or not app.debug:
        start_indexing()
    app.run(host="0.0.0.0", port=8080, debug=True, use_reloader=False)