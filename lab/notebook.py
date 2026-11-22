"""Shared lab equipment: README block editing, palettes, type, pixel chrome and motion.

Every image in the lab draws its lettering as vector paths from the fonts in
lab/fonts, so GitHub shows the same type to everyone, whatever fonts they have.
"""
import datetime as dt
import math
import os
import random
import re
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

# Type: Inter Bold for titles, Chakra Petch for text and every digit, Pixelify Sans for
# the wordmark and a few word tags (its 2, 5 and B misread small, so never for digits).
FACES = {"title": "Inter-Bold.otf", "body": "ChakraPetch-Regular.ttf", "body-bold": "ChakraPetch-Bold.ttf",
         "pixel": "PixelifySans-Bold.ttf"}
TRACK = {"title": -0.03}     # default tracking per face, in em

# The same DOS palette as the portfolio (portfolio-fin/app/globals.css).
BRAND = dict(ink="#1313ba", paper="#f6f6fc", lavender="#cbcbef", neon="#6666fd", deep="#0a0a5d")
THEMES = ("dark", "light")   # every picture ships in both; PAPER below holds each theme's colours


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
    import hashlib
    return hashlib.sha1("".join(parts).encode()).hexdigest()[:8]


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


# ------------------------------------------------------------------ pixel chrome

def notch(x, y, w, h, s=4):
    """A rectangle whose corners step in by one pixel block, like the portfolio's panels."""
    return (f"M{x + s} {y}H{x + w - s}V{y + s}H{x + w}V{y + h - s}H{x + w - s}V{y + h}"
            f"H{x + s}V{y + h - s}H{x}V{y + s}H{x + s}Z")


def mark(name, x, y, size, fill):
    """A one-colour icon from lab/icons.py, fitted into a size × size box."""
    from icons import ICONS
    box, d = ICONS[name.lower()]
    return (f'<svg x="{x:g}" y="{y:g}" width="{size:g}" height="{size:g}" viewBox="{box}">'
            f'<path fill="{fill}" d="{d}"/></svg>')


def pixels(rows, x, y, scale, palette):
    """Draw a pixel map; palette maps characters to colours, other cells stay empty."""
    out = []
    for key, colour in palette.items():
        d = "".join(f"M{x + c * scale:g} {y + r * scale:g}h{scale:g}v{scale:g}h-{scale:g}Z"
                    for r, row in enumerate(rows) for c, v in enumerate(row) if v == key)
        if d:
            out.append(f'<path d="{d}" fill="{colour}"/>')
    return f'<g shape-rendering="crispEdges">{"".join(out)}</g>'


# ------------------------------------------------------------------ type as paths

@lru_cache(maxsize=None)
def _font(face):
    from matplotlib.font_manager import FontProperties, get_font
    if face == "fallback":   # Greek and symbols the display faces lack; ships with matplotlib
        import matplotlib
        path = str(Path(matplotlib.get_data_path()) / "fonts" / "ttf" / "DejaVuSans.ttf")
    else:
        path = str(FONTS / FACES[face])
    # Advances come from FreeType's hinting at whole pixels. Older matplotlib hints at 8x
    # horizontal resolution by default (text.hinting_factor), which spreads every letter 8x
    # apart; ask for 1x so spacing doesn't depend on the installed version.
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
    adv = ft.load_char(ord(ch)).horiAdvance / 64
    if ch.isspace():
        return "", adv
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
    """Text as reusable glyph paths: each glyph is defined once in <defs> and placed with <use>.

    text(..., reveal=(start, rate)) makes glyphs appear one by one like a typewriter,
    starting at `start` seconds, `rate` seconds apart. Returns (svg, time typing ends).
    """

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


# ================================================================== lab sheets
# The profile's card language since Nov 2026, taken from the portfolio's paper
# sheets: a torn pixel edge top and bottom, square notched pixel geometry and a
# hard offset shadow. Pixelify for numbers and tags, Chakra Petch for text,
# Inter Bold for titles. Motion is stepped like a sprite: sheets print in row by
# row, counters tick, pixel art swaps between two frames. Nothing eases.


PAPER = {
    "light": dict(sheet=BRAND["paper"], line=BRAND["lavender"], shadow=BRAND["lavender"], text=BRAND["ink"],
                  muted="#4747b8", soft="#e4e4f7", well="#dedef4", chip="#ffffff", led=BRAND["neon"],
                  heat=["#dedef4", "#a8a8f6", BRAND["neon"], BRAND["ink"], BRAND["deep"]],
                  easy="#1a7f37", medium="#b45309", hard="#cf222e", page="#ffffff"),
    "dark": dict(sheet="#0b0b52", line="#2c2c96", shadow="#04042a", text=BRAND["paper"], muted=BRAND["lavender"],
                 soft="#17177a", well="#1a1a6c", chip="#10105e", led="#8f8fff",
                 heat=["#1a1a6c", "#3a3ab5", BRAND["neon"], "#a8a8f6", BRAND["paper"]],
                 easy="#3fb950", medium="#ffb02e", hard="#ff5c6c", page="#0d1117"),
}
TEAR, SHADE = 6, 4      # torn edge depth and shadow offset, px


def _torn(n, seed, depth=3):
    rng = random.Random(seed)
    k, out = rng.randint(0, depth), []
    for _ in range(n):
        k = max(0, min(depth, k + rng.choice((-1, 0, 1, 1, -1))))
        out.append(k * TEAR // depth)
    return out


def torn_path(w, h, seed, step=4, top=True, bottom=True):
    """A sheet with torn pixel edges: every `step` px the edge steps up or down a notch."""
    n = math.ceil(w / step)
    t = _torn(n, f"{seed}t") if top else [0] * n
    b = _torn(n, f"{seed}b") if bottom else [0] * n
    d = f"M0 {t[0]}"
    for i, y in enumerate(t):
        d += f"V{y}H{min(w, (i + 1) * step)}"
    for i in reversed(range(n)):
        d += f"V{h - b[i]}H{i * step}"
    return d + "Z"


def sheet(theme, w, h, seed, top=True, bottom=True):
    """The paper the card is on and its hard shadow. Content sits in (0..w-SHADE, TEAR..h-SHADE-TEAR)."""
    s = PAPER[theme]
    d = torn_path(w - SHADE, h - SHADE, seed, top=top, bottom=bottom)
    return (f'<g shape-rendering="crispEdges"><path transform="translate({SHADE} {SHADE})" d="{d}" fill="{s["shadow"]}"/>'
            f'<path d="{d}" fill="{s["sheet"]}" stroke="{s["line"]}" stroke-width="1"/></g>')


def box(x, y, w, h, fill, s=3, stroke=None):
    """A notched pixel box: each corner steps in by one block."""
    st = f' stroke="{stroke}" stroke-width="1"' if stroke else ""
    return f'<path d="{notch(x, y, w, h, s)}" fill="{fill}"{st} shape-rendering="crispEdges"/>'


def sprite_at(rows, x, y, scale, palette=None):
    colours = palette or dict(P=BRAND["paper"], L=BRAND["lavender"], N=BRAND["neon"], D=BRAND["deep"])
    return pixels(rows, x, y, scale, colours)


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


BAYER = [[0, 8, 2, 10], [12, 4, 14, 6], [3, 11, 1, 9], [15, 7, 13, 5]]


def materialize(uid, w, h, start=0.0, dur=0.7, cell=None):
    """The sheet resolves out of pixel noise: an ordered (Bayer) dither that also sweeps
    downward, so it reads as a retro screen drawing the card in. Each uid shifts the dither
    matrix, so neighbouring cards never resolve in the same pattern.
    Returns (defs, attribute for the group). The finished card is the base state."""
    import zlib
    cell = cell or (8 if w * h < 60000 else 12)
    seed = zlib.crc32(uid.encode())
    ox, oy = seed % 4, (seed // 4) % 4
    cols, rows = math.ceil(w / cell), math.ceil(h / cell)
    groups = {}
    for r in range(rows):
        band = round(7 * r / max(rows - 1, 1))
        for c in range(cols):
            order = BAYER[(r + oy) % 4][(c + ox) % 4] + band
            groups.setdefault(order, []).append(f"M{c * cell} {r * cell}h{cell}v{cell}h-{cell}Z")
    last = max(groups)
    total = start + dur + 0.01
    paths = []
    for order, cells in sorted(groups.items()):
        t = (start + dur * order / last) / total
        paths.append(f'<path d="{"".join(cells)}" fill="#000" opacity="0"><animate attributeName="opacity" '
                     f'values="1;0" keyTimes="0;{t:.4f}" calcMode="discrete" dur="{total:.2f}s" fill="freeze"/></path>')
    return (f'<mask id="{uid}" maskUnits="userSpaceOnUse" x="0" y="0" width="{w}" height="{h}">'
            f'<rect width="{w}" height="{h}" fill="#fff"/>{"".join(paths)}</mask>',
            f' mask="url(#{uid})"')


def print_clip(uid, w, h, start=0.0, steps=None, dur=0.7):
    """Every sheet's entrance; kept under its old name for the generators that call it."""
    return materialize(uid, w, h, start, dur)


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


def blink(period=1.0, begin=0.0, on=0.5, low=0, rhythm=None):
    """An LED. Without a rhythm it is on for `on` of the period; with one, "1" is lit and
    "0" is dim for each equal step, for flickers that do not feel metronomic."""
    if rhythm:
        n = len(rhythm)
        vals = ";".join("1" if ch == "1" else str(low) for ch in rhythm)
        times = ";".join(f"{i / n:.4f}" for i in range(n))
    else:
        vals, times = f"1;{low}", f"0;{on}"
    return (f'<animate attributeName="opacity" values="{vals}" keyTimes="{times}" calcMode="discrete" '
            f'dur="{period}s" begin="{begin}s" repeatCount="indefinite"/>')


def count_up(ts, value, face, size, x, y, fill, start=None, frames=10, dur=0.7, anchor="start", unit=None):
    """A number that races up and settles (ease-out over `frames` ticks), then holds.
    unit=(text, face, size, fill, dy) is set 8 px after each frame's number, so it travels
    with the count instead of waiting at the final width. start=None: just the number."""
    def frame(n):
        out = ts.text(f"{n:,}", face, size, x, y, fill, anchor=anchor)[0]
        if unit:
            text, uface, usize, ufill, dy = unit
            out += ts.text(text, uface, usize, x + text_width(f"{n:,}", face, size) + 8, y + dy, ufill)[0]
        return out
    final = frame(value)
    if start is None or not value:
        return final
    total = start + dur + 0.01
    out = []
    marks = [0] + [start + dur * i / frames for i in range(1, frames)]
    for i, t0 in enumerate(marks):
        n = round(value * (1 - (1 - i / frames) ** 3))
        t1 = marks[i + 1] if i + 1 < len(marks) else start + dur
        g = frame(n)
        out.append(f'<g opacity="0"><animate attributeName="opacity" values="0;1;0" '
                   f'keyTimes="0;{t0 / total:.4f};{t1 / total:.4f}" calcMode="discrete" dur="{total:.2f}s" '
                   f'fill="freeze"/>{g}</g>')
    out.append(f'<g>{step_in(start + dur)}{final}</g>')
    return "".join(out)


def fit(text, face, size, room, floor=8):
    while text_width(text, face, size) > room and size > floor:
        size -= 0.5
    return size


def tag(ts, theme, text, x, y, anchor="start", fill=None, colour=None):
    """A small Pixelify label in a notched chip. Returns (svg, width)."""
    s = PAPER[theme]
    w = text_width(text, "pixel", 10.5) + 14
    x0 = x - (w if anchor == "end" else 0)
    return (box(x0, y, w, 18, fill or s["soft"], 2)
            + ts.text(text, "pixel", 10.5, x0 + 7, y + 13, colour or s["text"])[0]), w


# ------------------------------------------------------------------ live cards
STAT_W, STAT_H = 252, 188     # three to a row on wide screens, stacked on phones
# 252 × 212 sheets, three to a row: a source tag with a blinking LED, a big number
# that ticks up, a pixel figure that steps in, and one quiet line at the foot.

def reading(ts, theme, seed, source, handle, value, unit, animate):
    s = PAPER[theme]
    right = STAT_W - SHADE - 14
    out = [sheet(theme, STAT_W, STAT_H, seed),
           f'<rect x="14" y="17" width="8" height="8" fill="{s["led"]}" shape-rendering="crispEdges">'
           f'{blink(3.6, 1.5, rhythm="111111101101") if animate else ""}</rect>',
           ts.text(source, "body-bold", 13, 29, 25.5, s["text"], tracking=1.2)[0],
           ts.text(handle, "body", 12, right, 25, s["muted"], anchor="end")[0],
           count_up(ts, value, "title", 36, 14, 70, s["text"], 0.55 if animate else None,
                    unit=(unit, "body", 13.5, s["muted"], -1))]
    return out


def foot(ts, theme, text):
    s = PAPER[theme]
    text = text if text_width(text, "body", 12) < STAT_W - 40 else text[:40].rstrip() + "…"
    return ts.text(text, "body", 12, 14, STAT_H - SHADE - 18, s["muted"])[0]


def printed(uid, w, h, body, animate):
    """Wrap a card body in its print-in clip when animated."""
    inner = "".join(body)
    if not animate:
        return inner
    defs, clip = print_clip(uid, w, h)
    return f"<defs>{defs}</defs><g{clip}>{inner}</g>"


COLUMN = 760   # the README's content column: two 376 cards, or three 252 cards, with their gaps


def wide_scene(stem, narrow, alt, folder="assets", width=COLUMN):
    """<picture> for a full-width animated image with a phone layout: still or moving, by theme."""
    def src(media, name):
        return f'<source media="{media}" srcset="{folder}/{name}.svg">'
    phone, still, dark = "(max-width: 600px)", "(prefers-reduced-motion: reduce)", "(prefers-color-scheme: dark)"
    return ('<picture>'
            + src(f"{phone} and {still} and {dark}", f"{narrow}-still-dark") + src(f"{phone} and {still}", f"{narrow}-still-light")
            + src(f"{phone} and {dark}", f"{narrow}-dark") + src(phone, f"{narrow}-light")
            + src(f"{still} and {dark}", f"{stem}-still-dark") + src(still, f"{stem}-still-light")
            + src(dark, f"{stem}-dark")
            + f'<img src="{folder}/{stem}-light.svg" alt="{esc(alt)}" width="{width}"></picture>')


def wrap(text, face, size, width):
    """Greedy line breaking by measured width."""
    lines, line = [], ""
    for word in text.split():
        trial = f"{line} {word}".strip()
        if line and text_width(trial, face, size) > width:
            lines.append(line)
            line = word
        else:
            line = trial
    return lines + ([line] if line else [])


def paragraph(ts, text, face, size, x, y, width, fill, leading=1.45):
    """Wrapped lines from baseline y. Returns (svg, baseline of the last line)."""
    lines = wrap(text, face, size, width)
    out = "".join(ts.text(line, face, size, x, y + i * size * leading, fill)[0] for i, line in enumerate(lines))
    return out, y + (len(lines) - 1) * size * leading
