import sys
import os
from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
from utils import get_archive_path
from crawler import crawl
import asyncio


app = Flask(__name__)
CORS(app)

# Set the default event loop policy for Windows(noisy warnings/errors for asyncio on Windows for Python < 3.8)
if sys.platform == "win32":
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())


@app.route("/archive", methods=["POST"])
def archive():
    data = request.get_json()
    url = data.get("url")
    try:
        archive_path, timestamp = get_archive_path(url)

        import aiohttp

        async def run_crawl():
            async with aiohttp.ClientSession() as session:
                await crawl(url, archive_path, timestamp, session=session)
        asyncio.run(run_crawl())
    except Exception as e:
        return {"status": "error", "message": str(e)}, 400

    return {"status": "ok", "archive_path": archive_path}


@app.route("/archives", methods=["GET"])
def list_archives():
    archives = []
    for domain in os.listdir("archives"):
        domain_path = os.path.join("archives", domain)
        if os.path.isdir(domain_path):
            versions = sorted(os.listdir(domain_path))
            archives.append({"domain": domain, "versions": versions})
    return jsonify(archives)


@app.route("/archives/<domain>", methods=["GET"])
def list_archives_by_domain(domain):
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
    return send_from_directory(archive_dir, "index.html")
