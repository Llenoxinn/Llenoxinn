#!/usr/bin/env python3
"""Draw one card per project and fill the README's PROJECTS block.

Each card has an original pixel icon of what the project does, two short lines
and an ink terminal strip that types the stack. Cards are separate images, two
to a row on wide screens and one on phones. Private repositories are labelled
rather than linked to a page that would 404.

    python lab/build_projects.py
"""
import math

from notebook import (ASSETS, BRAND, SHEET, STRIP, Typesetter, card, fade, replace_block, strip, svg_doc,
                      text_width, themed)

GITHUB = "https://github.com/Llenoxinn"
PROJECTS = [
    dict(name="Sylvi", repo=None, art="sylvi",
         line="ID photo sheets, printed true to size.", detail="1×1, 2×2, passport · PDF, PNG, JPG",
         stack=[("ts", "TypeScript"), ("js", "JavaScript"), ("react", "React"), ("vite", "Vite"),
                ("plpgsql", "PL/pgSQL"), ("html", "HTML"), ("css", "CSS")]),
    dict(name="Olatz-Tol", repo="Olatz-Tol-", art="collatz",
         line="Pick a number. Watch it fall to 1.", detail="The Collatz 3n + 1 rule, drawn",
         stack=[("react", "React"), ("vite", "Vite"), ("tailwind", "Tailwind CSS"), ("zustand", "Zustand"),
                ("lucide", "Lucide")]),
    dict(name="Protein Structure Viewer Lite", repo="Protein-Structure-Viewer-Lite-", art="helix",
         line="Proteins in 3D, on raw Three.js.", detail="No NGL, Mol* or 3Dmol.js inside",
         stack=[("react", "React"), ("vite", "Vite"), ("three", "Three.js"), ("r3f", "React Three Fiber"),
                ("drei", "Drei"), ("tailwind", "Tailwind CSS")]),
    dict(name="viscal", repo="viscal", art="lissajous",
         line="Generative art from pure math.", detail="Lissajous · L-systems · Gray–Scott",
         stack=[("react", "React"), ("vite", "Vite"), ("tailwind", "Tailwind CSS")]),
    dict(name="PhyTree", repo=None, art="tree",
         line="Trees of life, built step by step.", detail="Alignment · UPGMA · Neighbor-Joining",
         stack=[("ts", "TypeScript"), ("react", "React"), ("vite", "Vite"), ("tailwind", "Tailwind CSS"),
                ("d3", "D3.js"), ("zustand", "Zustand")]),
]
CARD_W, CARD_H = 376, 106
GRID, PIXEL = 20, 2.8             # a 20 × 20 pixel drawing in a 56 px ink square


# ------------------------------------------------------------------ pixel drawings

def raster_line(cells, a, b, value):
    (x0, y0), (x1, y1) = a, b
    steps = max(abs(x1 - x0), abs(y1 - y0), 1)
    for i in range(steps + 1):
        cells[(round(x0 + (x1 - x0) * i / steps), round(y0 + (y1 - y0) * i / steps))] = value


def art_sylvi():
    cells = {}
    for x in range(2, 18):
        for y in range(2, 18):
            cells[(x, y)] = "P"
    person = ["LLLLLL", "LLDDLL", "LDDDDL", "LLDDLL", "LDDDDL", "DDDDDD"]
    for ox, oy in ((3, 3), (11, 3), (3, 11), (11, 11)):
        for r, row in enumerate(person):
            for c, v in enumerate(row):
                cells[(ox + c, oy + r)] = v
    for x, y in ((9, 0), (10, 0), (9, 19), (10, 19), (0, 9), (0, 10), (19, 9), (19, 10)):
        cells[(x, y)] = "N"           # crop marks on the cut lines
    return cells


def art_collatz():
    seq = [6]
    while seq[-1] != 1:
        seq.append(seq[-1] // 2 if seq[-1] % 2 == 0 else 3 * seq[-1] + 1)
    peak = max(seq)
    pts = [(round(1 + 17 * i / (len(seq) - 1)), round(18 - 16 * (v - 1) / (peak - 1))) for i, v in enumerate(seq)]
    cells = {}
    for a, b in zip(pts, pts[1:]):
        raster_line(cells, a, b, "N")
    for x, y in pts[:-1]:
        cells[(x, y)] = "P"
    x, y = pts[-1]
    for dx in (-1, 0, 1):
        for dy in (-1, 0, 1):
            cells[(min(19, x + dx), min(19, y + dy))] = "L"
    cells[(x, y)] = "P"
    return cells


def art_helix():
    """A cartoon alpha helix: a coil seen from the side, its far half in shadow."""
    back, front = {}, {}
    for i in range(900):
        u = i / 899
        a = 2 * math.pi * 2.5 * u
        x, y = 2.5 + 15 * u + 1.8 * math.cos(a), 10 + 6.5 * math.sin(a) - 3 * (u - 0.5)
        layer = front if math.cos(a) < 0 else back
        layer[(round(x), round(y))] = "P"
        if layer is front:
            layer[(round(x) + 1, round(y))] = "L"
    return {**{k: "N" for k in back}, **front}


def art_lissajous():
    cells = {}
    for i in range(600):
        s = 2 * math.pi * i / 600
        cells[(round(9.5 + 8.5 * math.sin(3 * s + math.pi / 2)), round(9.5 + 8.5 * math.sin(2 * s)))] = "N"
    for x, y in ((9, 9), (10, 10), (9, 10), (10, 9)):
        cells[(x, y)] = "P"
    return cells


def art_tree():
    cells = {}
    leaves = [2, 6, 10, 14, 18]
    for y in leaves:
        raster_line(cells, (13, y), (16, y), "N")
        for x in (17, 18, 19):
            cells[(x, y)] = "P"
    for top, bottom, x in ((2, 6, 13), (14, 18, 13), (4, 10, 9), (7, 16, 4)):
        raster_line(cells, (x, top), (x, bottom), "N")
    raster_line(cells, (9, 10), (13, 10), "N")
    raster_line(cells, (9, 4), (13, 4), "N")
    raster_line(cells, (4, 7), (9, 7), "N")
    raster_line(cells, (4, 16), (13, 16), "N")
    raster_line(cells, (1, 11), (4, 11), "L")
    return cells


ARTS = dict(sylvi=art_sylvi, collatz=art_collatz, helix=art_helix, lissajous=art_lissajous, tree=art_tree)


def icon(project, x, y, delay):
    """The pixel drawing on its ink square; rows appear top to bottom, like a slow scan."""
    colours = dict(P=BRAND["paper"], L=BRAND["lavender"], N=BRAND["neon"], D=BRAND["deep"])
    cells = ARTS[project["art"]]()
    rows = []
    for r in range(GRID):
        paths = []
        for key, colour in colours.items():
            d = "".join(f"M{x + c * PIXEL:.1f} {y + r * PIXEL:.1f}h{PIXEL}v{PIXEL}h-{PIXEL}Z"
                        for c in range(GRID) if cells.get((c, r)) == key)
            if d:
                paths.append(f'<path d="{d}" fill="{colour}"/>')
        if paths:
            rows.append(f'<g opacity="1">{fade(delay + r * 0.025, 0.12)}{"".join(paths)}</g>')
    return (f'<rect x="{x}" y="{y}" width="{GRID * PIXEL}" height="{GRID * PIXEL}" rx="5" fill="{BRAND["ink"]}"/>'
            f'<g shape-rendering="crispEdges">{"".join(rows)}</g>')


def project_card(p, theme):
    s = SHEET[theme]
    ts = Typesetter("p")
    body = [card(theme, CARD_W, CARD_H), icon(p, 16, 10, 0.05)]
    status = "public" if p["repo"] else "private"
    room = CARD_W - 88 - 16
    if not p["repo"]:     # a lock and a word, so the missing link reads as deliberate
        tag = ts.text("private", "code", 12, CARD_W - 14, 30, s["muted"], anchor="end")[0]
        lx = CARD_W - 14 - text_width("private", "code", 12) - 14
        body.append(tag + f'<path d="M{lx + 2} 21v-2a3 3 0 0 1 6 0v2" fill="none" stroke="{s["muted"]}" stroke-width="1.5"/>'
                    f'<rect x="{lx}" y="21" width="10" height="9" rx="1.5" fill="{s["muted"]}"/>')
        room = lx - 8 - 88
    size = 18
    while text_width(p["name"], "label", size) > room:
        size -= 1
    body.append(f'<g opacity="1">{fade(0.2)}{ts.text(p["name"], "label", size, 88, 38, s["text"])[0]}</g>')
    body.append(f'<g opacity="1">{fade(0.3)}{ts.text(p["line"], "text", 14, 88, 60, s["muted"])[0]}</g>')
    names = "  ".join(short for short, _ in p["stack"])
    svg, _ = strip(ts, CARD_W, CARD_H - STRIP, [("$ ", BRAND["neon"]), (names, BRAND["paper"])], start=0.5, rate=0.012)
    body.append(svg)
    alt = (f"{p['name']}, {status} repository: {p['line']} {p['detail']}. "
           f"Built with {', '.join(full for _, full in p['stack'])}.")
    return svg_doc(CARD_W, CARD_H, ts.defs_svg() + "".join(body), alt), alt


def slug(name):
    return name.lower().replace(" ", "-")


def block():
    cells = []
    for p in PROJECTS:
        _, alt = project_card(p, "light")
        pic = themed(f"projects/{slug(p['name'])}", alt, CARD_W, CARD_H)
        cells.append(f'<a href="{GITHUB}/{p["repo"]}">{pic}</a>' if p["repo"] else pic)
    return "<p>\n" + "\n".join(cells) + "\n</p>"


if __name__ == "__main__":
    out = ASSETS / "projects"
    out.mkdir(parents=True, exist_ok=True)
    for old in out.glob("*.svg"):
        old.unlink()
    for theme in SHEET:
        for p in PROJECTS:
            (out / f"{slug(p['name'])}-{theme}.svg").write_text(project_card(p, theme)[0], encoding="utf-8")
    changed = replace_block("PROJECTS", block())
    print(f"wrote {len(PROJECTS)} project cards per theme, README {'updated' if changed else 'unchanged'}")
