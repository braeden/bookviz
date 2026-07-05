"""Render the color list as a PNG poster (requires Pillow).

Layout mirrors the reference poster: bold, comma-separated, fully justified
color words on a near-black background, with an "every color in <Title>"
caption bottom-right.
"""

from __future__ import annotations

import os

from .colors import ColorMatch

BG = "#1b1b1b"
FG = "#ffffff"

_FONT_CANDIDATES = [
    # (path, index) — first hit wins
    ("/System/Library/Fonts/Supplemental/Arial Bold.ttf", 0),
    ("/System/Library/Fonts/Helvetica.ttc", 1),  # 1 = Helvetica Bold
    ("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 0),
    ("/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf", 0),
    ("C:/Windows/Fonts/arialbd.ttf", 0),
]


def _load_font(size: int):
    from PIL import ImageFont

    for path, index in _FONT_CANDIDATES:
        if os.path.exists(path):
            try:
                return ImageFont.truetype(path, size, index=index)
            except OSError:
                continue
    return ImageFont.load_default(size)


def render_png(
    matches: list[ColorMatch],
    title: str,
    out_path: str,
    width: int = 1500,
) -> None:
    try:
        from PIL import Image, ImageDraw
    except ImportError:
        raise SystemExit(
            "PNG output requires Pillow: pip install pillow "
            "(or use --format html, which has no dependencies)"
        )

    margin = int(width * 0.045)
    usable = width - 2 * margin

    # Pick a word font size so the words fill roughly a 3:4 poster.
    # Estimate: total glyph area scales with size^2; solve for size, clamp.
    font_size = max(11, min(26, int((usable * width * 0.9 / max(
        1, sum(len(m.phrase) + 2 for m in matches))) ** 0.5 / 0.62 / 1.6)))
    font = _load_font(font_size)
    line_h = int(font_size * 1.62)

    probe = Image.new("RGB", (1, 1))
    measure = ImageDraw.Draw(probe)

    def w_of(s: str) -> int:
        return int(measure.textlength(s, font=font))

    space_w = w_of(" ")
    min_gap = int(space_w * 1.15)

    # Greedy line breaking over rendered word widths.
    words = []
    last = len(matches) - 1
    for i, m in enumerate(matches):
        text = m.phrase + ("" if i == last else ",")
        words.append((text, m.hex, w_of(text)))

    lines: list[list[tuple[str, str, int]]] = []
    cur: list[tuple[str, str, int]] = []
    cur_w = 0
    for item in words:
        add = item[2] if not cur else item[2] + min_gap
        if cur and cur_w + add > usable:
            lines.append(cur)
            cur, cur_w = [item], item[2]
        else:
            cur.append(item)
            cur_w += add
    if cur:
        lines.append(cur)

    footer_h = int(width * 0.09)
    height = margin + len(lines) * line_h + footer_h + margin
    img = Image.new("RGB", (width, height), BG)
    draw = ImageDraw.Draw(img)

    y = margin
    for li, line in enumerate(lines):
        text_w = sum(w for _, _, w in line)
        gaps = len(line) - 1
        is_last = li == len(lines) - 1
        gap = min_gap if is_last or gaps == 0 else (usable - text_w) / gaps
        x = float(margin)
        for text, hex_code, w in line:
            draw.text((x, y), text, font=font, fill=hex_code)
            x += w + gap
        y += line_h

    # Footer: just the title, bottom-right.
    title_font = _load_font(int(width * 0.042))
    title_w = int(measure.textlength(title, font=title_font))
    baseline = height - margin
    draw.text((width - margin - title_w, baseline - title_font.size), title,
              font=title_font, fill=FG)

    img.save(out_path)
