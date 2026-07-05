"""Render the color list as a self-contained HTML poster."""

from __future__ import annotations

import html

from .colors import ColorMatch

_TEMPLATE = """<!doctype html>
<html>
<head>
<meta charset="utf-8">
<title>every color in {title_esc}</title>
<style>
  body {{
    background: #1b1b1b;
    margin: 0;
    display: flex;
    justify-content: center;
  }}
  .poster {{
    box-sizing: border-box;
    width: min(1500px, 100vw);
    aspect-ratio: 3 / 4;
    min-height: 100vh;
    height: auto;
    padding: 4.5%;
    background: #1b1b1b;
    display: flex;
    flex-direction: column;
    font-family: "Helvetica Neue", Helvetica, Arial, sans-serif;
  }}
  .words {{
    text-align: justify;
    font-weight: 700;
    font-size: clamp(11px, 1.55vw, 23px);
    line-height: 1.6;
    word-spacing: 0.1em;
  }}
  .footer {{
    margin-top: auto;
    padding-top: 3em;
    display: flex;
    align-items: flex-end;
    justify-content: space-between;
    color: #fff;
  }}
  .credit {{ font-weight: 700; font-size: clamp(12px, 1.3vw, 20px); }}
  .caption {{ text-align: right; }}
  .caption .kicker {{ font-weight: 700; font-size: clamp(14px, 1.8vw, 27px); }}
  .caption .title {{ font-weight: 800; font-size: clamp(26px, 4.2vw, 64px); letter-spacing: -0.02em; }}
</style>
</head>
<body>
<div class="poster">
  <div class="words">{words}</div>
  <div class="footer">
    <div class="credit">{credit_esc}</div>
    <div class="caption">
      <div class="kicker">every color in</div>
      <div class="title">{title_esc}</div>
    </div>
  </div>
</div>
</body>
</html>
"""


def render_html(matches: list[ColorMatch], title: str, credit: str = "bookviz") -> str:
    spans = []
    last = len(matches) - 1
    for i, m in enumerate(matches):
        comma = "" if i == last else ","
        spans.append(
            f'<span style="color:{m.hex}">{html.escape(m.phrase)}{comma}</span>'
        )
    return _TEMPLATE.format(
        words=" ".join(spans),
        title_esc=html.escape(title),
        credit_esc=html.escape(credit),
    )
