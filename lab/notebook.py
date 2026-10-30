"""Shared lab equipment: README block editing, lab time, palettes, and type.

Every image in the lab draws its lettering as vector paths from the fonts in
lab/fonts, so GitHub shows the same type to everyone, whatever fonts they have.
"""
import datetime as dt
import random
import re
from functools import lru_cache
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
README = ROOT / "README.md"
FONTS = ROOT / "lab" / "fonts"
ASSETS = ROOT / "assets"
LAB = "https://github.com/Llenoxinn/Llenoxinn/blob/HEAD"  # absolute: relative links break on the profile page
USER = "Llenoxinn"
MANILA = dt.timezone(dt.timedelta(hours=8), "Asia/Manila")

# Notion /dev's pairing: Inter for headlines and text, iA Writer Mono for commands and code.
# Pixelify stays for the pixel accents.
FACES = {
    "headline": "Inter-Bold.otf",
    "label": "Inter-SemiBold.otf",
    "text": "Inter-Regular.otf",
    "code": "iAWriterMonoS-Regular.ttf",
    "code-bold": "iAWriterMonoS-Bold.ttf",
    "display": "PixelifySans-Bold.ttf",
    "wordmark": "PixelifySans-Bold.ttf",
    "mono": "iAWriterMonoS-Regular.ttf",
    "mono-bold": "iAWriterMonoS-Bold.ttf",
    "hand": "Inter-Regular.otf",
    "tape": "PixelifySans-Bold.ttf",
}
# Default tracking per face, in em: tight headlines as on notion.com/product/dev
TRACK = {"headline": -0.034, "label": -0.01, "code": -0.009, "code-bold": -0.009}
# older names used around the lab
FACES.update({"serif": FACES["display"], "type": FACES["text"], "type-bold": FACES["label"]})

# The same DOS palette as portfolio-fin/app/globals.css. Page backgrounds stay
# GitHub-native so the unframed scientific figures blend into the profile.
BRAND = dict(ink="#1313ba", paper="#f6f6fc", lavender="#cbcbef", neon="#6666fd", deep="#0a0a5d")
# "red" is the legacy accent key used by the scientific instruments. It now
# resolves to blue; A/C/G/T retain the sequencer's meaningful base colours.
THEMES = {
    "dark": dict(bg="#0d1117", panel="#101035", panel2=BRAND["deep"], edge="#474780", ink=BRAND["paper"],
                 muted=BRAND["lavender"], faint="#1b1b3a", paper=BRAND["paper"], paper_ink=BRAND["ink"],
                 pen=BRAND["lavender"], red=BRAND["neon"], red_dim="#343486", green="#3fb950", blue="#58a6ff",
                 amber="#ffb02e", orange="#ff7a45", purple="#bc8cff", glow=BRAND["neon"],
                 A="#3fb950", C="#58a6ff", G="#ffb02e", T="#ff1f3d"),
    "light": dict(bg="#ffffff", panel=BRAND["paper"], panel2="#e8e8fa", edge=BRAND["lavender"], ink=BRAND["ink"],
                  muted="#4b4b87", faint="#eeeefa", paper=BRAND["paper"], paper_ink=BRAND["ink"],
                  pen=BRAND["ink"], red=BRAND["ink"], red_dim=BRAND["lavender"], green="#1a7f37", blue="#0969da",
                  amber="#b45309", orange="#c2410c", purple="#8250df", glow=BRAND["ink"],
                  A="#1a7f37", C="#0969da", G="#24292f", T="#e0002a"),
}


def now_manila() -> dt.datetime:
    return dt.datetime.now(MANILA)


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


def scene(stem, alt, width="100%", folder="assets"):
    """<picture> for an animated image: a still for reduced motion, then dark/light."""
    return (f'<picture>'
            f'<source media="(prefers-reduced-motion: reduce) and (prefers-color-scheme: dark)" srcset="{folder}/{stem}-still-dark.svg">'
            f'<source media="(prefers-reduced-motion: reduce)" srcset="{folder}/{stem}-still-light.svg">'
            f'<source media="(prefers-color-scheme: dark)" srcset="{folder}/{stem}-dark.svg">'
            f'<img src="{folder}/{stem}-light.svg" alt="{esc(alt)}" width="{width}"></picture>')


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


# ------------------------------------------------------------------ motion
# One-shot entrances only. Every animation begins at 0 s and holds its start value
# until its turn, so renderers without SMIL show the finished picture. Cards and
# tiles change opacity only; the hero, which also moves, ships a still for
# prefers-reduced-motion.

EASE_OUT = "0.23 1 0.32 1"


def _hold(delay, dur):
    total = delay + dur
    return total, f'keyTimes="0;{delay / total:.3f};1" calcMode="spline" keySplines="0 0 1 1;{EASE_OUT}"'


def grow(attr, final, delay, dur=0.5):
    """Hold at zero until `delay`, then ease out to `final`."""
    total, timing = _hold(delay, dur)
    return f'<animate attributeName="{attr}" values="0;0;{final}" {timing} dur="{total:.2f}s" fill="freeze"/>'


def fade(delay, dur=0.3):
    return grow("opacity", 1, delay, dur)


def rise(delay, dy=12, dur=0.4):
    """Fade in while settling `dy` px upward. Movement: use only where a still exists."""
    total, timing = _hold(delay, dur)
    return (fade(delay, dur) + f'<animateTransform attributeName="transform" type="translate" '
            f'values="0 {dy};0 {dy};0 0" {timing} dur="{total:.2f}s" fill="freeze"/>')


def caret(x, y, w, h, colour, start, blinks=3):
    """A block caret that appears when typing ends, blinks a few times, then holds steady."""
    beats = ";".join(["1;0"] * blinks + ["1"])
    n = 2 * blinks + 1
    times = ";".join(f"{i / (n - 1):.3f}" for i in range(n))
    return (f'<rect x="{x:.1f}" y="{y:.1f}" width="{w}" height="{h}" fill="{colour}" opacity="0">'
            f'<set attributeName="opacity" to="1" begin="{start:.2f}s"/>'
            f'<animate attributeName="opacity" values="{beats}" keyTimes="{times}" calcMode="discrete" '
            f'begin="{start:.2f}s" dur="{blinks * 0.9:.1f}s" fill="freeze"/></rect>')


# Ambient motion for the hero and section headers. These loop, so every image that
# uses them ships a still twin that <picture> serves under prefers-reduced-motion.

def packet(path, colour, dur, begin=0.0, size=6):
    """A data packet that travels a circuit trace, fading in and out at the ends."""
    h = size / 2
    return (f'<rect x="{-h}" y="{-h}" width="{size}" height="{size}" fill="{colour}" opacity="0">'
            f'<animateMotion path="{path}" dur="{dur}s" begin="{begin}s" repeatCount="indefinite" '
            f'keyPoints="0;1" keyTimes="0;1" calcMode="linear"/>'
            f'<animate attributeName="opacity" values="0;1;1;0" keyTimes="0;0.1;0.85;1" dur="{dur}s" '
            f'begin="{begin}s" repeatCount="indefinite"/></rect>')


def dot_grid(w, h, colour, seed, pitch=20, opacity=0.14, twinkle=0, x0=0, y0=0):
    """A faint dot matrix; `twinkle` of its dots slowly brighten and fade, out of step."""
    rng = random.Random(seed)
    dots = [(x, y) for x in range(x0 + pitch // 2, x0 + w, pitch) for y in range(y0 + pitch // 2, y0 + h, pitch)]
    d = "".join(f"M{x - 1} {y - 1}h2v2h-2Z" for x, y in dots)
    out = [f'<path d="{d}" fill="{colour}" opacity="{opacity}"/>']
    for x, y in rng.sample(dots, min(twinkle, len(dots))):
        dur = rng.uniform(2.6, 5.2)
        out.append(f'<rect x="{x - 1.5}" y="{y - 1.5}" width="3" height="3" fill="{colour}" opacity="0">'
                   f'<animate attributeName="opacity" values="0;0.85;0" dur="{dur:.1f}s" '
                   f'begin="{rng.uniform(0, 4):.1f}s" repeatCount="indefinite"/></rect>')
    return "".join(out)


def bob(dy=4, dur=4.0, begin=0.0):
    """A slow float, eased at both ends, for toasts and the scientist."""
    return (f'<animateTransform attributeName="transform" type="translate" values="0 0;0 {-dy};0 0" '
            f'keyTimes="0;0.5;1" calcMode="spline" keySplines="0.45 0 0.55 1;0.45 0 0.55 1" '
            f'dur="{dur}s" begin="{begin}s" repeatCount="indefinite"/>')


def pixels(rows, x, y, scale, palette):
    """Draw a pixel map; palette maps characters to colours, other cells stay empty."""
    out = []
    for key, colour in palette.items():
        d = "".join(f"M{x + c * scale:g} {y + r * scale:g}h{scale:g}v{scale:g}h-{scale:g}Z"
                    for r, row in enumerate(rows) for c, v in enumerate(row) if v == key)
        if d:
            out.append(f'<path d="{d}" fill="{colour}"/>')
    return f'<g shape-rendering="crispEdges">{"".join(out)}</g>'


# ------------------------------------------------------------------ cards
# The profile's own card language: a pale sheet with a hairline, an ink terminal
# strip for commands, mono for code and heavy display type for headlines.

SHEET = {
    "dark": dict(sheet="#10103a", edge="#34348a", text=BRAND["paper"], muted="#b4b4f0", soft="#2a2a6e",
                 well="#1f1f55", heat=["#1f1f55", "#3a3ab5", BRAND["neon"], "#a8a8f6", BRAND["paper"]],
                 easy="#3fb950", medium="#ffb02e", hard="#ff4d5e", shadow=BRAND["deep"]),
    "light": dict(sheet=BRAND["paper"], edge=BRAND["lavender"], text=BRAND["ink"], muted="#4f4fc4", soft="#e4e4f7",
                  well="#e4e4f7", heat=["#e4e4f7", "#a8a8f6", BRAND["neon"], BRAND["ink"], BRAND["deep"]],
                  easy="#1a7f37", medium="#b45309", hard="#cf222e", shadow=BRAND["lavender"]),
}
STRIP = 30


def card(theme, w, h, radius=6):
    """The sheet every card sits on."""
    s = SHEET[theme]
    return (f'<rect x="1" y="1" width="{w - 2}" height="{h - 2}" rx="{radius}" fill="{s["sheet"]}" '
            f'stroke="{s["edge"]}" stroke-width="1.5"/>')


def strip(ts, w, y, parts, start=None, rate=0.022, radius=6, top=False):
    """An ink terminal strip. parts = [(text, colour), ...]; types itself out from `start`.

    Returns (svg, time typing ends). top=True rounds the top corners instead of the bottom.
    """
    b = BRAND
    if top:
        shape = f'M1 {y + STRIP}V{y + radius + 1}Q1 {y + 1} {radius + 1} {y + 1}H{w - radius - 1}Q{w - 1} {y + 1} {w - 1} {y + radius + 1}V{y + STRIP}Z'
    else:
        shape = f'M1 {y}H{w - 1}V{y + STRIP - radius - 1}Q{w - 1} {y + STRIP - 1} {w - radius - 1} {y + STRIP - 1}H{radius + 1}Q1 {y + STRIP - 1} 1 {y + STRIP - radius - 1}Z'
    out, x, t = [f'<path d="{shape}" fill="{b["ink"]}"/>'], 14, start
    for text, colour in parts:
        g, t2 = ts.text(text, "code", 12.5, x, y + 19.5, colour, reveal=(t, rate) if start is not None else None)
        out.append(g)
        x += text_width(text, "code", 12.5)
        t = t2 if start is not None else t
    if start is not None:
        out.append(caret(x + 2, y + 9, 7, 13, b["lavender"], t))
    return "".join(out), (t if start is not None else 0)


def strip_tag(ts, w, text, live=False, y=0):
    """Right-aligned status in a top strip; a live tag's dot pulses three times, then rests."""
    b = BRAND
    out = ts.text(text, "code", 12, w - 14, y + 19.5, b["lavender"], anchor="end")[0]
    if live:
        cx = w - 14 - text_width(text, "code", 12) - 8
        out += (f'<circle cx="{cx:.1f}" cy="{y + 15.5}" r="3" fill="{b["paper"]}">'
                f'<animate attributeName="opacity" values="1;0.25;1" dur="1.2s" begin="0.4s" repeatCount="3"/></circle>')
    return out


# Progress cards: three to a row on wide screens, stacked on phones
STAT_W, STAT_H = 252, 212


def readout(ts, theme, number, label, delay, x=14, y=82):
    """A big number with its unit, fading in once the command has typed."""
    s = SHEET[theme]
    nw = text_width(str(number), "headline", 30)
    return (f'<g opacity="1">{fade(delay)}{ts.text(str(number), "headline", 30, x, y, s["text"])[0]}'
            f'{ts.text(label, "text", 14, x + nw + 10, y - 3, s["muted"])[0]}</g>')


def footnote(ts, theme, text, delay, y=STAT_H - 16):
    s = SHEET[theme]
    while text_width(text, "code", 12) > STAT_W - 28 and len(text) > 4:
        text = text[:-2].rstrip() + "…"
    return f'<g opacity="1">{fade(delay)}{ts.text(text, "code", 12, 14, y, s["muted"])[0]}</g>'


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


def glyphs(text, face, size, x, y, anchor="start", tracking=0.0, jitter=0.0, seed=0):
    """Yield (char, transform, path data) for each visible character."""
    w = text_width(text, face, size, tracking)
    x -= {"start": 0, "middle": w / 2, "end": w}[anchor]
    rng = random.Random(f"{seed}{text}")
    for ch in text:
        d, adv = _glyph(ch, face, size)
        dy = rng.uniform(-jitter, jitter) if jitter else 0
        if d:
            yield ch, f"translate({x:.1f} {y + dy:.1f})", d
        x += adv + tracking


def svg_text(text, face, size, x, y, fill, anchor="start", tracking=0.0, jitter=0.0,
             opacity=None, attrs=""):
    """Text drawn as one <g> of glyph paths. jitter > 0 gives typewriter wobble and ink variation."""
    rng = random.Random(f"ink{text}")
    parts = []
    for _, tf, d in glyphs(text, face, size, x, y, anchor, tracking, jitter):
        ink = f' fill-opacity="{rng.uniform(0.78, 1):.2f}"' if jitter else ""
        parts.append(f'<path transform="{tf}" d="{d}"{ink}/>')
    op = f' opacity="{opacity}"' if opacity is not None else ""
    return f'<g fill="{fill}"{op}{attrs}>{"".join(parts)}</g>'


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

    def text(self, text, face, size, x, y, fill, anchor="start", tracking=None, jitter=0.0,
             opacity=None, reveal=None, seed=0, attrs=""):
        tracking = TRACK.get(face, 0) * size if tracking is None else tracking
        w = text_width(text, face, size, tracking)
        x -= {"start": 0, "middle": w / 2, "end": w}[anchor]
        rng = random.Random(f"{seed}{text}{face}")
        out = []
        t = reveal[0] if reveal else 0
        for ch in text:
            d, adv = _glyph(ch, face, size)
            if d:
                dy = rng.uniform(-jitter, jitter) if jitter else 0
                ink = f' fill-opacity="{rng.uniform(0.75, 1):.2f}"' if jitter else ""
                ref = self._ref(ch, face, size)
                if reveal:
                    out.append(f'<use href="#{ref}" xlink:href="#{ref}" x="{x:.1f}" y="{y + dy:.1f}"{ink} opacity="0">'
                               f'<set attributeName="opacity" to="1" begin="{t:.2f}s" fill="freeze"/></use>')
                else:
                    out.append(f'<use href="#{ref}" xlink:href="#{ref}" x="{x:.1f}" y="{y + dy:.1f}"{ink}/>')
            if reveal:
                t += reveal[1]
            x += adv + tracking
        op = f' opacity="{opacity}"' if opacity is not None else ""
        fl = f' fill="{fill}"' if fill else ""
        return f'<g{fl}{op}{attrs}>{"".join(out)}</g>', t

    def defs_svg(self):
        return "<defs>" + "".join(f'<path id="{i}" d="{d}"/>' for i, d in self.defs.values()) + "</defs>"


def ambient(uid, w, h, theme, seed=0, cells=9, bits=12, fade=70, opacity=1.0):
    """Unboxed atmosphere: cells and data fragments drifting through the figure.

    Everything fades out toward the edges through a soft mask, so a figure has
    no frame and seems to sit in the same fluid as the rest of the page.
    Returns (defs, body) SVG fragments; put body underneath the figure.
    """
    t = THEMES[theme]
    rng = random.Random(f"{uid}{seed}")
    ts = Typesetter(f"{uid}t")
    defs = [f'<linearGradient id="{uid}fx" x1="0" x2="1"><stop offset="0" stop-color="#000"/>'
            f'<stop offset="{fade / w:.3f}" stop-color="#fff"/><stop offset="{1 - fade / w:.3f}" stop-color="#fff"/>'
            f'<stop offset="1" stop-color="#000"/></linearGradient>'
            f'<linearGradient id="{uid}fy" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#000"/>'
            f'<stop offset="{fade / h:.3f}" stop-color="#fff"/><stop offset="{1 - fade / h:.3f}" stop-color="#fff"/>'
            f'<stop offset="1" stop-color="#000"/></linearGradient>'
            f'<mask id="{uid}fm" maskUnits="userSpaceOnUse" x="0" y="0" width="{w}" height="{h}">'
            f'<rect width="{w}" height="{h}" fill="url(#{uid}fx)"/></mask>'
            f'<mask id="{uid}m" maskUnits="userSpaceOnUse" x="0" y="0" width="{w}" height="{h}">'
            f'<g mask="url(#{uid}fm)"><rect width="{w}" height="{h}" fill="url(#{uid}fy)"/></g></mask>']
    red, ink = t["red"], t["ink"]
    out = []
    for _ in range(cells):
        r = rng.uniform(7, 19)
        x, y = rng.uniform(0, w), rng.uniform(0, h)
        dx, dy = rng.uniform(40, 140) * rng.choice((-1, 1)), rng.uniform(-30, 30)
        dur = rng.uniform(14, 30)
        nuc = rng.uniform(0.3, 0.45) * r
        out.append(f'<g opacity="{rng.uniform(0.25, 0.55) * opacity:.2f}"><g>'
                   f'<animateTransform attributeName="transform" type="translate" values="0 0;{dx:.0f} {dy:.0f};0 0" dur="{dur:.1f}s" repeatCount="indefinite"/>'
                   f'<circle cx="{x:.0f}" cy="{y:.0f}" r="{r:.1f}" fill="{red}" fill-opacity="0.10" stroke="{red}" stroke-opacity="0.55" stroke-width="1.2">'
                   f'<animate attributeName="r" values="{r:.1f};{r * 1.08:.1f};{r:.1f}" dur="{rng.uniform(3, 6):.1f}s" repeatCount="indefinite"/></circle>'
                   f'<circle cx="{x + rng.uniform(-2, 2):.0f}" cy="{y + rng.uniform(-2, 2):.0f}" r="{nuc:.1f}" fill="{red}" fill-opacity="0.45"/></g></g>')
    glyph_sets = ["0x4c", "0x6e", "ACGT", "1011", "FF", "SYN", "ACK", "GATTACA", "0110", "TLS", "CRC", "AUG", "SHA", "0xDE"]
    for _ in range(bits):
        x, y = rng.uniform(0, w), rng.uniform(0, h)
        dx = rng.uniform(60, 200) * rng.choice((-1, 1))
        dur = rng.uniform(10, 22)
        g, _ = ts.text(rng.choice(glyph_sets), "mono", rng.uniform(9, 12), x, y, ink)
        out.append(f'<g opacity="{rng.uniform(0.12, 0.3) * opacity:.2f}"><animateTransform attributeName="transform" type="translate" '
                   f'values="0 0;{dx:.0f} 0;0 0" dur="{dur:.1f}s" repeatCount="indefinite"/>{g}</g>')
    defs.append(ts.defs_svg()[len("<defs>"):-len("</defs>")])
    return "".join(defs), f'<g mask="url(#{uid}m)">{"".join(out)}</g>'
