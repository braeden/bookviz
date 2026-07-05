"""Sentence-length skyline poster (requires Pillow).

One thin bar per sentence, height = word count, wrapped into rows like a
city skyline — the rhythm of the author's prose. Bars are tinted by how
the sentence ends: statements off-white, questions blue, exclamations gold.
"""

from __future__ import annotations

import re

BG = "#1b1b1b"
FG = "#ffffff"
BAR = {".": "#d9d9d9", "?": "#6f9ff0", "!": "#e3c04b"}

# Common abbreviations that end with a period mid-sentence.
_ABBREV = {
    "mr", "mrs", "ms", "dr", "st", "prof", "capt", "gen", "col", "lieut",
    "rev", "hon", "esq", "jr", "sr", "vs", "etc", "viz", "no", "vol", "chap",
}

_SPLIT_RE = re.compile(r'([.!?])["\')\]]*\s+(?=["\'(\[]?[A-Z])')


def split_sentences(text: str) -> list[tuple[int, str]]:
    """Return (word_count, end_punctuation) per sentence."""
    text = re.sub(r"\s+", " ", text).strip()
    pieces: list[tuple[str, str]] = []  # (sentence, terminator)
    last = 0
    for m in _SPLIT_RE.finditer(text):
        before_term = text[last:m.start(1)].rstrip().rsplit(None, 1)
        if m.group(1) == "." and before_term and \
                before_term[-1].lower().strip(".") in _ABBREV:
            continue  # "Mr. Starbuck" — not a sentence boundary
        pieces.append((text[last:m.end()].strip(), m.group(1)))
        last = m.end()
    tail = text[last:].strip()
    if tail:
        pieces.append((tail, tail[-1] if tail[-1] in ".!?" else "."))
    return [(len(s.split()), term) for s, term in pieces if s]


def render_skyline(
    text: str,
    title: str,
    out_path: str,
    credit: str = "bookviz",
    width: int = 1500,
) -> None:
    try:
        from PIL import Image, ImageDraw
    except ImportError:
        raise SystemExit("skyline output requires Pillow: pip install pillow")
    from .render_png import _load_font

    sentences = split_sentences(text)
    margin = int(width * 0.045)
    usable = width - 2 * margin

    bar_w, gap = 2, 1
    per_row = usable // (bar_w + gap)
    rows = [sentences[i:i + per_row] for i in range(0, len(sentences), per_row)]

    cap = 80  # words; taller sentences are clipped to keep rows readable
    row_h = int(width * 0.075)
    row_gap = int(row_h * 0.28)

    footer_h = int(width * 0.12)
    height = margin + len(rows) * (row_h + row_gap) + footer_h + margin
    img = Image.new("RGB", (width, height), BG)
    draw = ImageDraw.Draw(img)

    y = margin
    for row in rows:
        base = y + row_h
        for i, (words, term) in enumerate(row):
            h = max(2, int(min(words, cap) / cap * row_h))
            x = margin + i * (bar_w + gap)
            draw.rectangle((x, base - h, x + bar_w - 1, base),
                           fill=BAR.get(term, BAR["."]))
        y = base + row_gap

    kicker_font = _load_font(int(width * 0.019))
    title_font = _load_font(int(width * 0.042))
    credit_font = _load_font(int(width * 0.014))
    baseline = height - margin
    title_w = draw.textlength(title, font=title_font)
    kicker = "sentence-length skyline of"
    kicker_w = draw.textlength(kicker, font=kicker_font)
    draw.text((width - margin - title_w, baseline - title_font.size), title,
              font=title_font, fill=FG)
    draw.text((width - margin - kicker_w,
               baseline - title_font.size - int(kicker_font.size * 1.6)),
              kicker, font=kicker_font, fill=FG)
    note = f"{len(sentences):,} sentences · one bar each · height = words · "
    draw.text((margin, baseline - credit_font.size), credit,
              font=credit_font, fill=FG)
    note_font = credit_font
    draw.text((margin, baseline - int(credit_font.size * 3)),
              note + "questions blue · exclamations gold",
              font=note_font, fill="#8c8c8c")

    img.save(out_path)
