from flask import Flask, send_file, jsonify, request
from flask_cors import CORS
import os
from pathlib import Path

app = Flask(__name__)
CORS(app)  # Enable CORS for mobile access

DRIVE_PATH = "/mnt/drive-x1"  # Your mounted external drive


@app.route('/download/<filename>')
def download_file(filename):
    """Serve file for download"""
    try:
        # Find file in drive
        file_path = find_file_in_drive(filename)
        if not file_path:
            return jsonify({"error": "File not found"}), 404

        return send_file(
            file_path,
            as_attachment=True,
            download_name=filename
        )
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route('/files')
def list_files():
    """List available files"""
    try:
        files = []
        for root, dirs, filenames in os.walk(DRIVE_PATH):
            for filename in filenames:
                file_path = os.path.join(root, filename)
                files.append({
                    "name": filename,
                    "size": os.path.getsize(file_path),
                    "path": os.path.relpath(file_path, DRIVE_PATH)
                })
        return jsonify({"files": files})
    except Exception as e:
        return jsonify({"error": str(e)}), 500


def find_file_in_drive(filename):
    """Search for file in drive directory"""
    for root, dirs, files in os.walk(DRIVE_PATH):
        for file in files:
            if filename.lower() in file.lower():
                return os.path.join(root, file)
    return None


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080, debug=True)
