import os
import requests
from bs4 import BeautifulSoup
from urllib.parse import urlparse, urljoin

def is_same_domain(base_url, target_url):
    return urlparse(base_url).netloc == urlparse(target_url).netloc

def sanitize_path(path):
    clean = path.strip("/").replace("/", "_")
    return clean if clean else "index"

def save_html(content, base_path, rel_path):
    full_path = os.path.join(base_path, rel_path)
    os.makedirs(full_path, exist_ok=True)
    with open(os.path.join(full_path, "index.html"), "w", encoding="utf-8") as f:
        f.write(content)

def crawl(url, base_path, visited=None, depth=0, max_depth=2):
    if visited is None:
        visited = set()
    if depth > max_depth or url in visited:
        return
    visited.add(url)

    try:
        res = requests.get(url, timeout=10)
        res.raise_for_status()
    except Exception as e:
        print(f"Failed to fetch {url}: {e}")
        return

    html = res.text
    parsed_url = urlparse(url)
    rel_path = sanitize_path(parsed_url.path)
    save_html(html, base_path, rel_path)

    soup = BeautifulSoup(html, "html.parser")
    links = [a.get("href") for a in soup.find_all("a", href=True)]

    for link in links:
        full_url = urljoin(url, link)
        if is_same_domain(url, full_url) and full_url not in visited:
            crawl(full_url, base_path, visited, depth + 1, max_depth)