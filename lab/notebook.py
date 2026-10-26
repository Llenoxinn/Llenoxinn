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

FACES = {
    "display": "Boldonse-Regular.ttf",          # the name and big IDs: heavy, condensed, a little menacing
    "label": "Jura-Medium.ttf",                 # instrument lettering: labels and readouts
    "text": "Jura-Medium.ttf",                  # data and captions
    "wordmark": "Tektur-Medium.ttf",            # base letterforms for the custom name treatment
    "mono": "GeistMono-Regular.ttf",            # terminal, hex, sequences
    "mono-bold": "GeistMono-Bold.ttf",
    "hand": "NothingYouCouldDo-Regular.ttf",    # red-pen margin notes
    "tape": "BigShoulders-Bold.ttf",            # label-maker tape
}
# older names used around the lab
FACES.update({"serif": FACES["display"], "type": FACES["text"], "type-bold": FACES["label"]})

# One palette for every figure: the lab is on red alert. "paper" is the aged
# card stock used for labels in both themes, the way a real label stays cream
# on a dark cabinet. A/C/G/T keep the standard sequencer colours.
THEMES = {
    "dark": dict(bg="#0d1117", panel="#14070a", panel2="#1f0a10", edge="#5a1622", ink="#f4e9e9",
                 muted="#b08f93", faint="#2a181c", paper="#efe6cf", paper_ink="#3b2f1c",
                 pen="#ff5c72", red="#ff1f3d", red_dim="#8b0018", green="#3fb950", blue="#58a6ff",
                 amber="#ffb02e", orange="#ff7a45", purple="#bc8cff", glow="#ff1f3d",
                 A="#3fb950", C="#58a6ff", G="#ffb02e", T="#ff1f3d"),
    "light": dict(bg="#ffffff", panel="#fff6f6", panel2="#ffecec", edge="#efc7c9", ink="#1f1416",
                  muted="#7a5a5e", faint="#fbeaea", paper="#fbf6e8", paper_ink="#3b2f1c",
                  pen="#d1002a", red="#e0002a", red_dim="#f7b3bf", green="#1a7f37", blue="#0969da",
                  amber="#b45309", orange="#c2410c", purple="#8250df", glow="#e0002a",
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


def text_width(text, face, size, tracking=0.0):
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

    def text(self, text, face, size, x, y, fill, anchor="start", tracking=0.0, jitter=0.0,
             opacity=None, reveal=None, seed=0, attrs=""):
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
