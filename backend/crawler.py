import os
import requests
from bs4 import BeautifulSoup
from urllib.parse import urlparse, urljoin

from utils import normalize_url, is_same_domain


def save_html(content, base_path, url):
    rel_path = urlparse(url).path.strip("/")
    if rel_path in ("", "index.html"):
        filepath = os.path.join(base_path, "index.html")
        with open(filepath, "w", encoding="utf-8") as f:
            f.write(content)
    elif rel_path.endswith(".html"):
        full_path = os.path.join(base_path, rel_path)
        os.makedirs(os.path.dirname(full_path), exist_ok=True)
        with open(full_path, "w", encoding="utf-8") as f:
            f.write(content)
    else:
        full_path = os.path.join(base_path, rel_path)
        os.makedirs(full_path, exist_ok=True)
        filepath = os.path.join(full_path, "index.html")
        with open(filepath, "w", encoding="utf-8") as f:
            f.write(content)


def download_asset(asset_url, asset_path):
    try:
        res = requests.get(asset_url, timeout=10)
        res.raise_for_status()
    except Exception as e:
        print(f"Failed to download asset {asset_url}: {e}")
        return None

    os.makedirs(os.path.dirname(asset_path), exist_ok=True)
    with open(asset_path, "wb") as f:
        f.write(res.content)
    return asset_path


def rewrite_asset_links(soup, page_url, base_path, timestamp):
    tags = [
        ("img", "src", "img"),
        ("script", "src", "js"),
        ("link", "href", "css"),
    ]

    parsed_url = urlparse(page_url)
    domain = parsed_url.netloc.replace("www.", "")
    archive_url_prefix = f"/archive/{domain}/{timestamp}/"

    for tag, attr, subfolder in tags:
        for el in soup.find_all(tag):
            url = el.get(attr)
            if not url or url.startswith("data:") or url.startswith("mailto:"):
                continue

            full_url = urljoin(page_url, url)
            parsed = urlparse(full_url)
            filename = os.path.basename(parsed.path)
            ext = os.path.splitext(filename)[1]
            filename = filename if ext else filename + ".bin"

            local_rel_path = os.path.join("assets", subfolder, filename)
            local_abs_path = os.path.join(base_path, local_rel_path)

            if download_asset(full_url, local_abs_path):
                el[attr] = archive_url_prefix + \
                    f"assets/{subfolder}/{filename}"


def rewrite_page_links(soup, page_url, timestamp):
    parsed = urlparse(page_url)
    domain = parsed.netloc.replace("www.", "")
    archive_url_prefix = f"/archive/{domain}/{timestamp}/"

    for a in soup.find_all("a", href=True):
        href = a["href"]

        if href.startswith(("#", "mailto:", "javascript:")):
            continue

        full_url = urljoin(page_url, href)

        if is_same_domain(page_url, full_url):
            target_path = urlparse(full_url).path.lstrip("/")
            a["href"] = archive_url_prefix + target_path


def crawl(url, base_path, timestamp, visited=None, depth=0, max_depth=2):
    if visited is None:
        visited = set()
    normalized_url = normalize_url(url)
    if depth > max_depth or normalized_url in visited:
        return
    visited.add(normalized_url)
    print(f"[depth={depth}] Archiving: {url}")

    try:
        res = requests.get(url, timeout=10)
        res.raise_for_status()
    except Exception as e:
        print(f"Failed to fetch {url}: {e}")
        return

    html = res.text
    soup = BeautifulSoup(html, "html.parser")

    links = [a.get("href") for a in soup.find_all("a", href=True)]

    for link in links:
        if not link or link.startswith("#"):
            continue
        full_link = urljoin(url, link)
        normalized_link = normalize_url(full_link)
        if is_same_domain(url, full_link) and normalized_link not in visited:
            crawl(full_link, base_path, timestamp,
                  visited, depth + 1, max_depth)

    rewrite_asset_links(soup, url, base_path, timestamp)
    rewrite_page_links(soup, url, timestamp)

    final_html = str(soup)
    save_html(final_html, base_path, url)
