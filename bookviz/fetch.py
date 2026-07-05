"""Fetching book text and metadata.

Text comes from Project Gutenberg (via the Gutendex API) because it is the
only major source that serves the *full text* of public domain books over a
plain programmatic API. The Google Books API is used, when available, to
enrich metadata (canonical title/author) — it does not expose full text,
even for public domain volumes.
"""

from __future__ import annotations

import json
import re
import urllib.parse
import urllib.request
from dataclasses import dataclass

GUTENDEX_URL = "https://gutendex.com/books/"
GOOGLE_BOOKS_URL = "https://www.googleapis.com/books/v1/volumes"
USER_AGENT = "bookviz/0.1 (+https://github.com/braeden/bookviz)"


@dataclass
class Book:
    title: str
    author: str
    gutenberg_id: int
    text: str


def _get(url: str, timeout: int = 60) -> bytes:
    req = urllib.request.Request(url, headers={"User-Agent": USER_AGENT})
    with urllib.request.urlopen(req, timeout=timeout) as resp:
        return resp.read()


def _get_json(url: str) -> dict:
    return json.loads(_get(url).decode("utf-8"))


def search_gutenberg(query: str) -> dict:
    """Return the most-downloaded Gutendex record matching the query."""
    url = f"{GUTENDEX_URL}?search={urllib.parse.quote(query)}"
    data = _get_json(url)
    results = data.get("results") or []
    if not results:
        raise SystemExit(f"No Project Gutenberg match for {query!r}")
    return results[0]  # Gutendex sorts by download count


def _plain_text_url(record: dict) -> str:
    for mime, url in record.get("formats", {}).items():
        if mime.startswith("text/plain") and not url.endswith(".zip"):
            return url
    raise SystemExit(f"No plain-text format for Gutenberg #{record.get('id')}")


def strip_gutenberg_boilerplate(raw: str) -> str:
    """Cut the Project Gutenberg license header/footer from the text."""
    start = re.search(r"\*\*\* ?START OF.*?\*\*\*", raw)
    end = re.search(r"\*\*\* ?END OF.*?\*\*\*", raw)
    lo = start.end() if start else 0
    hi = end.start() if end else len(raw)
    return raw[lo:hi]


def book_from_record(record: dict) -> Book:
    raw = _get(_plain_text_url(record)).decode("utf-8", errors="replace")
    authors = record.get("authors") or []
    author = authors[0]["name"] if authors else "Unknown"
    # Gutendex names are "Last, First"
    if "," in author:
        last, _, first = author.partition(",")
        author = f"{first.strip()} {last.strip()}".strip()
    return Book(
        title=record.get("title", "Unknown"),
        author=author,
        gutenberg_id=record["id"],
        text=strip_gutenberg_boilerplate(raw),
    )


def fetch_book(query: str | None = None, gutenberg_id: int | None = None) -> Book:
    if gutenberg_id is not None:
        record = _get_json(f"{GUTENDEX_URL}{gutenberg_id}")
    else:
        assert query is not None
        record = search_gutenberg(query)
    return book_from_record(record)


def short_title(title: str) -> str:
    """'Moby Dick; Or, The Whale' -> 'Moby Dick'."""
    return title.split(";")[0].split(":")[0].strip()


def top_records(n: int, language: str = "en") -> list[dict]:
    """The n most-downloaded Gutendex records with a plain-text format."""
    records: list[dict] = []
    url: str | None = f"{GUTENDEX_URL}?languages={language}"
    while url and len(records) < n:
        data = _get_json(url)
        for rec in data.get("results", []):
            has_text = any(
                m.startswith("text/plain") and not u.endswith(".zip")
                for m, u in rec.get("formats", {}).items()
            )
            if has_text:
                records.append(rec)
                if len(records) == n:
                    break
        url = data.get("next")
    return records


def fetch_top_books(n: int, language: str = "en", workers: int = 6) -> list[Book]:
    """Fetch the n most-downloaded books, preserving popularity order."""
    from concurrent.futures import ThreadPoolExecutor

    records = top_records(n, language=language)

    def safe(rec: dict) -> Book | None:
        try:
            return book_from_record(rec)
        except Exception:
            return None

    with ThreadPoolExecutor(max_workers=workers) as pool:
        books = list(pool.map(safe, records))
    return [b for b in books if b is not None]


def google_books_metadata(query: str, api_key: str | None = None) -> dict | None:
    """Optional metadata enrichment via the Google Books API.

    Returns {'title', 'authors', 'publishedDate'} or None on any failure
    (no key, quota exceeded, no match). Never raises: the poster can always
    fall back to Gutenberg metadata.
    """
    params = {"q": query, "maxResults": "1", "printType": "books"}
    if api_key:
        params["key"] = api_key
    url = f"{GOOGLE_BOOKS_URL}?{urllib.parse.urlencode(params)}"
    try:
        data = _get_json(url)
        info = data["items"][0]["volumeInfo"]
        return {
            "title": info.get("title"),
            "authors": info.get("authors", []),
            "publishedDate": info.get("publishedDate"),
        }
    except Exception:
        return None
