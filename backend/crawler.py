import os
import asyncio
from bs4 import BeautifulSoup
from urllib.parse import urlparse, urljoin

DEFAULT_TIMEOUT = 20


def is_same_domain(base_url, target_url):
    return urlparse(base_url).netloc == urlparse(target_url).netloc


def normalize_url(url):
    parsed = urlparse(url)
    path = parsed.path
    if path.endswith("index.html"):
        path = path[: -len("index.html")]
    path = path.rstrip("/")
    clean = parsed._replace(
        netloc=parsed.netloc.lower(), path=path, fragment="")
    return clean.geturl()


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


async def download_asset(session, asset_url, asset_path):
    headers = {"User-Agent": "Mozilla/5.0"}
    try:
        async with session.get(asset_url, headers=headers, timeout=DEFAULT_TIMEOUT) as res:
            if res.status != 200:
                print(f"Failed to download asset {asset_url}: {res.status}")
                return
            os.makedirs(os.path.dirname(asset_path), exist_ok=True)
            with open(asset_path, "wb") as f:
                f.write(await res.read())
    except Exception as e:
        print(
            f"Failed to download asset {asset_url} {e.__class__.__name__}: {e}")


async def rewrite_asset_links(soup, page_url, base_path, timestamp, session):
    tags = [("img", "src", "img"), ("script", "src", "js"),
            ("link", "href", "css")]
    parsed_url = urlparse(page_url)
    domain = parsed_url.netloc.replace("www.", "")
    archive_url_prefix = f"/archive/{domain}/{timestamp}/"

    tasks = []

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

            el[attr] = archive_url_prefix + f"assets/{subfolder}/{filename}"
            tasks.append(download_asset(session, full_url, local_abs_path))

    await asyncio.gather(*tasks)


def rewrite_page_links(soup, page_url, timestamp):
    parsed_url = urlparse(page_url)
    domain = parsed_url.netloc.replace("www.", "")
    archive_url_prefix = f"/archive/{domain}/{timestamp}/"

    for a in soup.find_all("a", href=True):
        href = a["href"]

        if href.startswith(("#", "mailto:", "javascript:")):
            continue

        full_url = urljoin(page_url, href)

        if not is_same_domain(page_url, full_url):
            continue

        parsed = urlparse(full_url)
        rel_path = parsed.path.lstrip("/")

        # Normalize to include index.html where appropriate
        if rel_path == "":
            rel_path = "index.html"
        elif rel_path.endswith("/"):
            rel_path += "index.html"
        elif not rel_path.endswith(".html"):
            rel_path = os.path.join(rel_path, "index.html")

        a["href"] = archive_url_prefix + rel_path


async def crawl(url, base_path, timestamp, visited=None, depth=0, max_depth=2, session=None):
    if visited is None:
        visited = set()
    normalized_url = normalize_url(url)
    if depth > max_depth or normalized_url in visited:
        return
    visited.add(normalized_url)

    try:
        async with session.get(url, timeout=DEFAULT_TIMEOUT) as res:
            if res.status != 200:
                print(f"[depth={depth}] Failed to fetch {url}: {res.status}")
                return
            html = await res.text()
    except Exception as e:
        print(
            f"[depth={depth}] Failed to fetch {url} {e.__class__.__name__}: {e}")
        return

    print(f"[depth={depth}] Archiving: {url}")
    soup = BeautifulSoup(html, "html.parser")

    # Extract links BEFORE rewriting
    links = [a.get("href") for a in soup.find_all("a", href=True)]
    full_links = []
    for link in links:
        if not link or link.startswith("#") or link.startswith("mailto:"):
            continue
        full_url = urljoin(url, link)
        normalized_link = normalize_url(full_url)
        if is_same_domain(url, full_url) and normalized_link not in visited:
            full_links.append((full_url, depth + 1))

    # Rewrite and save current page
    await rewrite_asset_links(soup, url, base_path, timestamp, session)
    rewrite_page_links(soup, url, timestamp)
    save_html(str(soup), base_path, url)

    # Recursively crawl subpages in parallel
    tasks = [
        crawl(link, base_path, timestamp, visited,
              new_depth, max_depth, session)
        for link, new_depth in full_links
    ]
    await asyncio.gather(*tasks)
