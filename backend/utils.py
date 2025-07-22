import os
from urllib.parse import urlparse
from datetime import datetime

def get_archive_path(url):
    parsed = urlparse(url)
    domain = parsed.netloc.replace("www.", "")
    timestamp = datetime.now().strftime("%Y-%m-%dT%H-%M-%S")
    path = os.path.join("archives", domain, timestamp)
    os.makedirs(path, exist_ok=True)
    return path