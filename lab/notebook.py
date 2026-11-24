"""Shared lab equipment: README block editing, palettes, type, instrument chrome and motion.

Since the Nov 24 2026 redesign the profile is a bench of lab instruments: machined
panels (graphite in dark mode, cool grey in light) held by corner screws, each with a
dark glass screen where amber phosphor draws numbers in a 5×7 dot-matrix face and the
pixel art as an LCD. Tools are keycaps. Lettering is drawn as vector paths from the
fonts in lab/fonts, so GitHub shows the same type to everyone, whatever fonts they have.
"""
import datetime as dt
import hashlib
import math
import os
import re
import zlib
from functools import lru_cache
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
README = ROOT / "README.md"
FONTS = ROOT / "lab" / "fonts"
ASSETS = ROOT / "assets"
USER = "Llenoxinn"
MANILA = dt.timezone(dt.timedelta(hours=8), "Asia/Manila")

# Ensure matplotlib uses the local persistent config and font cache
_lab_dir = Path(__file__).resolve().parent
_mpl_dir = _lab_dir / ".runtime" / ".mplconfig"
_mpl_dir.mkdir(parents=True, exist_ok=True)
os.environ.setdefault("MPLCONFIGDIR", str(_mpl_dir))

# Type: Instrument Sans throughout. Bold for titles, Regular for text, SemiBold for small
# emphasis, Condensed Bold capitals for the silkscreened labels on a panel. Numbers on a
# screen use the 5×7 dot-matrix face in pixel.DOTFONT instead of a font.
FACES = {"title": "BlackOpsOne-Regular.ttf", "head": "RussoOne-Regular.ttf", "body": "BarlowCondensed-Medium.ttf",
         "semi": "BarlowCondensed-SemiBold.ttf", "bold": "BarlowCondensed-Bold.ttf", "num": "Teko-SemiBold.ttf",
         "label": "BarlowCondensed-Bold.ttf"}
TRACK = {"label": 0.12}     # default tracking per face, in em

# Amber phosphor. Screens are dark glass in both themes, so these never change with the theme.
GLOW = dict(glass="#0f0d0a", ghost="#221a0e", grid="#2e2414", dim="#6e4b16", mid="#b97a1e",
            amber="#ffad33", hot="#ffe2ab")
# The 8 tones of the project illustrations (K darkest .. W brightest), as phosphor.
RAMP = dict(K="#17120b", D="#2b200f", M="#3f2e12", B="#7d5417", N="#c98419", L="#f0a43a", P="#ffc56c",
            W="#fff1d2")
# The portfolio's sprite cells (P paper, L lavender, N neon, D deep), as phosphor: the white
# lab coat burns brightest, hair and sparks in amber, skin and outlines mid.
SPRITE = dict(P=GLOW["hot"], L=GLOW["mid"], N=GLOW["amber"], D=GLOW["glass"])
# Data colours keep their meaning: LeetCode difficulty, drawn on glass in both themes.
SEMANTIC = dict(easy="#3fb950", medium="#ffb02e", hard="#ff5c6c")

THEMES = ("dark", "light")   # every picture ships in both; PANEL holds each theme's colours
PANEL = {
    "light": dict(page="#ffffff", face="#eceef1", edge="#c4cad1", lip="#cdd2d8", hi="#fbfcfd",
                  inset="#e1e4e8", text="#15181c", muted="#555e69", label="#48505a", rule="#c4cad1",
                  screw="#d3d7dc", slot="#858d97", bezel="#25282d", led="#e8900c", off="#b9c0c7",
                  key_face="#f8f9fa", key_side="#c3c9d0", key_edge="#aab1b9", key_ink="#272c33"),
    "dark": dict(page="#0d1117", face="#171a1f", edge="#2c3138", lip="#07080b", hi="#23272d",
                 inset="#111418", text="#eaedf0", muted="#9ba4ae", label="#aeb6bf", rule="#2f353d",
                 screw="#2a2f36", slot="#0b0d10", bezel="#050607", led="#ffad33", off="#3b4149",
                 key_face="#262b32", key_side="#0a0c0f", key_edge="#363c45", key_ink="#dde1e6"),
}
# Amber keycaps are the one action colour: the hero's button and the stack's group keys.
ACCENT = dict(face="#ffad33", top="#ffbd57", side="#a8630a", edge="#8f5408", ink="#1c1305")
COLUMN = 760   # the README's content column: two 376 cards with an 8 px gap, or one full-width piece


def replace_block(name: str, body: str, path: Path = README) -> bool:
    """Replace the text between <!-- NAME:START --> and <!-- NAME:END -->. True if changed."""
    text = path.read_text(encoding="utf-8")
    pattern = re.compile(rf"(<!-- {name}:START -->)(.*?)(<!-- {name}:END -->)", re.DOTALL)
    if not pattern.search(text):
        raise SystemExit(f"README is missing the <!-- {name}:START/END --> markers")
    new = pattern.sub(lambda m: f"{m.group(1)}\n{body.strip()}\n{m.group(3)}", text, count=1)
    if len(new.encode()) > 500 * 1024:
        print(f"::warning::README is {len(new.encode()) // 1024} KiB; GitHub truncates past 500 KiB")
    if new != text:
        path.write_text(new, encoding="utf-8")
        return True
    return False


def picture(stem, alt, width=None, folder="assets", ext="svg", query=""):
    """<picture> that swaps dark/light variants with GitHub's theme."""
    w = f' width="{width}"' if width else ""
    q = f"?{query}" if query else ""
    return (f'<picture><source media="(prefers-color-scheme: dark)" srcset="{folder}/{stem}-dark.{ext}{q}">'
            f'<img alt="{alt}" src="{folder}/{stem}-light.{ext}{q}"{w}></picture>')


def esc(s):
    return str(s).replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;").replace('"', "&quot;")


def stamp(*parts):
    """Short content hash: image URLs change only when the picture does."""
    return hashlib.sha1("".join(str(p) for p in parts).encode()).hexdigest()[:8]


def scene(stem, alt, width="100%", height=None, folder="assets", query=""):
    """<picture> for an animated image: a still for reduced motion, then dark/light."""
    q = f"?{query}" if query else ""
    size = f' width="{width}"' + (f' height="{height}"' if height else "")
    return (f'<picture>'
            f'<source media="(prefers-reduced-motion: reduce) and (prefers-color-scheme: dark)" srcset="{folder}/{stem}-still-dark.svg{q}">'
            f'<source media="(prefers-reduced-motion: reduce)" srcset="{folder}/{stem}-still-light.svg{q}">'
            f'<source media="(prefers-color-scheme: dark)" srcset="{folder}/{stem}-dark.svg{q}">'
            f'<img src="{folder}/{stem}-light.svg{q}" alt="{esc(alt)}"{size}></picture>')


def themed(stem, alt, width=None, height=None, folder="assets", title=None, attrs="", query=""):
    """Like picture(), with fixed pixel sizes and a hover title for inline tiles and chips."""
    size = (f' width="{width}"' if width else "") + (f' height="{height}"' if height else "")
    tip = f' title="{esc(title)}"' if title else ""
    q = f"?{query}" if query else ""
    return (f'<picture><source media="(prefers-color-scheme: dark)" srcset="{folder}/{stem}-dark.svg{q}">'
            f'<img src="{folder}/{stem}-light.svg{q}" alt="{esc(alt)}"{tip}{size}{attrs}></picture>')


def wide_scene(stem, narrow, alt, folder="assets", width=COLUMN, query=""):
    """<picture> for a full-width animated image with a phone layout: still or moving, by theme."""
    q = f"?{query}" if query else ""

    def src(media, name):
        return f'<source media="{media}" srcset="{folder}/{name}.svg{q}">'
    phone, still, dark = "(max-width: 600px)", "(prefers-reduced-motion: reduce)", "(prefers-color-scheme: dark)"
    return ('<picture>'
            + src(f"{phone} and {still} and {dark}", f"{narrow}-still-dark") + src(f"{phone} and {still}", f"{narrow}-still-light")
            + src(f"{phone} and {dark}", f"{narrow}-dark") + src(phone, f"{narrow}-light")
            + src(f"{still} and {dark}", f"{stem}-still-dark") + src(still, f"{stem}-still-light")
            + src(dark, f"{stem}-dark")
            + f'<img src="{folder}/{stem}-light.svg{q}" alt="{esc(alt)}" width="{width}"></picture>')


def write_pair(folder, stem, draw):
    """Write stem-{theme}.svg and stem-still-{theme}.svg; draw(theme, animate) returns svg text."""
    folder.mkdir(parents=True, exist_ok=True)
    for theme in THEMES:
        (folder / f"{stem}-{theme}.svg").write_text(draw(theme, True), encoding="utf-8")
        (folder / f"{stem}-still-{theme}.svg").write_text(draw(theme, False), encoding="utf-8")


# ------------------------------------------------------------------ type as paths

@lru_cache(maxsize=None)
def _font(face):
    from matplotlib.font_manager import FontProperties, get_font
    if face == "fallback":   # Greek and symbols the display faces lack; ships with matplotlib
        import matplotlib
        path = str(Path(matplotlib.get_data_path()) / "fonts" / "ttf" / "DejaVuSans.ttf")
    else:
        path = str(FONTS / FACES[face])
    # Older matplotlib hints at 8x horizontal resolution by default (text.hinting_factor),
    # which spreads every letter 8x apart; ask for 1x so spacing doesn't depend on the version.
    try:
        font = get_font(path, hinting_factor=1)
    except TypeError:
        font = get_font(path)
    return FontProperties(fname=path), font


@lru_cache(maxsize=20000)
def _glyph(ch, face, size):
    """(svg path data at origin, advance) for one character."""
    from matplotlib.path import Path as MPath
    from matplotlib.textpath import TextPath
    prop, ft = _font(face)
    if not ch.isspace() and ft.get_char_index(ord(ch)) == 0:
        if face != "fallback":
            return _glyph(ch, "fallback", size)
        ch = "?"   # nothing has it: show a visible placeholder rather than crash
    ft.set_size(size, 72)
    # Exact outline advances, not whole-pixel hinted ones: these are vector paths.
    try:
        from matplotlib.ft2font import LoadFlags
        adv = ft.load_char(ord(ch), LoadFlags.NO_HINTING).linearHoriAdvance / 65536
    except ImportError:
        adv = ft.load_char(ord(ch)).horiAdvance / 64
    if ch.isspace():
        return "", max(adv, 0.25 * size)   # Instrument Sans sets a tight 0.19 em word space
    tp = TextPath((0, 0), ch, size=size, prop=prop)
    out = []
    for verts, code in tp.iter_segments(simplify=False, curves=True):
        p = [f"{v:.1f}" for v in verts]
        pts = [(p[i], f"{-float(p[i + 1]):.1f}") for i in range(0, len(p), 2)]
        if code == MPath.MOVETO:
            out.append(f"M{pts[0][0]} {pts[0][1]}")
        elif code == MPath.LINETO:
            out.append(f"L{pts[0][0]} {pts[0][1]}")
        elif code == MPath.CURVE3:
            out.append(f"Q{pts[0][0]} {pts[0][1]} {pts[1][0]} {pts[1][1]}")
        elif code == MPath.CURVE4:
            out.append(f"C{pts[0][0]} {pts[0][1]} {pts[1][0]} {pts[1][1]} {pts[2][0]} {pts[2][1]}")
        elif code == MPath.CLOSEPOLY:
            out.append("Z")
    return "".join(out), adv


def text_width(text, face, size, tracking=None):
    tracking = TRACK.get(face, 0) * size if tracking is None else tracking
    return sum(_glyph(c, face, size)[1] + tracking for c in text) - (tracking if text else 0)


def svg_doc(w, h, body, label):
    return (f'<svg xmlns="http://www.w3.org/2000/svg" xmlns:xlink="http://www.w3.org/1999/xlink" '
            f'viewBox="0 0 {w} {h}" width="{w}" height="{h}" '
            f'role="img" aria-label="{esc(label)}">\n{body}\n</svg>\n')


class Typesetter:
    """Text as reusable glyph paths: each glyph is defined once in <defs> and placed with <use>."""

    def __init__(self, prefix="g"):
        self.prefix, self.defs = prefix, {}

    def _ref(self, ch, face, size):
        key = (ch, face, size)
        if key not in self.defs:
            d, _ = _glyph(ch, face, size)
            self.defs[key] = (f"{self.prefix}{len(self.defs)}", d)
        return self.defs[key][0]

    def text(self, text, face, size, x, y, fill, anchor="start", tracking=None, opacity=None, attrs=""):
        """One line of text as <use> references to shared glyphs. Returns (svg, 0); the second
        value is kept so existing `[0]` call sites keep working."""
        tracking = TRACK.get(face, 0) * size if tracking is None else tracking
        w = text_width(text, face, size, tracking)
        x -= {"start": 0, "middle": w / 2, "end": w}[anchor]
        out = []
        for ch in text:
            d, adv = _glyph(ch, face, size)
            if d:
                ref = self._ref(ch, face, size)
                out.append(f'<use href="#{ref}" xlink:href="#{ref}" x="{x:.1f}" y="{y:.1f}"/>')
            x += adv + tracking
        op = f' opacity="{opacity}"' if opacity is not None else ""
        fl = f' fill="{fill}"' if fill else ""
        return f'<g{fl}{op}{attrs}>{"".join(out)}</g>', 0

    def defs_svg(self):
        return "<defs>" + "".join(f'<path id="{i}" d="{d}"/>' for i, d in self.defs.values()) + "</defs>"


def label(ts, text, x, y, fill, size=10, anchor="start"):
    """A silkscreened panel label: condensed bold capitals, tracked out."""
    return ts.text(text.upper(), "label", size, x, y, fill, anchor=anchor)[0]


def fit(text, face, size, room, floor=8):
    while text_width(text, face, size) > room and size > floor:
        size -= 0.5
    return size


def wrap(text, face, size, width, balance=False):
    """Greedy line breaking by measured width. balance=True evens out two lines, so the
    second never ends on an orphaned word."""
    lines, line = [], ""
    for word in text.split():
        trial = f"{line} {word}".strip()
        if line and text_width(trial, face, size) > width:
            lines.append(line)
            line = word
        else:
            line = trial
    lines += [line] if line else []
    if balance and len(lines) == 2:
        words = text.split()
        splits = [(" ".join(words[:i]), " ".join(words[i:])) for i in range(1, len(words))]
        ok = [p for p in splits if text_width(p[0], face, size) <= width and text_width(p[1], face, size) <= width]
        if ok:
            lines = list(min(ok, key=lambda p: abs(text_width(p[0], face, size) - text_width(p[1], face, size))))
    return lines


def paragraph(ts, text, face, size, x, y, width, fill, leading=1.45):
    """Wrapped lines from baseline y. Returns (svg, baseline of the last line)."""
    lines = wrap(text, face, size, width)
    out = "".join(ts.text(line, face, size, x, y + i * size * leading, fill)[0] for i, line in enumerate(lines))
    return out, y + (len(lines) - 1) * size * leading


def mark(name, x, y, size, fill):
    """A one-colour icon from lab/icons.py, fitted into a size × size box."""
    from icons import ICONS
    box, d = ICONS[name.lower()]
    return (f'<svg x="{x:g}" y="{y:g}" width="{size:g}" height="{size:g}" viewBox="{box}">'
            f'<path fill="{fill}" d="{d}"/></svg>')


# ------------------------------------------------------------------ instrument chrome
# Shape rule: panels round at 8 (12 for the hero), screens at 5, keycaps at 6, chips at 4.

def _f(v):
    return f"{v:.1f}".rstrip("0").rstrip(".")


def screw(cx, cy, theme, seed):
    """A panel screw: a domed head with its slot turned however it was last tightened."""
    s = PANEL[theme]
    a = math.radians(zlib.crc32(str(seed).encode()) % 180)
    dx, dy = 2.1 * math.cos(a), 2.1 * math.sin(a)
    return (f'<circle cx="{_f(cx)}" cy="{_f(cy)}" r="3.3" fill="{s["screw"]}" stroke="{s["edge"]}" stroke-width="0.8"/>'
            f'<path d="M{cx - dx:.1f} {cy - dy:.1f}L{cx + dx:.1f} {cy + dy:.1f}" stroke="{s["slot"]}" '
            f'stroke-width="1.1" stroke-linecap="round"/>')


def panel(theme, x, y, w, h, r=8, screws=True, seed="panel", inset=9):
    """A machined instrument panel: face, 1 px edge, a top highlight, a 3 px lip underneath
    for thickness, and a screw in each corner. Content sits in (x .. x+w, y .. y+h-3)."""
    s = PANEL[theme]
    out = [f'<rect x="{_f(x)}" y="{_f(y)}" width="{_f(w)}" height="{_f(h)}" rx="{r}" fill="{s["lip"]}"/>',
           f'<rect x="{_f(x + .5)}" y="{_f(y + .5)}" width="{_f(w - 1)}" height="{_f(h - 3.5)}" rx="{r - .5}" '
           f'fill="{s["face"]}" stroke="{s["edge"]}"/>',
           f'<rect x="{_f(x + r)}" y="{_f(y + 1.5)}" width="{_f(w - 2 * r)}" height="1" fill="{s["hi"]}"/>']
    if screws:
        for k, (cx, cy) in enumerate(((x + inset, y + inset), (x + w - inset, y + inset),
                                      (x + inset, y + h - 3 - inset), (x + w - inset, y + h - 3 - inset))):
            out.append(screw(cx, cy, theme, f"{seed}{k}"))
    return "".join(out)


def screen(theme, x, y, w, h, r=5):
    """A dark glass screen in a bezel. Draw the picture next, then glass() over it."""
    s = PANEL[theme]
    return (f'<rect x="{_f(x - 3)}" y="{_f(y - 3)}" width="{_f(w + 6)}" height="{_f(h + 6)}" rx="{r + 3}" fill="{s["bezel"]}"/>'
            f'<rect x="{_f(x)}" y="{_f(y)}" width="{_f(w)}" height="{_f(h)}" rx="{r}" fill="{GLOW["glass"]}"/>')


def glass(x, y, w, h, r=5):
    """What makes a screen read as a tube: scanlines every 3 px and a faint glare."""
    lines = "".join(f"M{_f(x + 1)} {yy}h{_f(w - 2)}v1h-{_f(w - 2)}Z" for yy in range(int(y) + 2, int(y + h) - 1, 3))
    glare = f"M{_f(x + r)} {_f(y + 1)}H{_f(x + w * .46)}L{_f(x + w * .30)} {_f(y + h - 1)}H{_f(x + 1)}V{_f(y + r)}Z"
    return (f'<path d="{lines}" fill="#000" opacity="0.24"/>'
            f'<path d="{glare}" fill="#fff" opacity="0.028"/>')


def graticule(x, y, w, h, cols, rows, colour=None):
    """An oscilloscope graticule: dotted division lines, a brighter centre cross with ticks."""
    colour = colour or GLOW["grid"]
    d = []
    for i in range(1, cols):
        gx = x + w * i / cols
        d.extend(f"M{gx:.1f} {yy:.1f}h1v1h-1Z" for yy in frange(y + 3, y + h - 2, 4))
    for j in range(1, rows):
        gy = y + h * j / rows
        d.extend(f"M{xx:.1f} {gy:.1f}h1v1h-1Z" for xx in frange(x + 3, x + w - 2, 4))
    return f'<path d="{"".join(d)}" fill="{colour}"/>'


def frange(a, b, step):
    v = a
    while v < b:
        yield v
        v += step


def led(x, y, on, theme, size=6):
    """A panel LED, lit or dark; it never blinks."""
    s = PANEL[theme]
    if not on:
        return f'<rect x="{_f(x)}" y="{_f(y)}" width="{size}" height="{size}" rx="1.5" fill="{s["off"]}"/>'
    return (f'<rect x="{_f(x - 1.5)}" y="{_f(y - 1.5)}" width="{size + 3}" height="{size + 3}" rx="3" fill="{GLOW["amber"]}" opacity="0.25"/>'
            f'<rect x="{_f(x)}" y="{_f(y)}" width="{size}" height="{size}" rx="1.5" fill="{GLOW["amber"]}"/>'
            f'<rect x="{_f(x + 1.5)}" y="{_f(y + 1.5)}" width="{size - 3}" height="1.5" fill="{GLOW["hot"]}"/>')


def keycap(x, y, w, h, theme, accent=False, r=6):
    """A keyboard key: the skirt, then a narrower top surface a little lighter, set high."""
    s = PANEL[theme]
    side, top, edge = ((ACCENT["side"], ACCENT["face"], ACCENT["edge"]) if accent
                       else (s["key_side"], s["key_face"], s["key_edge"]))
    shine = "#fff" if accent or theme == "light" else "#ffffff"
    op = "0.45" if accent else ("0.9" if theme == "light" else "0.07")
    return (f'<rect x="{_f(x)}" y="{_f(y)}" width="{_f(w)}" height="{_f(h)}" rx="{r}" fill="{side}" stroke="{edge}" stroke-width="1"/>'
            f'<rect x="{_f(x + 3)}" y="{_f(y + 1.5)}" width="{_f(w - 6)}" height="{_f(h - 7.5)}" rx="{r - 1.5}" fill="{top}"/>'
            f'<rect x="{_f(x + 3 + r)}" y="{_f(y + 2.5)}" width="{_f(w - 6 - 2 * r)}" height="1" fill="{shine}" opacity="{op}"/>')


def chip(x, y, w, h, theme, r=4):
    """An engraved recess in the panel for a small icon or word."""
    s = PANEL[theme]
    return (f'<rect x="{_f(x)}" y="{_f(y)}" width="{_f(w)}" height="{_f(h)}" rx="{r}" fill="{s["inset"]}" '
            f'stroke="{s["edge"]}" stroke-width="0.8"/>')


def pixels(rows, x, y, scale, palette, gap=0.0):
    """Draw a pixel map; palette maps characters to colours, other cells stay empty. With a
    gap, each cell is a separate square, like an LCD's dot pitch."""
    out, side = [], scale - gap
    for key, colour in palette.items():
        d = "".join(f"M{_f(x + c * scale)} {_f(y + r * scale)}h{_f(side)}v{_f(side)}h-{_f(side)}Z"
                    for r, row in enumerate(rows) for c, v in enumerate(row) if v == key)
        if d:
            out.append(f'<path d="{d}" fill="{colour}"/>')
    return f'<g shape-rendering="crispEdges">{"".join(out)}</g>'


def lcd(rows, x, y, scale, palette=None, gap=None):
    """A portfolio sprite on a screen, in phosphor, with the LCD's dot gap."""
    return pixels(rows, x, y, scale, palette or SPRITE, gap if gap is not None else (1 if scale >= 4 else 0))


# ------------------------------------------------------------------ the 5×7 dot-matrix face

def _dot_glyph(ch):
    from pixel import DOTFONT
    return DOTFONT.get(ch) or DOTFONT.get(ch.upper()) or DOTFONT["?"]


def dot_cells(text):
    """Lit cells of `text` as (column, row) and the number of columns it spans."""
    cells, col = [], 0
    for ch in text:
        g = _dot_glyph(ch)
        cells.extend((col + c, r) for r, row in enumerate(g) for c, v in enumerate(row) if v == "#")
        col += len(g[0]) + 1
    return cells, max(0, col - 1)


def dot_width(text, pitch):
    return dot_cells(text)[1] * pitch


def _dot(cx, cy, r, shape):
    if shape == "round":
        return (f"M{cx - r:.2f} {cy:.2f}a{r:.2f} {r:.2f} 0 1 0 {2 * r:.2f} 0"
                f"a{r:.2f} {r:.2f} 0 1 0 {-2 * r:.2f} 0Z")
    return f"M{cx - r:.2f} {cy - r:.2f}h{2 * r:.2f}v{2 * r:.2f}h{-2 * r:.2f}Z"


BAYER = [[0, 8, 2, 10], [12, 4, 14, 6], [3, 11, 1, 9], [15, 7, 13, 5]]


def dot_text(text, x, y, pitch, fill=None, anchor="start", size=0.92, shape="round", ghost=None,
             halo=0.0, boot=None):
    """`text` in the 5×7 dot-matrix face with its top-left cell at (x, y), `pitch` px per dot.
    ghost: colour of the unlit dots behind the text, as on a real LED module. halo: opacity of
    a wider dim dot under each lit one. boot=(start, dur, steps): the dots come on in ordered
    dither groups, like a module running its self-test. Returns svg."""
    fill = fill or GLOW["amber"]
    cells, cols = dot_cells(text)
    w = cols * pitch
    x -= {"start": 0, "middle": w / 2, "end": w}[anchor]
    r = pitch * size / 2
    out = []
    if ghost:
        pid = "gd" + stamp(text, x, y, pitch)
        out.append(f'<defs><pattern id="{pid}" patternUnits="userSpaceOnUse" x="{x:.2f}" y="{y:.2f}" '
                   f'width="{pitch}" height="{pitch}"><path d="{_dot(pitch / 2, pitch / 2, r, shape)}" fill="{ghost}"/>'
                   f'</pattern></defs><rect x="{x:.2f}" y="{y:.2f}" width="{w:.2f}" height="{7 * pitch:.2f}" fill="url(#{pid})"/>')

    def path(cs, rad, extra=""):
        # each dot is a zero-length stroke with round (or square) caps: a circle in ~12 bytes
        d = "".join(f"M{x + (c + .5) * pitch:.1f} {y + (rw + .5) * pitch:.1f}h0" for c, rw in cs)
        cap = "round" if shape == "round" else "square"
        return (f'<path d="{d}" fill="none" stroke="{fill}" stroke-width="{2 * rad:.2f}" '
                f'stroke-linecap="{cap}"{extra}/>') if d else ""
    if halo:
        out.append(path(cells, pitch * 0.62, f' opacity="{halo}"'))
    if not boot:
        out.append(path(cells, r))
        return "".join(out)
    start, dur, steps = boot
    groups = {}
    for c, rw in cells:
        groups.setdefault(BAYER[rw % 4][c % 4] * steps // 16, []).append((c, rw))
    for k in sorted(groups):
        out.append(f'<g>{step_in(start + dur * k / steps)}{path(groups[k], r)}</g>')
    return "".join(out)


# ------------------------------------------------------------------ stepped motion
# Every animation leaves the finished picture as the base value, so a renderer
# without SMIL shows the final frame. Loops need a -still twin.

def step_in(delay):
    """Hidden until `delay`, then on: no fade, a frame cut."""
    if delay is None or delay <= 0:
        return ""
    t = delay + 0.01
    return (f'<animate attributeName="opacity" values="0;1" keyTimes="0;{delay / t:.4f}" calcMode="discrete" '
            f'dur="{t:.2f}s" fill="freeze"/>')


def _ease_out(i, steps, power=2.3):
    return 1.0 - (1.0 - i / steps) ** power


def power_on(uid, x, y, w, h, inner, start=0.08, dur=0.34, steps=6):
    """CRT power-on: a hot line flashes across the middle of the screen and the picture opens
    out of it, top and bottom at once, in `steps` stops. The full picture is the base value."""
    total = start + dur + 0.01
    cy = y + h / 2
    ys, hs, kt = [f"{cy:.1f}"], ["0"], ["0"]
    ys.append(f"{cy - 1:.1f}")
    hs.append("2")
    kt.append(f"{start / total:.4f}")
    for k in range(1, steps + 1):
        hh = max(2.0, h * _ease_out(k, steps))
        ys.append(f"{cy - hh / 2:.1f}")
        hs.append(f"{hh:.1f}")
        kt.append(f"{(start + dur * k / steps) / total:.4f}")
    kts = ";".join(kt)
    clip = (f'<defs><clipPath id="{uid}"><rect x="{_f(x)}" y="{_f(y)}" width="{_f(w)}" height="{_f(h)}">'
            f'<animate attributeName="y" values="{";".join(ys)}" keyTimes="{kts}" calcMode="discrete" dur="{total:.2f}s" fill="freeze"/>'
            f'<animate attributeName="height" values="{";".join(hs)}" keyTimes="{kts}" calcMode="discrete" dur="{total:.2f}s" fill="freeze"/>'
            f'</rect></clipPath></defs>')
    off = (start + dur * 2 / steps) / total
    flash = (f'<rect x="{_f(x + 2)}" y="{cy - 1:.1f}" width="{_f(w - 4)}" height="2" fill="{GLOW["hot"]}" opacity="0">'
             f'<animate attributeName="opacity" values="0;1;0" keyTimes="0;{start / total:.4f};{off:.4f}" '
             f'calcMode="discrete" dur="{total:.2f}s" fill="freeze"/></rect>')
    return f'{clip}<g clip-path="url(#{uid})">{inner}</g>{flash}'


def roll(x, y, w, h, period=9.0, begin=2.0, band=14):
    """Now and then a faint brighter band rolls down the tube, in steps, then the screen rests."""
    steps = 12
    travel = 0.14
    ys = [f"{y + (h - band) * i / (steps - 1):.1f}" for i in range(steps)]
    kt = [f"{travel * i / steps:.4f}" for i in range(steps)] + [f"{travel:.4f}", "1"]
    return (f'<rect x="{_f(x)}" y="{ys[0]}" width="{_f(w)}" height="{band}" fill="{GLOW["hot"]}" opacity="0">'
            f'<animate attributeName="y" values="{";".join(ys)};{ys[-1]};{ys[0]}" keyTimes="{";".join(kt)}" '
            f'calcMode="discrete" dur="{period}s" begin="{begin}s" repeatCount="indefinite"/>'
            f'<animate attributeName="opacity" values="{";".join(["0.05"] * steps)};0;0" keyTimes="{";".join(kt)}" '
            f'calcMode="discrete" dur="{period}s" begin="{begin}s" repeatCount="indefinite"/></rect>')


def flip(a, b, period=1.2, begin=0.0, rhythm="01"):
    """Two sprite frames. `rhythm` spells which frame shows in each equal step of the
    period ("0" = a, "1" = b), so a sprite can act: wave three times and rest, crackle
    unevenly, glint once in a while. Frame a is the still."""
    n = len(rhythm)
    times = ";".join(f"{i / n:.4f}" for i in range(n))

    def anim(on):
        vals = ";".join("1" if (ch == "1") == on else "0" for ch in rhythm)
        return (f'<animate attributeName="opacity" values="{vals}" keyTimes="{times}" calcMode="discrete" '
                f'dur="{period}s" begin="{begin}s" repeatCount="indefinite"/>')
    return f'<g>{anim(False)}{a}</g><g opacity="0">{anim(True)}{b}</g>'


def frames(svgs, period=2.4, begin=0.0, order=None):
    """Multi-frame stepped sprite animation. `order` lists the frame index shown at each
    equal step of `period` (default: 0..len-1). Frame 0 is the resting/still base frame."""
    seq = list(range(len(svgs))) if order is None else list(order)
    n = len(seq)
    times = ";".join(f"{i / n:.4f}" for i in range(n))
    out = []
    for idx, svg in enumerate(svgs):
        vals = ";".join("1" if s == idx else "0" for s in seq)
        op = "" if idx == 0 else ' opacity="0"'
        out.append(f'<g{op}><animate attributeName="opacity" values="{vals}" keyTimes="{times}" '
                   f'calcMode="discrete" dur="{period}s" begin="{begin}s" repeatCount="indefinite"/>{svg}</g>')
    return "".join(out)


def sparkle(sx, sy, unit, colour, period=5.4, begin=0.8):
    """A 4-point pixel sparkle (+ then a dot) that pops briefly, for an award's sheen."""
    u = unit
    plus = f"M{sx:g} {sy - u:g}h{u:g}v{u * 3:g}h-{u:g}ZM{sx - u:g} {sy:g}h{u * 3:g}v{u:g}h-{u * 3:g}Z"
    dot = f"M{sx:g} {sy:g}h{u:g}v{u:g}h-{u:g}Z"
    kt = "0;0.06;0.10;0.14;0.18;1"
    return (f'<g shape-rendering="crispEdges">'
            f'<path d="{plus}" fill="{colour}" opacity="0">'
            f'<animate attributeName="opacity" values="0;0;1;0;0;0" keyTimes="{kt}" calcMode="discrete" '
            f'dur="{period}s" begin="{begin}s" repeatCount="indefinite"/></path>'
            f'<path d="{dot}" fill="{colour}" opacity="0">'
            f'<animate attributeName="opacity" values="0;1;0;1;0;0" keyTimes="{kt}" calcMode="discrete" '
            f'dur="{period}s" begin="{begin}s" repeatCount="indefinite"/></path></g>')


def count_up(draw, value, start=None, frames=10, dur=0.7):
    """A number that races up and settles (ease-out over `frames` ticks), then holds.
    draw(n) returns the svg for one value. start=None: just the final value."""
    final = draw(value)
    if start is None or not value:
        return final
    total = start + dur + 0.01
    out = []
    marks = [0] + [start + dur * i / frames for i in range(1, frames)]
    for i, t0 in enumerate(marks):
        n = round(value * (1 - (1 - i / frames) ** 3))
        t1 = marks[i + 1] if i + 1 < len(marks) else start + dur
        out.append(f'<g opacity="0"><animate attributeName="opacity" values="0;1;0" '
                   f'keyTimes="0;{t0 / total:.4f};{t1 / total:.4f}" calcMode="discrete" dur="{total:.2f}s" '
                   f'fill="freeze"/>{draw(n)}</g>')
    out.append(f'<g>{step_in(start + dur)}{final}</g>')
    return "".join(out)


LIVE_W, LIVE_H = 376, 212     # LeetCode and picoGym modules, two to a row


def reading_frame(ts, theme, source, handle, icon=None, w=LIVE_W, h=LIVE_H, top=40, foot=30):
    """A live reading's module: its source silkscreened top left (after an optional mark), the
    handle top right, and a screen filling the rest above a one-line footer.
    Returns (svg, (sx, sy, sw, sh)): draw the reading inside that screen, then glass()."""
    s = PANEL[theme]
    x = 18
    out = [panel(theme, 0, 0, w, h, screws=False)]
    if icon:
        out.append(mark(icon, x, 13, 15, s["text"]))
        x += 22
    out.append(label(ts, source, x, 25, s["text"], 11.5))
    out.append(ts.text(handle, "semi", 12.5, w - 18, 25, s["muted"], anchor="end")[0])
    sx, sy, sw, sh = 16, top, w - 32, h - top - foot - 3
    out.append(screen(theme, sx, sy, sw, sh, 5))
    return "".join(out), (sx, sy, sw, sh)


def footnote(ts, theme, text, w=LIVE_W, h=LIVE_H):
    """The quiet line under a reading's screen."""
    s = PANEL[theme]
    size = fit(text, "body", 12.5, w - 36)
    return ts.text(text, "body", size, 18, h - 15, s["muted"])[0]


def segments(x, y, n, lit, w, h, gap, on, off, start=None, step=0.025, vertical=False, r=1):
    """An LED bar meter: `n` segments, the first `lit` on. Animated, the lit ones come on
    one after another from the base, like a VU meter rising to its reading."""
    out = []
    for i in range(n):
        if vertical:
            sx, sy, sw, sh = x, y - (i + 1) * (h + gap) + gap, w, h
        else:
            sx, sy, sw, sh = x + i * (w + gap), y, w, h
        is_on = i < lit
        motion = step_in(start + i * step) if start is not None and is_on else ""
        out.append(f'<rect x="{_f(sx)}" y="{_f(sy)}" width="{_f(sw)}" height="{_f(sh)}" rx="{r}" '
                   f'fill="{on if is_on else off}">{motion}</rect>')
    return "".join(out)
