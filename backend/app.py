import os
from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
from utils import get_archive_path
from crawler import crawl

app = Flask(__name__)
CORS(app)


@app.route("/archive", methods=["POST"])
def archive():
    data = request.get_json()
    url = data.get("url")
    try:
        archive_path, timestamp = get_archive_path(url)
        crawl(url, archive_path, timestamp, max_depth=2)
    except Exception as e:
        return {"status": "error", "message": str(e)}, 400

    return {"status": "ok", "archive_path": archive_path}


@app.route("/archives/<domain>", methods=["GET"])
def list_archives(domain):
    path = os.path.join("archives", domain)
    if not os.path.exists(path):
        return jsonify([])

    versions = sorted(os.listdir(path))
    return jsonify(versions)


@app.route("/archive/<domain>/<timestamp>/<path:filename>")
def serve_archived_file(domain, timestamp, filename):
    archive_dir = os.path.join("archives", domain, timestamp)
    return send_from_directory(archive_dir, filename)


@app.route("/archive/<domain>/<timestamp>/")
def serve_index(domain, timestamp):
    archive_dir = os.path.join("archives", domain, timestamp)
    print(f"Serving index from {archive_dir}")
    if not os.path.exists(archive_dir):
        return jsonify({"error": "Archive not found"}), 404
    else:
        print(f"Found index.html in {archive_dir}")
    return send_from_directory(archive_dir, "index.html")
