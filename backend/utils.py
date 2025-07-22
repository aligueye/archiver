import os
from urllib.parse import urlparse
from datetime import datetime


def get_archive_path(url):
    parsed = urlparse(url)
    domain = parsed.netloc.replace("www.", "")
    timestamp = datetime.now().strftime("%Y-%m-%dT%H-%M-%S")
    path = os.path.join("archives", domain, timestamp)
    os.makedirs(path, exist_ok=True)
    return path, timestamp


def is_same_domain(base_url, target_url):
    return urlparse(base_url).netloc == urlparse(target_url).netloc


def normalize_url(url):
    parsed = urlparse(url)
    path = parsed.path
    if path.endswith("index.html"):
        path = path[: -len("index.html")]
    path = path.rstrip("/")
    clean = parsed._replace(netloc=parsed.netloc.lower(),  # removes case sensitivity
                            path=path,  # removes trailing slashes
                            fragment=""  # removes URL fragment
                            )
    return clean.geturl()
