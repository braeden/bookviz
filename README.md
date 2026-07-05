# bookviz

Poster-style visualizations of public domain books, pulled straight from Project Gutenberg. Three visualizations so far:

- **every color in \<book\>** — every color word, in order of appearance, rendered in its own color. Inspired by [barelymaps](https://barelymaps.com)' *every color in Moby-Dick* poster.
- **sentence-length skyline** — one thin bar per sentence, height = word count: the rhythm of the author's prose as a city skyline.
- **palette set** — the Gutenberg Top 20, one color-barcode row per book. The palettes alone identify the books.

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

# Sentence-length skyline (needs pillow)
python3 -m bookviz "Moby Dick" --viz skyline

# Palette-set poster of the 20 most-downloaded Gutenberg books (needs pillow)
python3 -m bookviz --top 20
```

## Sentence-length skyline

One bar per sentence, height = word count, wrapped into rows. Questions are blue, exclamations gold. Tables of contents, chapter headings, and other all-caps front matter are stripped first so only prose sentences count:

![sentence-length skyline of Moby Dick](examples/moby-dick-skyline.png)

## The Gutenberg Top 20

Every color in each of the 20 most-downloaded Gutenberg books, one barcode row per book, each sequence stretched to the same width. The palettes identify the books: Moby Dick reads white, Dracula red, *The City of God* gold, Middlemarch pink and grey:

![every color in the Gutenberg Top 20](examples/gutenberg-top-20.png)

Or install it:

```bash
pip install ".[png]"
bookviz "The Wonderful Wizard of Oz" --format png --width 2000
```

Options: `--viz colors|skyline`, `--top N` (palette-set poster), `--out` (output path without extension), `--width` (PNG pixels), `--google-api-key` (see below).

## How it works

1. **Fetch** — searches Project Gutenberg via the [Gutendex](https://gutendex.com) API and downloads the plain-text edition, stripping the Gutenberg boilerplate.
2. **Extract** — scans the text against a lexicon of ~150 color words, including literary/archaic ones (`brimstone`, `sable`, `swart`, `vermillion`), inflections (`reddening`, `whitest`), hyphenated compounds (`snow-white`, `grey-headed`, `coffin-coloured`), and modifier phrases (`dark purplish yellow`, `faded walnut`).
3. **Render** — lays the words out justified on a near-black poster, each in its display color. HTML output is dependency-free; PNG uses Pillow.

### Why not the Google Books API for text?

The Google Books API serves **metadata and preview snippets only** — it never returns machine-readable full text, even for public domain volumes (the "download" links it exposes go through captcha-gated web pages, and anonymous API access is heavily quota-limited). So bookviz uses Google Books optionally for metadata enrichment (canonical title for the poster caption, via `--google-api-key` or `GOOGLE_BOOKS_API_KEY`), and Project Gutenberg for the actual text — the only major source with full public domain texts behind a plain programmatic API.

## More poster ideas

See [IDEAS.md](IDEAS.md) for a brainstorm of similar poster-style visualizations for books, movies, and TV.

## Gallery: the Gutenberg Top 10

Both posters for each of the 10 most-downloaded books on Project Gutenberg.

| | every color in | sentence-length skyline |
|---|---|---|
| **Moby Dick** | ![](examples/moby-dick.png) | ![](examples/moby-dick-skyline.png) |
| **Pride and Prejudice** | ![](examples/pride-and-prejudice.png) | ![](examples/pride-and-prejudice-skyline.png) |
| **Romeo and Juliet** | ![](examples/romeo-and-juliet.png) | ![](examples/romeo-and-juliet-skyline.png) |
| **The City of God, Volume I** | ![](examples/the-city-of-god--volume-i.png) | ![](examples/the-city-of-god--volume-i-skyline.png) |
| **A Room with a View** | ![](examples/a-room-with-a-view.png) | ![](examples/a-room-with-a-view-skyline.png) |
| **Crime and Punishment** | ![](examples/crime-and-punishment.png) | ![](examples/crime-and-punishment-skyline.png) |
| **Alice's Adventures in Wonderland** | ![](examples/alice-s-adventures-in-wonderland.png) | ![](examples/alice-s-adventures-in-wonderland-skyline.png) |
| **The Count of Monte Cristo** | ![](examples/the-count-of-monte-cristo.png) | ![](examples/the-count-of-monte-cristo-skyline.png) |
| **Middlemarch** | ![](examples/middlemarch.png) | ![](examples/middlemarch-skyline.png) |
| **Frankenstein** | ![](examples/frankenstein.png) | ![](examples/frankenstein-skyline.png) |

## License

MIT. Book texts are public domain via [Project Gutenberg](https://www.gutenberg.org).
