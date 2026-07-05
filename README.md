# bookviz

Generate **"every color in \<book\>"** posters from public domain texts — every color word in a book, in order of appearance, rendered in its own color. Inspired by [barelymaps](https://barelymaps.com)' *every color in Moby-Dick* poster.

![every color in Moby Dick](examples/moby-dick.png)

## Usage

```bash
# HTML poster (no dependencies, stdlib only)
python3 -m bookviz "Moby Dick"

# PNG poster too (needs pillow)
pip install pillow
python3 -m bookviz "Moby Dick" --format html,png

# Skip search, use a Project Gutenberg id directly
python3 -m bookviz --gutenberg-id 2701

# Just print the color words
python3 -m bookviz "Dracula" --list
```

Or install it:

```bash
pip install ".[png]"
bookviz "The Wonderful Wizard of Oz" --format png --width 2000
```

Options: `--out` (output path without extension), `--width` (PNG pixels), `--credit` (bottom-left credit line), `--google-api-key` (see below).

## How it works

1. **Fetch** — searches Project Gutenberg via the [Gutendex](https://gutendex.com) API and downloads the plain-text edition, stripping the Gutenberg boilerplate.
2. **Extract** — scans the text against a lexicon of ~150 color words, including literary/archaic ones (`brimstone`, `sable`, `swart`, `vermillion`), inflections (`reddening`, `whitest`), hyphenated compounds (`snow-white`, `grey-headed`, `coffin-coloured`), and modifier phrases (`dark purplish yellow`, `faded walnut`).
3. **Render** — lays the words out justified on a near-black poster, each in its display color. HTML output is dependency-free; PNG uses Pillow.

### Why not the Google Books API for text?

The Google Books API serves **metadata and preview snippets only** — it never returns machine-readable full text, even for public domain volumes (the "download" links it exposes go through captcha-gated web pages, and anonymous API access is heavily quota-limited). So bookviz uses Google Books optionally for metadata enrichment (canonical title for the poster caption, via `--google-api-key` or `GOOGLE_BOOKS_API_KEY`), and Project Gutenberg for the actual text — the only major source with full public domain texts behind a plain programmatic API.

## More poster ideas

See [IDEAS.md](IDEAS.md) for a brainstorm of similar poster-style visualizations for books, movies, and TV.

## License

MIT. Book texts are public domain via [Project Gutenberg](https://www.gutenberg.org).
