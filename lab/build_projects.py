#!/usr/bin/env python3
"""Draw the project sheets and fill the README's PROJECTS block.

The first project is the featured one: a full-width lab sheet (with a phone
layout) carrying big pixel art, the story, its award and the whole stack. The
rest are torn lab sheets two to a row: an original pixel icon of what the
project does, its name, one line and the stack as notched chips. Sheets resolve
out of a pixel dither as they scroll into view; the chips then cut in one by one. Private repositories are
labelled rather than linked to a page that would 404.

    python lab/build_projects.py
"""
import math

from notebook import (ASSETS, BRAND, PAPER, SHADE, Typesetter, box, fit, flip, mark, paragraph, pixels,
                      print_clip, replace_block, scene, sheet, sprite_at, step_in, svg_doc, text_width, wide_scene)
from pixel import TROPHY, TROPHY_GLINT

GITHUB = "https://github.com/Llenoxinn"
PROJECTS = [
    dict(name="PlacebAIStudio", repo=None, live="https://placebeat-studio.vercel.app", art="placebo",
         line="Every effect works. None touch your audio.",
         story="Reverb echoes your clicks, bass boost drops the buttons, and export hands back a silent master.",
         award=("Champion, Rage Quit Award", "at MALFUNCTION Hackathon 2026, iDE.A iAcademy"),
         detail="MALFUNCTION 2026 champion, Rage Quit Award, with team Dexter's Fun Club",
         stack=[("react", "React"), ("ts", "TypeScript"), ("vite", "Vite"), ("vitest", "Vitest"),
                ("matter", "Matter.js"), ("xstate", "XState"), ("claude", "Claude API")]),
    dict(name="dfCTF", repo="dfCTF", art="flag",
         line="Solve flags. Climb the weekly board.", detail="Seven categories, first-blood tracking and timed events",
         stack=[("ts", "TypeScript"), ("next", "Next.js"), ("react", "React"), ("postgres", "PostgreSQL"),
                ("drizzle", "Drizzle"), ("docker", "Docker")]),
    dict(name="BELaude", repo="BELaude", art="laude",
         line="The GWA you need for Latin honors.", detail="Summa, magna or cum laude, semester by semester, for UP students",
         stack=[("react", "React"), ("ts", "TypeScript"), ("vite", "Vite"), ("tailwind", "Tailwind CSS"),
                ("vitest", "Vitest"), ("python", "Python")]),
    dict(name="Sylvi", repo="Sylvi", art="sylvi",
         line="ID photo sheets, printed true to size.", detail="1×1, 2×2 and passport sizes, as PDF, PNG or JPG",
         stack=[("ts", "TypeScript"), ("js", "JavaScript"), ("react", "React"), ("vite", "Vite"),
                ("plpgsql", "PL/pgSQL"), ("html", "HTML"), ("css", "CSS")]),
    dict(name="Olatz-Tol", repo="Olatz-tol", art="collatz",
         line="Pick a number. Watch it fall to 1.", detail="The Collatz 3n + 1 rule, drawn",
         stack=[("react", "React"), ("vite", "Vite"), ("tailwind", "Tailwind CSS"), ("zustand", "Zustand"),
                ("lucide", "Lucide")]),
    dict(name="Protein Structure Viewer Lite", repo="Protein-Structure-Viewer-Lite-", art="helix",
         line="Proteins in 3D, on raw Three.js.", detail="No NGL, Mol* or 3Dmol.js inside",
         stack=[("react", "React"), ("vite", "Vite"), ("three", "Three.js"), ("r3f", "React Three Fiber"),
                ("drei", "Drei"), ("tailwind", "Tailwind CSS")]),
    dict(name="viscal", repo="Viscal", art="lissajous",
         line="Generative art from pure math.", detail="Lissajous curves, L-systems and Gray–Scott patterns",
         stack=[("react", "React"), ("vite", "Vite"), ("tailwind", "Tailwind CSS")]),
    dict(name="Perk the Star", repo="GeoCeff/perk-the-star", art="orbit",
         line="Rotating towers defend the Sun.", detail="Godot 4.6 orbital tower defense, built with GeoCeff",
         stack=[("godot", "Godot"), ("c++", "C++"), ("gdscript", "GDScript")]),
    dict(name="PhyTree", repo=None, art="tree",
         line="Trees of life, built step by step.", detail="Alignment, UPGMA and Neighbor-Joining",
         stack=[("ts", "TypeScript"), ("react", "React"), ("vite", "Vite"), ("tailwind", "Tailwind CSS"),
                ("d3", "D3.js"), ("zustand", "Zustand")]),
]
CARD_W, CARD_H = 376, 104
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


def art_orbit():
    """The Sun, two orbits and the towers riding them."""
    cells, c = {}, 9.5
    for i in range(400):
        a = 2 * math.pi * i / 400
        for r in (5.2, 8.6):
            cells.setdefault((round(c + r * math.cos(a)), round(c + r * math.sin(a))), "N")
    for x in range(20):
        for y in range(20):
            d = math.hypot(x - c, y - c)
            if d <= 2.4:
                cells[(x, y)] = "P"
            elif d <= 3.2:
                cells[(x, y)] = "L"
    for r, angles in ((5.2, (30, 210)), (8.6, (100, 250, 340))):
        for deg in angles:
            tx, ty = round(c + r * math.cos(math.radians(deg))), round(c + r * math.sin(math.radians(deg)))
            for dx in (0, 1):
                for dy in (0, 1):
                    cells[(tx + dx - 1, ty + dy - 1)] = "P"
    return cells


def art_flag():
    """A capture flag on its pole, mid-wave."""
    cells = {}
    for y in range(2, 19):
        cells[(4, y)] = "L"
    for x in range(2, 8):
        cells[(x, 18)] = "N"
    for x in range(5, 18):
        wave = round(1.2 * math.sin((x - 5) / 12 * 2 * math.pi))
        for y in range(3 + wave, 11 + wave):
            cells[(x, y)] = "P"
    for x, y in ((8, 6), (9, 6), (8, 7), (9, 7), (12, 5), (13, 5), (12, 6), (13, 6)):
        cells[(x, y + round(1.2 * math.sin((x - 5) / 12 * 2 * math.pi)))] = "N"
    return cells


def art_laude():
    """A mortarboard with its tassel."""
    cells = {}
    for y in range(3, 11):
        half = 8 - abs(y - 7) * 2
        for x in range(10 - half, 10 + half):
            cells[(x, y)] = "P"
    for y in range(10, 15):
        for x in range(5, 15):
            cells[(x, y)] = "L"
    for x in range(5, 15):
        cells[(x, 15)] = "N"
    cells[(9, 6)] = cells[(10, 6)] = "N"
    for x, y in ((11, 7), (12, 8), (13, 9), (14, 10), (15, 11)):
        cells[(x, y)] = "N"
    for y in range(12, 17):
        cells[(16, y)] = "N"
    for x in (15, 16, 17):
        cells[(x, 17)] = "P"
    return cells


def art_placebo():
    """A placebo capsule over a sound wave: half paper, half neon, tilted."""
    cells = {}
    for i in range(20):
        y = round(15 + 2.2 * math.sin(i / 19 * 4 * math.pi))
        cells[(i, y)] = "L"
        cells[(i, y + 1)] = "L"
    for x in range(1, 19):
        for y in range(1, 13):
            u, v = (x - 9.5) * 0.8 + (y - 7) * 0.6, -(x - 9.5) * 0.6 + (y - 7) * 0.8
            if (abs(u) <= 5 and abs(v) <= 2.8) or math.hypot(abs(u) - 5, v) <= 2.8:
                cells[(x, y)] = "P" if u < 0 else "N"
    for x, y in ((6, 6), (7, 5)):
        cells[(x, y)] = "L"          # a glint on the paper half
    return cells


ARTS = dict(placebo=art_placebo, flag=art_flag, laude=art_laude, sylvi=art_sylvi, collatz=art_collatz, helix=art_helix, lissajous=art_lissajous, tree=art_tree,
            orbit=art_orbit)


def icon(project, x, y):
    """The project's pixel drawing, in paper, lavender and neon, for an ink box."""
    colours = dict(P=BRAND["paper"], L=BRAND["lavender"], N=BRAND["neon"], D=BRAND["deep"])
    cells = ARTS[project["art"]]()
    rows = ["".join(cells.get((c, r), ".") for c in range(GRID)) for r in range(GRID)]
    return pixels(rows, x, y, PIXEL, colours)


def chips(ts, theme, stack, x, y, room, delay):
    """Stack as notched chips: an icon where the lab has one, else the name. Overflow folds into +N."""
    from icons import ICONS
    s = PAPER[theme]
    out = []
    for k, name in enumerate(stack):
        if name.lower() in ICONS:
            w, inner = 22, mark(name, x + 4, y + 4, 14, s["text"])
        else:
            w = text_width(name, "body-bold", 11) + 14
            inner = ts.text(name, "body-bold", 11, x + 7, y + 15, s["text"])[0]
        rest = len(stack) - k - 1
        if x + w + (30 if rest else 0) > room:
            more = f"+{len(stack) - k}"
            w = text_width(more, "body-bold", 12) + 14
            out.append(f'<g>{step_in(delay(k))}{box(x, y, w, 22, s["soft"], 2)}'
                       f'{ts.text(more, "body-bold", 12, x + 7, y + 15.5, s["muted"])[0]}</g>')
            break
        out.append(f'<g>{step_in(delay(k))}{box(x, y, w, 22, s["chip"], 2, s["line"])}{inner}</g>')
        x += w + 4
    return "".join(out)


def status(ts, theme, p, right, y, animate):
    """Top-right tag: where the code lives. A lit LED means you can open it."""
    s = PAPER[theme]
    words = "live demo" if p.get("live") and not p["repo"] else ("public" if p["repo"] else "private")
    w = text_width(words, "pixel", 12) + 28
    x = right - w
    lit = bool(p["repo"] or p.get("live"))
    led = f'<rect x="{x + 7}" y="{y + 7}" width="6" height="6" fill="{s["led"] if lit else s["muted"]}"/>'
    return (box(x, y, w, 20, s["soft"], 2) + led
            + ts.text(words, "pixel", 12, x + 19, y + 14.5, s["text"])[0]), x


def link(p):
    if p["repo"]:
        return f"https://github.com/{p['repo']}" if "/" in p["repo"] else f"{GITHUB}/{p['repo']}"
    return p.get("live")


def project_card(p, theme, animate=True):
    s = PAPER[theme]
    ts = Typesetter("p")
    body = [sheet(theme, CARD_W, CARD_H, p["name"])]
    art = icon(p, 16, 18)
    body.append(box(14, 16, 60, 60, BRAND["ink"], 3) + art)
    pill, px = status(ts, theme, p, CARD_W - SHADE - 12, 14, animate)
    body.append(pill)
    size = fit(p["name"], "title", 18, px - 8 - 88)
    body.append(ts.text(p["name"], "title", size, 88, 30, s["text"])[0])
    body.append(ts.text(p["line"], "body", 13, 88, 52, s["muted"])[0])
    at = (lambda k: 0.7 + k * 0.07) if animate else (lambda k: None)
    body.append(chips(ts, theme, [full for _, full in p["stack"]], 88, 64, CARD_W - SHADE - 12, at))
    where = (f"{'public' if p['repo'] else 'private'} repository"
             + (f", with {p['repo'].split('/')[0]}" if p["repo"] and "/" in p["repo"] else "")
             + (", live demo" if p.get("live") else ""))
    alt = (f"{p['name']}, {where}: {p['line']} {p['detail']}. "
           f"Built with {', '.join(full for _, full in p['stack'])}.")
    inner = "".join(body)
    if animate:
        defs, clip = print_clip(f"pc{slug(p['name'])}", CARD_W, CARD_H)
        inner = f'<defs>{defs}</defs><g{clip}>{inner}</g>'
    return svg_doc(CARD_W, CARD_H, ts.defs_svg() + inner, alt), alt


def big_art(p, x, y, scale):
    colours = dict(P=BRAND["paper"], L=BRAND["lavender"], N=BRAND["neon"], D=BRAND["deep"])
    cells = ARTS[p["art"]]()
    rows = ["".join(cells.get((c, r), ".") for c in range(GRID)) for r in range(GRID)]
    return pixels(rows, x, y, scale, colours)


def feature_card(p, theme, layout, animate=True):
    """The featured project: big pixel art, story, award band and full stack on one wide sheet."""
    s = PAPER[theme]
    ts = Typesetter("ft")
    wide = layout == "wide"
    W = 840 if wide else 400
    right = W - SHADE - 14
    art_box, scale = (148, 6.6) if wide else (96, 4.4)
    art = big_art(p, 18 + (art_box - GRID * scale) / 2, 20 + (art_box - GRID * scale) / 2, scale)
    body = [box(18, 20, art_box, art_box, BRAND["ink"], 4),
            art]
    tx = 18 + art_box + 24
    pill, px = status(ts, theme, p, right if wide else tx - status(ts, theme, p, 0, 0, False)[1], 18 if wide else 66,
                      animate)
    body.append(pill)
    tsize = fit(p["name"], "title", 30 if wide else 24, (px - 12 if wide else right) - tx)
    body.append(ts.text(p["name"], "title", tsize, tx, 54 if wide else 52, s["text"])[0])
    if wide:
        body.append(ts.text(p["line"], "body", 15.5, tx, 82, s["text"])[0])
        story, y = paragraph(ts, p["story"], "body", 13.5, tx, 104, right - tx, s["muted"])
        ax = tx
    else:
        line, y = paragraph(ts, p["line"], "body", 15, 18, 146, right - 18, s["text"])
        story, y = paragraph(ts, p["story"], "body", 13.5, 18, y + 22, right - 18, s["muted"])
        body.append(line)
        ax = 18
    body.append(story)
    # the award, on a band of its own with a glinting trophy
    title, event = p["award"]
    by = y + 14
    bh = 32 if wide else 50
    cup = dict(P=s["text"], N=s["text"], L=s["muted"])      # ink on paper, paper on navy
    ta = sprite_at(TROPHY, ax + 8, by + (bh - 20) / 2, 2, cup)
    tb = sprite_at(TROPHY_GLINT, ax + 8, by + (bh - 20) / 2, 2, dict(cup, L=BRAND["neon"]))
    body.append(box(ax, by, right - ax, bh, s["soft"], 2)
                + (flip(ta, tb, 4.8, 1.2, rhythm="000000000100") if animate else ta))
    if wide:
        tw = text_width(title, "title", 14)
        body.append(ts.text(title, "title", 14, ax + 38, by + 21, s["text"])[0]
                    + ts.text(event, "body", 13, ax + 38 + tw + 12, by + 21, s["muted"])[0])
    else:
        body.append(ts.text(title, "title", 14, ax + 38, by + 21, s["text"])[0]
                    + ts.text(event, "body", fit(event, "body", 12.5, right - ax - 46), ax + 38, by + 39, s["muted"])[0])
    cy = by + bh + 12
    at = (lambda k: 0.7 + k * 0.07) if animate else (lambda k: None)
    body.append(chips(ts, theme, [full for _, full in p["stack"]], ax, cy, right + 2, at))
    H = int(max(cy + 22, 20 + art_box) + 16 + SHADE)
    body.insert(0, sheet(theme, W, H, f"feature{layout}"))
    alt = (f"{p['name']}, featured, private repository with a live demo: {p['line']} {p['story']} "
           f"{title} {event}. Built with {', '.join(full for _, full in p['stack'])}.")
    inner = "".join(body)
    if animate:
        defs, clip = print_clip(f"ft{layout}", W, H, steps=12, dur=0.7)
        inner = f'<defs>{defs}</defs><g{clip}>{inner}</g>'
    return svg_doc(W, H, ts.defs_svg() + inner, alt), alt


def slug(name):
    return name.lower().replace(" ", "-")


def block():
    lead, rest = PROJECTS[0], PROJECTS[1:]
    stem = f"projects/{slug(lead['name'])}-feature"
    hero = wide_scene(stem, f"{stem}-narrow", feature_card(lead, "light", "wide")[1])
    cells = []
    for p in rest:
        _, alt = project_card(p, "light")
        pic = scene(f"projects/{slug(p['name'])}", alt, CARD_W, CARD_H)
        cells.append(f'<a href="{link(p)}">{pic}</a>' if link(p) else pic)
    return (f'<p align="center">\n<a href="{link(lead)}">{hero}</a>\n</p>\n'
            '<p align="center">\n' + "\n".join(cells) + "\n</p>")


if __name__ == "__main__":
    out = ASSETS / "projects"
    out.mkdir(parents=True, exist_ok=True)
    for old in out.glob("*.svg"):
        old.unlink()
    lead = PROJECTS[0]
    for theme in PAPER:
        for layout, stem in (("wide", f"{slug(lead['name'])}-feature"), ("narrow", f"{slug(lead['name'])}-feature-narrow")):
            (out / f"{stem}-{theme}.svg").write_text(feature_card(lead, theme, layout)[0], encoding="utf-8")
            (out / f"{stem}-still-{theme}.svg").write_text(feature_card(lead, theme, layout, False)[0], encoding="utf-8")
        for p in PROJECTS[1:]:
            (out / f"{slug(p['name'])}-{theme}.svg").write_text(project_card(p, theme)[0], encoding="utf-8")
            (out / f"{slug(p['name'])}-still-{theme}.svg").write_text(project_card(p, theme, False)[0], encoding="utf-8")
    changed = replace_block("PROJECTS", block())
    print(f"wrote the featured sheet and {len(PROJECTS) - 1} project cards per theme, "
          f"README {'updated' if changed else 'unchanged'}")
