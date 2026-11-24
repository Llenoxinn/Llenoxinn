"""The RTS command-console kit: iron plates, gold trim, chrome lettering, orbs and slot bars.

Every picture on the profile is a piece of one original strategy-game HUD, drawn in
vector: riveted gunmetal plates with a bevelled rim, gold-orange trim, chrome title
lettering, glass orbs and recessed resource slots. Gradients live in defs() and are
referenced by id, so call defs() once per document.
"""
import base64
from pathlib import Path

from notebook import ROOT, Typesetter, text_width

W, HALF = 828, 412          # GitHub's README column: one full piece, or two halves with a gap
LOGOS = ROOT / "lab" / "data" / "logos"
INK = dict(text="#f3ead6", soft="#c9d0d8", muted="#9aa3ad", dim="#6d7781", gold="#ffcf6a", amber="#e8891f",
           sky="#7fdcff", green="#7fe0a0", blue="#9ad0ff", violet="#c58cff", page_dark="#0d1117")


def _lin(id_, stops, x2=0, y2=1):
    s = "".join(f'<stop offset="{o}" stop-color="{c}"{f" stop-opacity={chr(34)}{a}{chr(34)}" if a != 1 else ""}/>'
                for o, c, a in stops)
    return f'<linearGradient id="{id_}" x1="0" y1="0" x2="{x2}" y2="{y2}">{s}</linearGradient>'


def defs():
    """Shared paints: iron plate, rim, gold trim, chrome, orange title, slot well, lit and unlit orbs."""
    return ("<defs>"
            + _lin("iron", [(0, "#45484d", 1), (.25, "#26282c", 1), (1, "#121315", 1)])
            + _lin("rim", [(0, "#9aa0a8", 1), (.5, "#3b3e43", 1), (1, "#15171a", 1)])
            + _lin("gold", [(0, "#ffe08a", 1), (.5, "#e8891f", 1), (1, "#8a4208", 1)])
            + _lin("goldh", [(0, "#ffe08a", 1), (.5, "#e8891f", 1), (1, "#8a4208", 1)], 1, 0)
            + _lin("chrome", [(0, "#ffffff", 1), (.42, "#e3e8ee", 1), (.5, "#5d6672", 1), (.62, "#cfd6de", 1),
                              (1, "#7f8994", 1)])
            + _lin("orange", [(0, "#ffe08a", 1), (.55, "#ff8f2a", 1), (1, "#b3400c", 1)])
            + _lin("well", [(0, "#0c0d10", 1), (1, "#1d1f24", 1)])
            + _lin("steel", [(0, "#5a5f66", 1), (.5, "#2a2e34", 1), (1, "#15181c", 1)])
            + '<radialGradient id="orbon"><stop offset="0" stop-color="#fff"/><stop offset=".6" stop-color="#ffd36b"/>'
              '<stop offset="1" stop-color="#b8650f"/></radialGradient>'
            + '<radialGradient id="socket"><stop offset="0" stop-color="#3a3d42"/><stop offset="1" stop-color="#0b0c0e"/></radialGradient>'
            + '<pattern id="plate" width="22" height="22" patternUnits="userSpaceOnUse">'
              '<path d="M0 11h22M11 0v22" stroke="#000" stroke-opacity=".22"/><circle cx="2" cy="2" r="1" fill="#6a6e74"/></pattern>'
            + "</defs>")


def plaque(x, y, w, h, r=4, pattern=False):
    """A riveted gunmetal plate with a bevelled rim and a hard drop shadow."""
    out = [f'<rect x="{x + 2}" y="{y + 4}" width="{w - 2}" height="{h - 2}" rx="{r}" fill="#000" opacity=".55"/>',
           f'<rect x="{x + 1}" y="{y + 1}" width="{w - 3}" height="{h - 5}" rx="{r}" fill="url(#iron)" stroke="url(#rim)" stroke-width="2"/>']
    if pattern:
        out.append(f'<rect x="{x + 2}" y="{y + 2}" width="{w - 5}" height="{h - 7}" rx="{r}" fill="url(#plate)"/>')
    out.append(f'<rect x="{x + 6}" y="{y + 3}" width="{w - 14}" height="1" fill="#fff" opacity=".12"/>')
    for rx, ry in ((x + 8, y + 8), (x + w - 10, y + 8), (x + 8, y + h - 10), (x + w - 10, y + h - 10)):
        out.append(f'<circle cx="{rx}" cy="{ry}" r="2.2" fill="#8d939b" stroke="#2a2c30" stroke-width=".8"/>')
    return "".join(out)


def well(x, y, w, h, r=2):
    return (f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="{r}" fill="url(#well)" stroke="#5d6168" stroke-width="1.2"/>'
            f'<rect x="{x + 1}" y="{y + 1}" width="{w - 2}" height="2" fill="#000" opacity=".5"/>')


def text(ts, s, face, size, x, y, fill, anchor="start", track=0.0, stroke=None):
    """Glyph-path text; fill may be a colour or a gradient url. stroke=(colour, width) outlines it."""
    g, _ = ts.text(s, face, size, x, y, fill, anchor=anchor, tracking=track * size)
    if stroke:
        col, sw = stroke
        outline, _ = ts.text(s, face, size, x, y, "none", anchor=anchor, tracking=track * size,
                             attrs=f' stroke="{col}" stroke-width="{sw}" stroke-linejoin="round"')
        return outline + g
    return g


def bar(ts, x, y, w, frac, colour, label, value, start=None):
    """A recessed resource slot that fills to `frac`; animated, it fills in steps from empty."""
    fw = max(2.0, (w - 4) * min(1.0, frac))
    fill = (f'<rect x="{x + 2}" y="{y + 2}" width="{fw:.1f}" height="12" fill="{colour}" opacity=".85">'
            + (f'<animate attributeName="width" values="0;{fw * .35:.1f};{fw * .7:.1f};{fw * .9:.1f};{fw:.1f}" '
               f'keyTimes="0;.25;.5;.75;1" calcMode="discrete" dur="0.6s" begin="{start}s" fill="freeze"/>'
               if start is not None else "") + "</rect>"
            f'<rect x="{x + 2}" y="{y + 2}" width="{fw:.1f}" height="4" fill="#fff" opacity=".18"/>')
    return (well(x, y, w, 16) + fill
            + text(ts, label.upper(), "bold", 11, x, y - 5, INK["muted"], track=.12)
            + text(ts, value, "num", 18, x + w, y - 3, INK["text"], anchor="end"))


def logo(key, x, y, size, r=None):
    """A project's own logo (lab/data/logos), embedded as a data URI and clipped to a rounded square."""
    for ext, mime in (("svg", "image/svg+xml"), ("png", "image/png")):
        p = LOGOS / f"{key}.{ext}"
        if p.exists():
            data = base64.b64encode(p.read_bytes()).decode()
            r = size * .22 if r is None else r
            cid = f"lg{key}{int(x)}{int(y)}"
            return (f'<clipPath id="{cid}"><rect x="{x}" y="{y}" width="{size}" height="{size}" rx="{r:.1f}"/></clipPath>'
                    + (f'<rect x="{x}" y="{y}" width="{size}" height="{size}" rx="{r:.1f}" fill="#fff"/>' if ext == "png" else "")
                    + f'<image clip-path="url(#{cid})" x="{x}" y="{y}" width="{size}" height="{size}" '
                      f'preserveAspectRatio="xMidYMid meet" href="data:{mime};base64,{data}"/>')
    return ""


def orb(cx, cy, d, inner):
    """A gold-rimmed ability socket with something inside it."""
    return (f'<circle cx="{cx}" cy="{cy}" r="{d / 2 + 3}" fill="url(#gold)"/>'
            f'<circle cx="{cx}" cy="{cy}" r="{d / 2}" fill="url(#socket)"/>' + inner)


def banner(ts, title, w=W, meta=None):
    """A section banner: a gold double rule broken by an iron cartouche with the title."""
    cw = text_width(title.upper(), "head", 17, 17 * .16) + 70
    cx = w / 2
    a, b = cx - cw / 2, cx + cw / 2
    out = [f'<path d="M0 24H{a - 14}l14-14H{b}l14 14H{w}" stroke="url(#goldh)" stroke-width="2" fill="none"/>',
           f'<path d="M0 28H{a - 14}l14 14H{b}l14-14H{w}" stroke="#8a4208" stroke-width="1" fill="none"/>',
           f'<path d="M{a} 10H{b}l14 14-14 14H{a}l-14-14z" fill="#16171a" stroke="#ffcf6a" stroke-width="1.5"/>',
           text(ts, title.upper(), "head", 17, cx, 31, "url(#orange)", anchor="middle", track=.16)]
    if meta:
        out.append(text(ts, meta.upper(), "bold", 11, w, 8, INK["dim"], anchor="end", track=.12))
    return "".join(out)


def glint(x, y, w, h, period=5.0, begin=1.0):
    """A diagonal light that sweeps across now and then (chrome titles, gold buttons)."""
    return (f'<g opacity="0"><animate attributeName="opacity" values="0;1;0" keyTimes="0;.001;.16" calcMode="discrete" '
            f'dur="{period}s" begin="{begin}s" repeatCount="indefinite"/>'
            f'<rect x="{x}" y="{y}" width="26" height="{h}" fill="#fff" opacity=".3" transform="skewX(-20)">'
            f'<animate attributeName="x" values="{x - 40};{x + w + h};{x + w + h}" keyTimes="0;.16;1" '
            f'dur="{period}s" begin="{begin}s" repeatCount="indefinite"/></rect></g>')
