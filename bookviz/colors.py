"""Color-word lexicon and extraction.

Finds every color word in a text, in order of appearance, in the spirit of
barelymaps' "every color in Moby-Dick" poster. Matches plain color words
("crimson"), inflections ("reddening"), hyphenated compounds ("snow-white",
"grey-headed", "coffin-coloured"), and modifier phrases ("dark purplish
yellow", "faded walnut").
"""

from __future__ import annotations

import re
from dataclasses import dataclass

# Display hexes are tuned for legibility on a near-black background.
WHITE = "#ffffff"
GREY = "#a9a9a9"
BLACK = "#8c8c8c"  # "black" still has to be readable on a dark poster
RED = "#e05e5e"
PINK = "#ef8fa8"
ORANGE = "#e8a25e"
TAN = "#cf9468"
YELLOW = "#e9d44d"
GOLD = "#e3c04b"
GREEN = "#7cc36e"
BLUE = "#6f9ff0"
PURPLE = "#b07fe8"
BROWN = "#c08552"
SILVER = "#c0c6cc"


def _family(hex_code: str, *words: str) -> dict[str, str]:
    return {w: hex_code for w in words}


# fmt: off
COLOR_WORDS: dict[str, str] = {
    **_family(WHITE,
        "white", "whitish", "whiter", "whitest", "whitened", "snowy",
        "milky", "pearly", "ivory", "alabaster", "marble", "marbleized",
        "blanched", "bleached", "bleaching", "pallid", "pale", "paler",
        "palest", "wan", "ashen", "ashy", "chalky", "ghostly", "albino",
        "colourless", "colorless", "blank", "creamy", "cream"),
    **_family(GREY,
        "grey", "gray", "greyish", "grayish", "leaden", "slate", "slaty",
        "dusky", "grizzled", "hoary", "ash", "livid", "lividly",
        "discoloured", "discolored", "drab", "dun"),
    **_family(SILVER, "silver", "silvery"),
    **_family(BLACK,
        "black", "blackish", "blacker", "blackest", "blackened", "ebon",
        "ebony", "sable", "jetty", "raven", "inky", "sooty", "pitchy",
        "pitchiest", "charcoal"),
    **_family(RED,
        "red", "redder", "reddish", "reddened", "reddening", "ruddy",
        "crimson", "crimsoned", "scarlet", "vermilion", "vermillion",
        "bloodshot", "carmine", "maroon", "fiery"),
    **_family(PINK, "pink", "rosy", "roseate"),
    **_family(ORANGE,
        "orange", "tawny", "tawn", "amber", "apricot", "copper", "coppery",
        "bronze", "bronzed", "rust", "rusty", "russet", "sunburnt",
        "swart", "swarthy", "sallow"),
    **_family(YELLOW,
        "yellow", "yellowish", "flaxen", "saffron", "brimstone", "lemon",
        "blond", "blonde"),
    **_family(GOLD, "gold", "golden", "gilded"),
    **_family(GREEN,
        "green", "greenish", "greener", "greenest", "verdant", "emerald",
        "olive"),
    **_family(BLUE,
        "blue", "bluish", "bluer", "bluest", "azure", "indigo", "sapphire",
        "cobalt", "cerulean", "ultramarine"),
    **_family(PURPLE,
        "purple", "purplish", "purpled", "violet", "lavender", "lilac",
        "mauve"),
    **_family(BROWN,
        "brown", "brownish", "chestnut", "mahogany", "walnut", "sepia",
        "umber", "hazel", "tanned"),
}
# fmt: on

# Words that only count when attached to a color word ("snow-white",
# "dark blue", "iron-grey") — too ambiguous to match on their own.
MODIFIERS = {
    "dark", "darkly", "deep", "deeply", "light", "lightly", "bright",
    "vivid", "dull", "faded", "mild", "wondrous", "slightly", "spotted",
    "snow", "milk", "blood", "coal", "pitch", "jet", "iron", "steel",
    "lead", "sun", "tiger", "sea", "sky", "wine", "smoke",
}

# A hyphenated word ending in one of these counts even if the first half
# isn't a known color ("coffin-coloured", "drab-coloured").
COLOR_SUFFIXES = {"coloured", "colored", "hued", "tinted", "colour", "color"}

_WORD_RE = re.compile(r"[A-Za-z]+(?:[-'][A-Za-z]+)*")


@dataclass
class ColorMatch:
    phrase: str  # as it appeared, lowercased ("snow-white", "dark blue")
    hex: str  # display color


def _classify_token(token: str) -> str | None:
    """Return a display hex if this single token is a color word."""
    if token in COLOR_WORDS:
        return COLOR_WORDS[token]
    if "-" in token:
        parts = token.split("-")
        color_parts = [p for p in parts if p in COLOR_WORDS]
        if color_parts:
            return COLOR_WORDS[color_parts[-1]]
        if parts[-1] in COLOR_SUFFIXES:
            return GREY
    return None


def _is_modifier(token: str) -> bool:
    if token in MODIFIERS:
        return True
    # hyphenated modifier halves: "snow-" in "snow-white" is handled by
    # _classify_token; this covers things like "hill-side blue"
    return "-" in token and any(p in MODIFIERS for p in token.split("-"))


def extract_colors(text: str) -> list[ColorMatch]:
    """Every color word/phrase in the text, in order of appearance."""
    tokens = [(m.group(0), m.start(), m.end()) for m in _WORD_RE.finditer(text)]
    matches: list[ColorMatch] = []
    i = 0
    while i < len(tokens):
        lower = tokens[i][0].lower()
        hex_code = _classify_token(lower)
        if hex_code is None and not _is_modifier(lower):
            i += 1
            continue

        # Greedily extend a phrase across adjacent modifier/color tokens
        # (separated by whitespace only — punctuation breaks the phrase).
        phrase = [lower]
        phrase_hex = hex_code
        j = i + 1
        while j < len(tokens) and len(phrase) < 3:
            nxt, nstart, _ = tokens[j]
            between = text[tokens[j - 1][2]:nstart]
            if between.strip():  # punctuation between words
                break
            nlower = nxt.lower()
            nhex = _classify_token(nlower)
            if nhex is None and not _is_modifier(nlower):
                break
            # Modifiers only precede colors ("dark blue"), never trail
            # them ("black sea" is not a color phrase).
            if nhex is None and phrase_hex is not None:
                break
            # Don't merge two standalone colors ("green green" in "green,
            # green" once punctuation is stripped) unless the earlier word
            # blends into the next ("purplish yellow"), i.e. the phrase so
            # far is modifiers-only or its last word is an "-ish" color.
            if nhex is not None and phrase_hex is not None and not phrase[-1].endswith("ish"):
                break
            phrase.append(nlower)
            if nhex is not None:
                phrase_hex = nhex
            j += 1

        if phrase_hex is not None:
            matches.append(ColorMatch(" ".join(phrase), phrase_hex))
            i = j
        else:
            i += 1  # modifier(s) with no color attached — not a match
    return matches
