"""Palette-set poster: one color-barcode row per book (requires Pillow).

Each book's color words, in order of appearance, become thin stripes
stretched across a fixed-width strip — the palettes alone identify the
books (Moby-Dick reads white, Dracula red and black).
"""

from __future__ import annotations

from .colors import ColorMatch

BG = "#1b1b1b"
FG = "#ffffff"


def render_palette_set(
    books: list[tuple[str, list[ColorMatch]]],
    out_path: str,
    width: int = 1500,
) -> None:
    try:
        from PIL import Image, ImageDraw
    except ImportError:
        raise SystemExit("palette-set output requires Pillow: pip install pillow")
    from .render_png import _load_font

    margin = int(width * 0.045)
    usable = width - 2 * margin

    label_font = _load_font(int(width * 0.0155))
    strip_h = int(width * 0.026)
    label_gap = int(label_font.size * 0.55)
    row_h = label_font.size + label_gap + strip_h
    row_gap = int(width * 0.017)

    height = margin + len(books) * (row_h + row_gap) - row_gap + margin
    img = Image.new("RGB", (width, height), BG)
    draw = ImageDraw.Draw(img)

    y = margin
    for title, matches in books:
        count = f"{len(matches):,} color words"
        count_w = draw.textlength(count, font=label_font)
        draw.text((margin, y), title, font=label_font, fill=FG)
        draw.text((width - margin - count_w, y), count,
                  font=label_font, fill="#8c8c8c")
        top = y + label_font.size + label_gap
        n = max(1, len(matches))
        for i, m in enumerate(matches):
            x0 = margin + i * usable / n
            x1 = margin + (i + 1) * usable / n
            draw.rectangle((x0, top, max(x0 + 1, x1), top + strip_h), fill=m.hex)
        y = top + strip_h + row_gap

    img.save(out_path)
