from flask import Flask, request
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
        archive_path = get_archive_path(url)
        crawl(url, archive_path, max_depth=2)
    except Exception as e:
        return {"status": "error", "message": str(e)}, 400

    return {"status": "ok", "archive_path": archive_path}