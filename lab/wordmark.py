"""Custom lettering for the name. Four treatments of the same Tektur letterforms:

  claw     heavy slanted letters torn by three claw marks, alarm red bleeding through
  hive     the name grown as a colony of hexagonal cells, some of them infected
  stencil  military stencil, the kind sprayed on a containment crate
  breach   heavy letters with an RGB split and slices knocked out of line

Each returns (defs, body) SVG fragments placed with the baseline at (x, y).
"""
import math
import random

from notebook import _glyph, text_width

NAME = "DEXTER JUEVESANO"


def _paths(text, face, size, x, y, tracking):
    out = []
    for ch in text:
        d, adv = _glyph(ch, face, size)
        if d:
            out.append(f'<path transform="translate({x:.1f} {y:.1f})" d="{d}"/>')
        x += adv + tracking
    return "".join(out)


def width(size, tracking=2.0, face="wordmark"):
    return text_width(NAME, face, size, tracking)


def _bold(paths, fill, weight):
    """Embolden outline type by stroking it in its own colour."""
    return (f'<g fill="{fill}" stroke="{fill}" stroke-width="{weight}" stroke-linejoin="miter" '
            f'stroke-miterlimit="2">{paths}</g>')


def claw(uid, x, y, size, ink, red, glow=True):
    tr = 2.4
    w = width(size, tr)
    letters = _paths(NAME, "wordmark", size, x, y, tr)
    top = y - size * 0.74
    rng = random.Random(4)
    # three parallel tears, each a tapered sliver
    cx = x + w * 0.63
    tears = []
    for k in range(3):
        ox = cx + (k - 1) * size * 0.30
        wob = rng.uniform(-3, 3)
        x1, y1 = ox + size * 0.34 + wob, top - size * 0.16
        x2, y2 = ox - size * 0.34, y + size * 0.16
        mx, my = (x1 + x2) / 2 + size * 0.05, (y1 + y2) / 2
        wd = size * (0.085 - 0.012 * abs(k - 1))
        tears.append(f"M{x1:.1f},{y1:.1f} Q{mx + wd:.1f},{my:.1f} {x2:.1f},{y2:.1f} Q{mx - wd:.1f},{my:.1f} {x1:.1f},{y1:.1f}Z")
    tear_d = " ".join(tears)
    skew = f"translate({y * 0.16:.1f} 0) skewX(-9)"
    defs = (f'<mask id="{uid}m" maskUnits="userSpaceOnUse" x="{x - 40}" y="{top - 60}" width="{w + 120}" height="{size * 2}">'
            f'<rect x="{x - 40}" y="{top - 60}" width="{w + 120}" height="{size * 2}" fill="#fff"/>'
            f'<path d="{tear_d}" fill="#000"/></mask>'
            f'<filter id="{uid}g" x="-10%" y="-40%" width="120%" height="180%"><feGaussianBlur stdDeviation="5" result="b"/>'
            f'<feMerge><feMergeNode in="b"/><feMergeNode in="SourceGraphic"/></feMerge></filter>')
    body = (f'<g transform="{skew}">'
            f'<g opacity="0.55" transform="translate(4 3)">{_bold(letters, red, 2.6)}</g>'
            f'<g mask="url(#{uid}m)">{_bold(letters, ink, 2.6)}</g>'
            f'<path d="{tear_d}" fill="{red}"{f" filter=\"url(#{uid}g)\"" if glow else ""} opacity="0.95">'
            f'<animate attributeName="opacity" values="0.95;0.5;0.95" dur="2.4s" repeatCount="indefinite"/></path></g>')
    return defs, body


def hive(uid, x, y, size, ink, red, cell=None, start=0.2):
    """The name grown as a colony of hexagonal cells.

    Cells bud outward from a few inoculation sites (each cell scales up when the
    colony front reaches it), a red infection wave sweeps the colony every few
    seconds, and a handful of cells stay infected and pulse.
    """
    from PIL import Image, ImageDraw, ImageFont
    from notebook import FACES, FONTS
    tr = 2.0
    scale = 4
    f = ImageFont.truetype(str(FONTS / FACES["wordmark"]), size * scale)
    w = int(width(size, tr) * scale) + 40
    h = int(size * 1.3 * scale)
    img = Image.new("L", (w, h), 0)
    d = ImageDraw.Draw(img)
    base = int(size * 1.05 * scale)
    cx = 0
    for ch in NAME:
        d.text((cx, base), ch, font=f, fill=255, anchor="ls")
        cx += f.getlength(ch) + tr * scale
    cell = cell or size / 8.6
    hy = cell * math.sqrt(3) / 2
    r = cell * 0.5
    rng = random.Random(11)
    cells = []
    j = 0
    while j * hy * scale < h:
        i = 0
        while i * cell * scale < w:
            px = i * cell + (cell / 2 if j % 2 else 0)
            py = j * hy
            sx, sy = int(px * scale), int(py * scale)
            if sx < w and sy < h and img.getpixel((sx, sy)) > 120:
                cells.append((x + px, y - base / scale + py))
            i += 1
        j += 1
    if not cells:
        return "", ""
    xs = [c[0] for c in cells]
    x0, x1 = min(xs), max(xs)
    seeds = [cells[int(k * (len(cells) - 1) / 4)] for k in range(5)]
    speed = 260.0   # px per second
    hexpts = " ".join(f"{r * math.cos(math.radians(60 * k + 30)):.2f},{r * math.sin(math.radians(60 * k + 30)):.2f}"
                      for k in range(6))
    grow, sick = [], []
    for (X, Y) in cells:
        dist = min(math.dist((X, Y), s) for s in seeds)
        t0 = start + dist / speed + rng.uniform(0, 0.08)
        g = (f'<g transform="translate({X:.1f} {Y:.1f})"><use href="#{uid}h" xlink:href="#{uid}h" transform="scale(0)">'
             f'<animateTransform attributeName="transform" type="scale" values="0;1.25;1" dur="0.35s" begin="{t0:.2f}s" fill="freeze"/>'
             f'</use></g>')
        if rng.random() < 0.06:
            sick.append(g.replace("<use ", f'<use fill="{red}" ', 1).replace(
                "</use>", f'<animate attributeName="opacity" values="1;0.2;1" dur="{rng.uniform(1.1, 2.4):.1f}s" '
                          f'begin="{t0 + 0.4:.2f}s" repeatCount="indefinite"/></use>', 1))
        else:
            grow.append(g)
    span = x1 - x0 + 200
    wave_begin = start + max(math.dist(c, s) for c in cells for s in seeds[:1]) / speed + 0.4
    defs = (f'<polygon id="{uid}h" points="{hexpts}"/>'
            f'<g id="{uid}c">{"".join(grow)}</g>'
            f'<linearGradient id="{uid}w" gradientUnits="userSpaceOnUse" x1="{x0 - 200:.0f}" y1="0" x2="{x0:.0f}" y2="0">'
            f'<stop offset="0" stop-color="{red}" stop-opacity="0"/><stop offset="0.75" stop-color="{red}" stop-opacity="1"/>'
            f'<stop offset="1" stop-color="{red}" stop-opacity="0"/>'
            f'<animateTransform attributeName="gradientTransform" type="translate" values="0 0;{span:.0f} 0;{span:.0f} 0" '
            f'keyTimes="0;0.45;1" dur="5s" begin="{wave_begin:.2f}s" repeatCount="indefinite"/></linearGradient>'
            f'<filter id="{uid}g" x="-5%" y="-30%" width="110%" height="160%"><feGaussianBlur stdDeviation="2.2" result="b"/>'
            f'<feMerge><feMergeNode in="b"/><feMergeNode in="SourceGraphic"/></feMerge></filter>')
    body = (f'<use href="#{uid}c" xlink:href="#{uid}c" fill="{red}" opacity="0.35" transform="translate(2.5 2)"/>'
            f'<use href="#{uid}c" xlink:href="#{uid}c" fill="{ink}"/>'
            f'<use href="#{uid}c" xlink:href="#{uid}c" fill="url(#{uid}w)" filter="url(#{uid}g)"/>'
            f'<g filter="url(#{uid}g)">{"".join(sick)}</g>')
    return defs, body


def stencil(uid, x, y, size, ink, red):
    tr = 4.0
    w = width(size, tr)
    letters = _paths(NAME, "wordmark", size, x, y, tr)
    top = y - size * 0.74
    bridges = []
    xx = x
    for ch in NAME:
        _, adv = _glyph(ch, "wordmark", size)
        if ch != " ":
            for fx in ((0.5,) if ch not in "MW" else (0.33, 0.66)):
                bx = xx + adv * fx
                bridges.append(f'<rect x="{bx - size * 0.035:.1f}" y="{top - 4:.1f}" width="{size * 0.07:.1f}" height="{size * 0.84:.1f}"/>')
        xx += adv + tr
    defs = (f'<mask id="{uid}s" maskUnits="userSpaceOnUse" x="{x - 20}" y="{top - 30}" width="{w + 60}" height="{size * 1.4}">'
            f'<rect x="{x - 20}" y="{top - 30}" width="{w + 60}" height="{size * 1.4}" fill="#fff"/>'
            f'<g fill="#000">{"".join(bridges)}</g></mask>')
    spray = []
    rng = random.Random(5)
    for _ in range(140):
        spray.append(f'<circle cx="{rng.uniform(x, x + w):.1f}" cy="{rng.gauss(y - size * 0.35, size * 0.45):.1f}" r="{rng.uniform(0.4, 1.4):.1f}"/>')
    body = (f'<g fill="{ink}" opacity="0.5">{"".join(spray)}</g>'
            f'<g mask="url(#{uid}s)">{_bold(letters, ink, 3.2)}</g>')
    return defs, body


def breach(uid, x, y, size, ink, red):
    tr = 2.4
    w = width(size, tr)
    letters = _paths(NAME, "wordmark", size, x, y, tr)
    top = y - size * 0.74
    defs = (f'<clipPath id="{uid}a"><rect x="{x - 30}" y="{top - 10:.1f}" width="{w + 60}" height="{size * 0.30:.1f}"/></clipPath>'
            f'<clipPath id="{uid}b"><rect x="{x - 30}" y="{top + size * 0.30:.1f}" width="{w + 60}" height="{size * 0.14:.1f}"/></clipPath>'
            f'<clipPath id="{uid}c"><rect x="{x - 30}" y="{top + size * 0.44:.1f}" width="{w + 60}" height="{size * 0.6:.1f}"/></clipPath>')
    b = _bold(letters, ink, 2.8)
    body = (f'<g opacity="0.8" transform="translate(-4 0)">{_bold(letters, "#00e5ff", 2.8)}</g>'
            f'<g opacity="0.85" transform="translate(4 0)">{_bold(letters, red, 2.8)}</g>'
            f'<g clip-path="url(#{uid}a)">{b}</g>'
            f'<g clip-path="url(#{uid}b)" transform="translate(14 0)">{b}'
            f'<animateTransform attributeName="transform" type="translate" values="14 0;-10 0;22 0;14 0" dur="2.2s" calcMode="discrete" repeatCount="indefinite"/></g>'
            f'<g clip-path="url(#{uid}c)">{b}</g>')
    return defs, body


STYLES = {"claw": claw, "hive": hive, "stencil": stencil, "breach": breach}
