"""bookviz command-line interface."""

from __future__ import annotations

import argparse
import os
import sys

from .colors import extract_colors
from .fetch import fetch_book, google_books_metadata
from .render_html import render_html
from .render_png import render_png


def main(argv: list[str] | None = None) -> None:
    parser = argparse.ArgumentParser(
        prog="bookviz",
        description='Generate an "every color in <book>" poster from a '
        "public domain text.",
    )
    parser.add_argument("query", nargs="?", help='book title, e.g. "Moby Dick"')
    parser.add_argument("--gutenberg-id", type=int,
                        help="Project Gutenberg book id (skips search)")
    parser.add_argument("--out", default=None,
                        help="output path without extension (default: slug of title)")
    parser.add_argument("--format", default="html", dest="formats",
                        help="comma-separated: html,png (default: html)")
    parser.add_argument("--width", type=int, default=1500,
                        help="PNG width in pixels (default: 1500)")
    parser.add_argument("--credit", default="bookviz",
                        help="credit line, bottom-left of the poster")
    parser.add_argument("--google-api-key",
                        default=os.environ.get("GOOGLE_BOOKS_API_KEY"),
                        help="Google Books API key for metadata enrichment "
                        "(or set GOOGLE_BOOKS_API_KEY). Text always comes "
                        "from Project Gutenberg — Google Books does not "
                        "serve full text.")
    parser.add_argument("--list", action="store_true",
                        help="print the extracted color words and exit")
    args = parser.parse_args(argv)

    if not args.query and args.gutenberg_id is None:
        parser.error("provide a book title or --gutenberg-id")

    book = fetch_book(query=args.query, gutenberg_id=args.gutenberg_id)
    title = book.title.split(";")[0].split(":")[0].strip()

    if args.query:
        meta = google_books_metadata(args.query, api_key=args.google_api_key)
        if meta and meta.get("title"):
            title = meta["title"]

    print(f"Fetched: {book.title} by {book.author} "
          f"(Gutenberg #{book.gutenberg_id}, {len(book.text):,} chars)",
          file=sys.stderr)

    matches = extract_colors(book.text)
    print(f"Found {len(matches)} color words", file=sys.stderr)

    if args.list:
        for m in matches:
            print(m.phrase)
        return

    slug = args.out or "".join(
        c if c.isalnum() else "-" for c in title.lower()).strip("-")
    formats = {f.strip() for f in args.formats.split(",")}
    unknown = formats - {"html", "png"}
    if unknown:
        parser.error(f"unknown format(s): {', '.join(sorted(unknown))}")

    if "html" in formats:
        path = f"{slug}.html"
        with open(path, "w", encoding="utf-8") as f:
            f.write(render_html(matches, title, credit=args.credit))
        print(f"Wrote {path}", file=sys.stderr)
    if "png" in formats:
        path = f"{slug}.png"
        render_png(matches, title, path, credit=args.credit, width=args.width)
        print(f"Wrote {path}", file=sys.stderr)


if __name__ == "__main__":
    main()
