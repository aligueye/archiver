# Website Archiver

A full-stack app that lets users archive a website snapshot and browse it later including subpages, images, scripts, and styles. All of this is stored offline and navigable like the live site.

## Demo

- Input a URL (e.g., `https://books.toscrape.com`)
- The app crawls and archives all linked pages (up to a depth of 4. Depth is set in crawler.py), saving them locally
- Archived snapshots are viewable from a built-in archive viewer

## Features

- Recursive HTML page crawling (async)
- Saves full snapshots to `archives/<domain>/<timestamp>/`
- Link rewriting to preserve full in-site navigation
- Asset downloading (images, CSS, JS)
- Web UI with live preview of archived snapshots
- Archive history browser with expandable per-site versions

## How to Run

### Backend

```bash
cd backend
python -m venv venv
. venv/Scripts/activate
pip install -r requirements.txt
flask run
```

### Frontend

```bash
cd frontend
npm install
npm run dev # or npm start
```

Visit `http://localhost:5173` to use the app. Make sure the backend is running at `http://localhost:5000`.

## Directory Structure

```
archives/
└── books.toscrape.com/
    └── 2025-07-22T13-11-51/
        ├── index.html
        └── catalogue/
            └── some-book/
                └── index.html
```

## Possible Enhancements

- Scheduled auto-crawls (cron or button-triggered)
- Configurable depth of crawl on the frontend
- Export full archive as downloadable .zip

## Production Considerations

- **Scalable Storage:** Migrate from local filesystem to a cloud solution like AWS S3 with metadata managed in a relational database
- **Dynamic Content Support:** Integrate headless browser tools like Playwright or Puppeteer to capture pages that require JavaScript rendering
- **UI Enhancements:** Add archive deletion, search, filtering, and visual loading indicators to improve usability and manageability
