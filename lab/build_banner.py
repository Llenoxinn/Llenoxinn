#!/usr/bin/env python3
"""Build the hero title screen, the commander console and the contact command keys.

The hero is drawn, not painted: a night tactical map (grid, contour lines, a coastline,
radar rings with a sweeping beam) behind chrome LLENOXINN lettering, a gold
DEXTER JUEVESANO plate and the portfolio button. The console under it is the RTS
command bar: service record on the left, win orbs and the emblem in the middle, every
project as an ability socket with its own logo, and the commander card on the right.
"""
import math
import random

from notebook import ASSETS, THEMES, Typesetter, mark, svg_doc, write_pair
from rts import HALF, INK, W, bar, defs, glint, logo, orb, plaque, text, well

TITLE, NAME = "LLENOXINN", "DEXTER JUEVESANO"
TAG = "/dev/dexter"
WHO = "Computer science at UP Cebu. I build web apps, 3D visualizers and CTF tools."
BUTTON = "ENTER THE PORTFOLIO"


def tactical_map(w, h, cx, cy, seed, animate):
    """The night map behind the title: grid, contours, a coastline, radar rings and a sweep."""
    rng = random.Random(seed)
    out = [f'<rect width="{w}" height="{h}" fill="#070b12"/>',
           f'<radialGradient id="haze" cx=".5" cy=".62" r=".7"><stop offset="0" stop-color="#16324d"/>'
           f'<stop offset="1" stop-color="#070b12" stop-opacity="0"/></radialGradient>',
           f'<rect width="{w}" height="{h}" fill="url(#haze)"/>']
    grid = "".join(f"M{x} 0V{h}" for x in range(0, w, 36)) + "".join(f"M0 {y}H{w}" for y in range(0, h, 36))
    out.append(f'<path d="{grid}" stroke="#24507a" stroke-width="1" opacity=".6"/>')
    for k in range(7):                       # contour lines across the map
        y0 = h * (.18 + k * .11)
        pts = " ".join(f"{x},{y0 + 9 * math.sin(x / 70 + k * 1.7) + 6 * math.sin(x / 23 + k):.1f}" for x in range(0, w + 20, 20))
        out.append(f'<polyline points="{pts}" fill="none" stroke="#3a76a6" stroke-width="1.2" opacity=".5"/>')
    coast = [f"0,{h}"]
    for x in range(0, w + 24, 24):
        coast.append(f"{x},{h - 46 - 20 * math.sin(x / 90) - rng.randint(0, 14)}")
    coast.append(f"{w},{h}")
    out.append(f'<polygon points="{" ".join(coast)}" fill="#0b1520" stroke="#2f6a91" stroke-width="1.5"/>')
    for r in (60, 120, 180, 240):
        out.append(f'<circle cx="{cx}" cy="{cy}" r="{r}" fill="none" stroke="#5aa6dd" stroke-width="1.2" opacity=".6" stroke-dasharray="3 5"/>')
    out.append(f'<path d="M{cx - 260} {cy}H{cx + 260}M{cx} {cy - 260}V{cy + 260}" stroke="#3d7fae" opacity=".3"/>')
    sweep = (f'<path d="M{cx} {cy}L{cx + 240} {cy}A240 240 0 0 0 {cx + 240 * math.cos(math.radians(-35)):.1f} '
             f'{cy + 240 * math.sin(math.radians(-35)):.1f}Z" fill="#7fdcff" opacity=".10"/>'
             f'<path d="M{cx} {cy}L{cx + 240} {cy}" stroke="#bfefff" stroke-width="1.5" opacity=".6"/>')
    if animate:
        sweep = (f'<g>{sweep}<animateTransform attributeName="transform" type="rotate" from="0 {cx} {cy}" '
                 f'to="-360 {cx} {cy}" dur="8s" repeatCount="indefinite"/></g>')
    out.append(sweep)
    for _ in range(9):                       # contacts on the map, a few of them friendly gold
        a, r = rng.uniform(0, 6.28), rng.uniform(70, 230)
        x, y = cx + r * math.cos(a), cy + r * math.sin(a) * .6
        col = "#ffcf6a" if rng.random() < .35 else "#7fdcff"
        blink = (f'<animate attributeName="opacity" values="1;.25;1" dur="{rng.uniform(1.6, 3.2):.1f}s" '
                 f'repeatCount="indefinite"/>' if animate else "")
        out.append(f'<rect x="{x - 2:.0f}" y="{y - 2:.0f}" width="4" height="4" fill="{col}">{blink}</rect>')
    out.append(f'<rect width="{w}" height="{h}" fill="#05070b" opacity=".12"/>')
    return "".join(out)


def filigree(w):
    """Iron scrollwork across the top edge with a crest in the middle."""
    c = w / 2
    return (f'<g fill="none" stroke="url(#gold)" stroke-width="2" stroke-linecap="round">'
            f'<path d="M{c - 70} 8q-40 -4 -70 10q-30 14 -70 6"/><path d="M{c + 70} 8q40 -4 70 10q30 14 70 6"/>'
            f'<path d="M{c - 30} 4q30 -10 60 0"/></g>'
            f'<path d="M{c} -4l12 16 -12 10 -12 -10z" fill="#1d1f24" stroke="#ffcf6a" stroke-width="1.5"/>')


def hero(theme, animate=True, layout="wide"):
    wide = layout == "wide"
    w, h = (W, 360) if wide else (400, 400)
    ts = Typesetter("hr")
    body = [defs(), f'<clipPath id="hclip"><rect width="{w}" height="{h}" rx="6"/></clipPath><g clip-path="url(#hclip)">',
            tactical_map(w, h, w / 2, h * (.6 if wide else .58), "map", animate),
            f'<rect width="{w}" height="{h}" fill="url(#vig)"/></g>',
            f'<radialGradient id="vig" cx=".5" cy=".5" r=".75"><stop offset=".55" stop-color="#000" stop-opacity="0"/>'
            f'<stop offset="1" stop-color="#000" stop-opacity=".75"/></radialGradient>',
            f'<rect x="1" y="1" width="{w - 2}" height="{h - 2}" rx="6" fill="none" stroke="url(#gold)" stroke-width="2"/>',
            filigree(w)]
    cx = w / 2
    ty = 30 if wide else 32
    tw = 150 if wide else 140
    body.append(f'<rect x="{cx - tw / 2}" y="{ty}" width="{tw}" height="26" rx="2" fill="url(#steel)" stroke="url(#gold)" stroke-width="1.5"/>'
                + text(ts, TAG, "semi", 16, cx, ty + 19, INK["gold"], anchor="middle", track=.04))
    if wide:
        body.append(f'<rect x="60" y="{ty + 12}" width="{cx - tw / 2 - 72}" height="2" fill="url(#goldh)" opacity=".8"/>'
                    f'<rect x="{cx + tw / 2 + 12}" y="{ty + 12}" width="{cx - tw / 2 - 72}" height="2" fill="url(#goldh)" opacity=".8"/>')
    size, base = (104, 168) if wide else (60, 140)
    body.append(text(ts, TITLE, "title", size, cx, base + 5, "#e8891f", anchor="middle", stroke=("#e8891f", 4)))
    body.append(text(ts, TITLE, "title", size, cx, base, "url(#chrome)", anchor="middle", stroke=("#0d1015", 5)))
    if animate:
        body.append(f'<clipPath id="tclip"><rect x="0" y="{base - size * .8}" width="{w}" height="{size * .85}"/></clipPath>'
                    f'<g clip-path="url(#tclip)">{glint(40, base - size * .8, w - 80, size * .85, 6.0, 1.4)}</g>')
    nsize, ny = (24, 210) if wide else (17, 178)
    body.append(text(ts, NAME, "head", nsize, cx, ny, "url(#orange)", anchor="middle", track=.3, stroke=("#1a0b03", 2)))
    body.append(f'<rect x="{cx - (170 if wide else 140)}" y="{ny + 12}" width="{340 if wide else 280}" height="2" fill="url(#goldh)"/>')
    lines = [WHO] if wide else ["Computer science at UP Cebu.", "I build web apps, 3D visualizers and CTF tools."]
    for i, line in enumerate(lines):
        ly = ny + 40 + i * 22
        body.append(f'<rect x="{cx - 290 if wide else 20}" y="{ly - 17}" width="{580 if wide else 360}" height="24" fill="#05070b" opacity=".7"/>'
                    + text(ts, line, "semi", 17 if wide else 15.5, cx, ly, "#e8eef5", anchor="middle"))
    bw, bh = 250, 44
    by = h - 74 if wide else h - 70
    body.append(f'<rect x="{cx - bw / 2 + 2}" y="{by + 4}" width="{bw}" height="{bh}" rx="3" fill="#000" opacity=".6"/>'
                f'<rect x="{cx - bw / 2}" y="{by}" width="{bw}" height="{bh}" rx="3" fill="url(#orange)" stroke="#fff2c4" stroke-width="1.5"/>'
                + text(ts, BUTTON, "head", 15, cx - 14, by + 28, "#1c1005", anchor="middle", track=.1)
                + f'<path d="M{cx + bw / 2 - 22} {by + 15}l10 7-10 7z" fill="#1c1005"/>')
    if animate:
        body.append(f'<clipPath id="bclip"><rect x="{cx - bw / 2}" y="{by}" width="{bw}" height="{bh}" rx="3"/></clipPath>'
                    f'<g clip-path="url(#bclip)">{glint(cx - bw / 2, by, bw, bh, 4.0, 2.4)}</g>')
    return svg_doc(w, h, ts.defs_svg() + "".join(body), f"{TITLE}: {NAME}. {WHO} Enter the portfolio.")


# ---------------------------------------------------------------- the commander console

def console(theme, animate=True, layout="wide"):
    from build_headers import WINS
    from build_projects import PROJECTS
    from build_shelf import SHELF
    wide = layout == "wide"
    ts = Typesetter("cn")
    tools = sum(len(t) for _, t in SHELF)
    record = [("Units deployed", str(len(PROJECTS))), ("Medals earned", str(len(WINS))),
              ("Structures", str(tools)), ("In the field since", "APR 2026")]
    champs = sum(1 for w in WINS if w["title"].startswith("Champion"))
    if wide:
        w, h = W, 236
        crown = (f'<path d="M0 58Q60 54 96 34L150 34Q190 10 250 26L330 26Q370 4 {w / 2} 4Q{w - 370} 4 {w - 330} 26'
                 f'L{w - 250} 26Q{w - 190} 10 {w - 150} 34L{w - 96} 34Q{w - 60} 54 {w} 58V{h - 4}H0Z" ')
        body = [defs(), '<path transform="translate(2 4)" opacity=".55" fill="#000" ' + crown[5:] + '/>',
                crown + 'fill="url(#iron)" stroke="url(#rim)" stroke-width="3"/>',
                crown + 'fill="url(#plate)"/>',
                f'<g fill="#55595f">{"".join(f"<circle cx={chr(34)}{14 + i * 40}{chr(34)} cy={chr(34)}{h - 12}{chr(34)} r={chr(34)}2.5{chr(34)}/>" for i in range(21))}</g>']
        # service record
        for i, (k, v) in enumerate(record):
            y = 70 + i * 40
            body.append(well(18, y, 214, 28) + f'<rect x="18" y="{y}" width="4" height="28" fill="url(#gold)"/>'
                        + text(ts, k.upper(), "bold", 11, 30, y + 18, INK["muted"], track=.14)
                        + text(ts, v, "num", 22, 224, y + 21, INK["text"], anchor="end"))
        # win orbs: one lit per real result
        for i in range(10):
            lit = i < len(WINS)
            cx = 262 + i * 17
            delay = f'<animate attributeName="opacity" values="0;1" keyTimes="0;1" calcMode="discrete" dur="{0.5 + i * .25:.2f}s" fill="freeze"/>' if animate and lit else ""
            body.append(f'<circle cx="{cx}" cy="50" r="6" fill="url(#socket)" stroke="#70747b"/>'
                        + (f'<circle cx="{cx}" cy="50" r="6" fill="url(#orbon)" stroke="#ffe6a6">{delay}</circle>' if lit else ""))
        body.append(text(ts, f"{len(WINS)} WINS", "bold", 11, 256, 36, INK["gold"], track=.14))
        # emblem: an atom over the socket, the commander below
        body.append(orb(w / 2, 100, 64, '<g fill="none" stroke="#ffcf6a" stroke-width="2">'
                                          + "".join(f'<ellipse cx="{w / 2}" cy="100" rx="22" ry="8" transform="rotate({a} {w / 2} 100)"/>' for a in (0, 60, 120))
                                          + f'</g><circle cx="{w / 2}" cy="100" r="5" fill="#ff9a2e"/>'))
        body.append(f'<circle cx="{w / 2}" cy="186" r="44" fill="url(#socket)" stroke="#5d6168" stroke-width="2"/>'
                    + text(ts, "CMDR", "bold", 11, w / 2, 178, INK["gold"], anchor="middle", track=.3)
                    + text(ts, "LLENOXINN", "head", 13, w / 2, 197, INK["text"], anchor="middle"))
        # ability sockets: every project, with its own logo where it has one
        spots = [(262, 104), (312, 104), (262, 156), (312, 156), (528, 104), (578, 104), (528, 156), (578, 156), (628, 130)]
        for (x, y), p in zip(spots, PROJECTS):
            body.append(orb(x, y, 40, logo(p["logo"], x - 14, y - 14, 28) if p.get("logo") else glyph(p["art"], x, y)))
        # commander card
        cx0 = w - 164
        body.append(f'<rect x="{cx0}" y="52" width="148" height="170" rx="3" fill="#121418" stroke="url(#gold)" stroke-width="3"/>'
                    + text(ts, "COMMANDER", "bold", 11, cx0 + 12, 72, INK["gold"], track=.16)
                    + text(ts, "Dexter Juevesano", "head", 14, cx0 + 12, 94, INK["text"])
                    + text(ts, "Computer science", "body", 13, cx0 + 12, 114, INK["soft"])
                    + text(ts, "student at UP Cebu", "body", 13, cx0 + 12, 130, INK["soft"])
                    + f'<rect x="{cx0 + 12}" y="142" width="124" height="1" fill="#ffcf6a" opacity=".4"/>'
                    + text(ts, f"{champs}X CHAMPION", "bold", 12, cx0 + 12, 162, "#ffe08a", track=.1)
                    + text(ts, "TOP 2, HACKFORGOV5", "bold", 12, cx0 + 12, 180, INK["soft"], track=.06)
                    + text(ts, TAG, "semi", 14, cx0 + 12, 206, INK["sky"]))
    else:
        w, h = 400, 300
        body = [defs(), plaque(0, 0, w, h, pattern=True)]
        for i, (k, v) in enumerate(record):
            x, y = 16 + (i % 2) * 188, 20 + (i // 2) * 38
            body.append(well(x, y, 180, 28) + f'<rect x="{x}" y="{y}" width="4" height="28" fill="url(#gold)"/>'
                        + text(ts, k.upper(), "bold", 10, x + 12, y + 18, INK["muted"], track=.1)
                        + text(ts, v, "num", 20, x + 172, y + 21, INK["text"], anchor="end"))
        for i, p in enumerate(PROJECTS):
            x, y = 40 + (i % 5) * 80, 128 + (i // 5) * 58
            body.append(orb(x, y, 40, logo(p["logo"], x - 14, y - 14, 28) if p.get("logo") else glyph(p["art"], x, y)))
        body.append(text(ts, f"{champs}X CHAMPION   TOP 2, HACKFORGOV5", "bold", 12, w / 2, 262, "#ffe08a", anchor="middle", track=.1)
                    + text(ts, "CMDR LLENOXINN", "head", 13, w / 2, 282, INK["text"], anchor="middle"))
    return svg_doc(w, h, ts.defs_svg() + "".join(body),
                   f"Commander Llenoxinn: {len(PROJECTS)} projects, {len(WINS)} wins, {tools} tools, on GitHub since April 2026.")


GLYPHS = {   # original line glyphs for projects without a logo of their own
    "helix": '<path d="M-10 -12c14 6 6 10 20 14s-20 8-6 14" stroke="#fff" stroke-width="2.4" fill="none"/>'
             '<path d="M10 -12c-14 6-6 10-20 14s20 8 6 14" stroke="#fff" stroke-width="1.4" fill="none" opacity=".7"/>',
    "orbit": '<circle r="5" fill="#fff"/><circle r="11" stroke="#fff" stroke-width="2" fill="none" stroke-dasharray="4 3"/>'
             '<circle cx="9" cy="-7" r="2.6" fill="#fff"/>',
}


def glyph(key, x, y):
    return f'<g transform="translate({x} {y})">{GLYPHS.get(key, "")}</g>'


# ---------------------------------------------------------------- contact command keys

CONTACTS = [("linkedin", "Recruit on LinkedIn", "linkedin.com/in/dsjuevesano"),
            ("github", "Follow on GitHub", "github.com/Llenoxinn")]
CONTACT_W, CONTACT_H = HALF, 80


def contact(key, label, url, theme):
    ts = Typesetter("ct")
    body = [defs(), plaque(0, 0, CONTACT_W, CONTACT_H),
            '<rect x="14" y="12" width="54" height="54" rx="4" fill="url(#orange)" stroke="#fff2c4" stroke-width="1"/>',
            mark(key, 27, 25, 28, "#1c1305"),
            text(ts, label.upper(), "head", 15, 84, 36, INK["text"], track=.06),
            text(ts, url, "body", 14, 84, 58, INK["muted"]),
            f'<path d="M{CONTACT_W - 34} 30l12 9-12 9z" fill="url(#orange)" stroke="#ffe08a"/>']
    return svg_doc(CONTACT_W, CONTACT_H, ts.defs_svg() + "".join(body), f"{label}: {url}")


if __name__ == "__main__":
    for old in ASSETS.glob("banner*.svg"):
        old.unlink()
    write_pair(ASSETS, "banner", lambda t, a: hero(t, a, "wide"))
    write_pair(ASSETS, "banner-narrow", lambda t, a: hero(t, a, "narrow"))
    write_pair(ASSETS, "console", lambda t, a: console(t, a, "wide"))
    write_pair(ASSETS, "console-narrow", lambda t, a: console(t, a, "narrow"))
    for old in ASSETS.glob("contact-*.svg"):
        old.unlink()
    for theme in THEMES:
        for key, label, url in CONTACTS:
            (ASSETS / f"contact-{key}-{theme}.svg").write_text(contact(key, label, url, theme), encoding="utf-8")
    print("wrote the hero, the console and the contact keys")
