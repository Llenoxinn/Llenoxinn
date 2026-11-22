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

from notebook import (ASSETS, BRAND, PAPER, SHADE, Typesetter, box, fit, frames, mark, nudge_in, paragraph, pixels,
                      printed, replace_block, scene, sheet, sparkle, stamp, svg_doc, text_width, wide_scene)
from pixel import CUP_HACK, sheen_mask

GITHUB = "https://github.com/Llenoxinn"
PROJECTS = [
    dict(name="PlacebAIStudio", repo=None, live="https://placebeat-studio.vercel.app", art="placebo",
         line="Every effect works, except none of them touch your audio.",
         story="Reverb echoes your clicks, bass boost drops the buttons, and export hands back a silent master.",
         award=("Champion, Rage Quit Award", "at MALFUNCTION Hackathon 2026, iDE.A iAcademy"),
         detail="MALFUNCTION 2026 champion, Rage Quit Award, with Team Dexter's Fun Club",
         stack=[("react", "React"), ("ts", "TypeScript"), ("vite", "Vite"), ("vitest", "Vitest"),
                ("matter", "Matter.js"), ("xstate", "XState"), ("claude", "Claude API")]),
    dict(name="dfCTF", repo="dfCTF", art="flag",
         line="Capture flags and climb the weekly leaderboard.", detail="Seven categories, first-blood tracking, and timed events",
         stack=[("ts", "TypeScript"), ("next", "Next.js"), ("react", "React"), ("postgres", "PostgreSQL"),
                ("drizzle", "Drizzle"), ("docker", "Docker")]),
    dict(name="BELaude", repo="BELaude", art="laude",
         line="Track the GWA you need for UP Latin honors.", detail="Summa, magna, or cum laude, semester by semester, for UP students",
         stack=[("react", "React"), ("ts", "TypeScript"), ("vite", "Vite"), ("tailwind", "Tailwind CSS"),
                ("vitest", "Vitest"), ("python", "Python")]),
    dict(name="Sylvi", repo="Sylvi", art="sylvi",
         line="Generate print-ready ID photo sheets true to size.", detail="1×1, 2×2, and passport sizes, as PDF, PNG, or JPG",
         stack=[("ts", "TypeScript"), ("js", "JavaScript"), ("react", "React"), ("vite", "Vite"),
                ("plpgsql", "PL/pgSQL"), ("html", "HTML"), ("css", "CSS")]),
    dict(name="Olatz-Tol", repo="Olatz-tol", art="collatz",
         line="Pick a number and watch the 3n + 1 path fall to 1.", detail="Interactive Collatz conjecture visualizer",
         stack=[("react", "React"), ("vite", "Vite"), ("tailwind", "Tailwind CSS"), ("zustand", "Zustand"),
                ("lucide", "Lucide")]),
    dict(name="Protein Structure Viewer Lite", repo="Protein-Structure-Viewer-Lite-", art="helix",
         line="Explore 3D protein structures built on raw Three.js.", detail="Built from scratch without NGL, Mol*, or 3Dmol.js",
         stack=[("react", "React"), ("vite", "Vite"), ("three", "Three.js"), ("r3f", "React Three Fiber"),
                ("drei", "Drei"), ("tailwind", "Tailwind CSS")]),
    dict(name="viscal", repo="Viscal", art="lissajous",
         line="Interactive generative art driven by pure math.", detail="Lissajous curves, L-systems, and Gray–Scott patterns",
         stack=[("react", "React"), ("vite", "Vite"), ("tailwind", "Tailwind CSS")]),
    dict(name="Perk the Star", repo="GeoCeff/perk-the-star", art="orbit",
         line="Defend the Sun with rotating orbital towers.", detail="Godot 4.6 orbital tower defense, built with GeoCeff",
         stack=[("godot", "Godot"), ("c++", "C++"), ("gdscript", "GDScript")]),
    dict(name="PhyTree", repo=None, art="tree",
         line="Build and trace phylogenetic trees step by step.", detail="Sequence alignment, UPGMA, and Neighbor-Joining",
         stack=[("ts", "TypeScript"), ("react", "React"), ("vite", "Vite"), ("tailwind", "Tailwind CSS"),
                ("d3", "D3.js"), ("zustand", "Zustand")]),
]
CARD_W, CARD_H = 376, 104
GRID, PIXEL = 28, 2               # crisp 28 × 28 pixel illustration at exact integer 2× scale (56 px in a 64 px double-bezel)

# 8-tone harmonized DOS-lab illustration palette:
# K = obsidian contour/shadow, D = deep navy, M = mid-indigo grid/dither, B = royal shade,
# N = electric neon, L = lavender mid-highlight, P = crisp paper, W = pure specular white.
ART_PALETTE = dict(
    K="#050533",
    D="#0a0a5d",
    M="#1c1c94",
    B="#2e2ec4",
    N=BRAND["neon"],
    L="#b8b8f8",
    P=BRAND["paper"],
    W="#ffffff",
)

BAYER4 = ((0, 8, 2, 10), (12, 4, 14, 6), (3, 11, 1, 9), (15, 7, 13, 5))


# ------------------------------------------------------------------ 28×28 pixel illustrations

def _put(cells, x, y, val):
    if 0 <= x < GRID and 0 <= y < GRID:
        cells[(x, y)] = val


def raster_line(cells, a, b, value):
    (x0, y0), (x1, y1) = a, b
    steps = max(abs(x1 - x0), abs(y1 - y0), 1)
    for i in range(steps + 1):
        _put(cells, round(x0 + (x1 - x0) * i / steps), round(y0 + (y1 - y0) * i / steps), value)


def _bg_dither_glow(cx, cy, radius, col="M", strength=0.38):
    """Ordered Bayer-dither radial glow for atmospheric depth inside a viewport."""
    cells = {}
    for y in range(GRID):
        for x in range(GRID):
            d = math.hypot(x - cx, y - cy) / radius
            if d < 1.0:
                dens = strength * (1.0 - d)
                if BAYER4[y % 4][x % 4] < dens * 16:
                    cells[(x, y)] = col
    return cells


def _bg_grid(step=6, col="M"):
    """Subtle oscilloscope / blueprint dot-grid texture."""
    cells = {}
    for y in range(2, GRID - 1, step):
        for x in range(2, GRID - 1, step):
            cells[(x, y)] = col
    return cells


def _outline_shadow(cells, fg_keys=("P", "L", "N", "W", "B"), shadow_col="K", dx=1, dy=1):
    """Add a 1-pixel offset cast shadow behind foreground pixels for tactile depth."""
    sh = {}
    for (x, y), v in cells.items():
        if v in fg_keys:
            nx, ny = x + dx, y + dy
            if 0 <= nx < GRID and 0 <= ny < GRID and (nx, ny) not in cells:
                sh[(nx, ny)] = shadow_col
    return {**sh, **cells}


def bg_placebo():
    cells = _bg_dither_glow(13.5, 11.5, 13.5, "M", 0.34)
    for x in range(1, GRID - 1, 3):
        cells.setdefault((x, 21), "M")
    for y in range(2, GRID - 2, 5):
        for x in range(2, GRID - 2, 5):
            cells[(x, y)] = "M"
    return cells


def art_placebo(phase=0):
    """Sculpted 3D tilted placebo capsule floating over a glowing dual-layer audio waveform."""
    cells = {}
    shift = phase * (math.pi / 2)
    # Ghost harmonic wave behind (royal blue B) + main stereo wave (neon N, lavender L, paper P peaks)
    for i in range(1, GRID - 1):
        y_echo = round(21.5 + 2.4 * math.sin(i / 25 * 4 * math.pi - shift + 1.1))
        _put(cells, i, y_echo, "B")
    for i in range(1, GRID - 1):
        s = math.sin(i / 25 * 4 * math.pi - shift)
        y = round(21.5 + 2.8 * s)
        _put(cells, i, y + 1, "B")
        _put(cells, i, y, "N")
        if abs(s) > 0.72:
            _put(cells, i, y, "L")
            _put(cells, i, y - 1, "P" if s < -0.72 else "L")

    # Subtle 1px celebratory float bob on the capsule
    bob = -1 if phase in (1, 2) else 0
    cx, cy = 13.5, 10.5 + bob

    # Cast shadow under capsule
    for x in range(6, 22):
        if (x + phase) % 2 == 0:
            _put(cells, x, 17, "K")

    # 3D tilted pill capsule (rotated ~36 deg) with cylinder shading & dividing seam
    cos_a, sin_a = 0.80, 0.60
    half_len, rad = 5.4, 3.8
    for y in range(1, 20):
        for x in range(2, 26):
            u = (x - cx) * cos_a + (y - cy) * sin_a
            v = -(x - cx) * sin_a + (y - cy) * cos_a
            dist = abs(v) if abs(u) <= half_len else math.hypot(abs(u) - half_len, v)
            if dist <= rad + 0.85 and dist > rad:
                _put(cells, x, y, "K")     # crisp dark silhouette contour
            elif dist <= rad:
                # Shading across cylinder cross-section v (top-left light: negative v is lit)
                if abs(u) < 0.55:
                    _put(cells, x, y, "D")  # crisp center capsule seam
                elif u < 0:
                    # Paper/white half
                    if v < -2.1:
                        _put(cells, x, y, "W")
                    elif v < 1.1:
                        _put(cells, x, y, "P")
                    else:
                        _put(cells, x, y, "L")
                else:
                    # Neon/royal half
                    if v < -2.0:
                        _put(cells, x, y, "L")
                    elif v < 1.0:
                        _put(cells, x, y, "N")
                    else:
                        _put(cells, x, y, "B")

    # Sweeping pure-white specular sheen pixel along the upper curve
    glint_pts = ((8, 7), (9, 7), (10, 8)) if phase == 2 else ((7, 8), (8, 8))
    for gx, gy in glint_pts:
        _put(cells, gx, gy + bob, "W")
    return cells


def bg_flag():
    cells = _bg_dither_glow(14, 12, 13, "M", 0.36)
    # Faint horizon ground line
    for x in range(2, 26):
        cells[(x, 24)] = "M"
    return cells


def art_flag(phase=0):
    """Billowing 3D shaded CTF pennant on a metallic flagpole & stepped pedestal."""
    cells = {}
    # Stepped pedestal base with highlight & shadow
    for x in range(4, 13):
        _put(cells, x, 24, "B")
        _put(cells, x, 25, "K")
    for x in range(5, 12):
        _put(cells, x, 23, "N")
    for x in range(6, 11):
        _put(cells, x, 22, "L")
    # Metallic flagpole (2px shaded shaft + gleaming finial orb)
    for y in range(4, 23):
        _put(cells, 7, y, "P" if y % 4 != 0 else "L")
        _put(cells, 8, y, "B")
    _put(cells, 7, 3, "W")
    _put(cells, 8, 3, "L")
    if phase == 2:
        _put(cells, 7, 2, "W")
        _put(cells, 6, 3, "L")
    # Billowing checkered CTF cloth with real wave-trough shading
    shift = phase * (math.pi / 2)
    for i in range(15):
        x = 9 + i
        s = math.sin(i / 14 * 2 * math.pi - shift)
        wave = round(1.4 * s)
        trough = s > 0.35
        crest = s < -0.35
        height = 10 if i < 12 else (9 if i < 14 else 7)
        for dy in range(height):
            y = 5 + wave + dy
            chk = ((i // 3) + (dy // 3)) % 2 == 0
            if dy == 0:
                col = "W" if crest else ("L" if chk else "N")
            elif dy == height - 1:
                col = "B" if not chk else "L"
            elif chk:
                col = "L" if trough else ("W" if crest and dy < 3 else "P")
            else:
                col = "B" if trough else "N"
            _put(cells, x, y, col)
    return _outline_shadow(cells, dx=1, dy=1)


def bg_laude():
    cells = _bg_dither_glow(14, 13, 13, "M", 0.34)
    # Subtle pixel laurel sprigs in lower corners
    for dx, dy in ((4, 22), (5, 23), (7, 24), (23, 22), (22, 23), (20, 24)):
        _put(cells, dx, dy, "B")
    return cells


def art_laude(phase=0):
    """3D isometric mortarboard with sculpted cap, specular rim, and swaying fringed tassel."""
    cells = {}
    # Skullcap body (cylinder shaded B -> N -> L)
    for y in range(13, 21):
        for x in range(8, 20):
            if y == 20 and (x < 10 or x > 17):
                continue
            if x <= 10:
                col = "L"
            elif x <= 15:
                col = "N"
            else:
                col = "B"
            _put(cells, x, y, col)
    for x in range(8, 20):
        _put(cells, x, 13, "D")  # cast shadow under board rim
        _put(cells, x, 14, "K")

    # Isometric diamond board (rows 5..14, width up to 24px)
    for y in range(5, 15):
        half = round(11.5 - abs(y - 9.5) * 2.2)
        for x in range(14 - half, 14 + half + 1):
            if y == 5 or (y <= 9 and x == 14 - half):
                col = "W"          # crisp top-left specular bevel
            elif y <= 9:
                col = "P"          # lit upper facet
            elif y == 14:
                col = "N"          # front bevel edge
            else:
                col = "L"          # lower plane shading
            _put(cells, x, y, col)
    # Center crown button
    _put(cells, 13, 9, "N")
    _put(cells, 14, 9, "W")
    # Braided tassel cord draped over right edge
    for cx, cy in ((15, 9), (17, 10), (19, 11), (21, 12), (22, 13)):
        _put(cells, cx, cy, "N")
        _put(cells, cx + 1, cy, "L")
    sway = 1 if phase == 1 else 0
    for y in range(14, 21):
        tx = 22 + (sway if y >= 17 else 0)
        _put(cells, tx, y, "N")
    # Fringed tassel bell
    tx = 22 + sway
    _put(cells, tx, 20, "W")
    for dx in (-1, 0, 1):
        _put(cells, tx + dx, 21, "P")
        _put(cells, tx + dx, 22, "L" if dx == 1 else "P")
        _put(cells, tx + dx, 23, "N")
    # Crown sparkle on rest-break frame
    if phase == 1:
        for sx, sy in ((14, 3), (14, 4), (13, 4), (15, 4)):
            _put(cells, sx, sy, "W")
    return _outline_shadow(cells, dx=1, dy=1)


def bg_sylvi():
    cells = _bg_grid(4, "M")
    return cells


def art_sylvi(phase=0):
    """Print-ready 2×2 ID photo sheet with drop shadow, shaded mini portraits & precision crop marks."""
    cells = {}
    # Paper sheet with 2px offset shadow
    for y in range(5, 25):
        for x in range(5, 25):
            _put(cells, x, y, "K")
    for y in range(3, 24):
        for x in range(3, 24):
            _put(cells, x, y, "P" if x < 22 and y < 22 else "L")
    # 4 crisp ID photo frames (2×2 grid) with shaded head + shoulders
    portrait = [
        "BBBBBBBB",
        "BLLMLLLB",
        "BLLWPLLB",
        "BLLPPLLB",
        "BLNNNNLB",
        "BNNPPNNB",
        "BNNPPNNB",
        "BBBBBBBB",
    ]
    for ox, oy in ((5, 5), (14, 5), (5, 14), (14, 14)):
        for r, row in enumerate(portrait):
            for c, ch in enumerate(row):
                _put(cells, ox + c, oy + r, ch)
    # Dotted center cut guides
    for i in range(4, 23, 2):
        _put(cells, 13, i, "N")
        _put(cells, i, 13, "N")
    # Precision L-shaped corner crop marks
    crop = "W" if phase in (1, 2) else "N"
    for cx, cy, dx, dy in ((1, 1, 1, 1), (26, 1, -1, 1), (1, 26, 1, -1), (26, 26, -1, -1)):
        _put(cells, cx, cy, crop)
        _put(cells, cx + dx, cy, crop)
        _put(cells, cx + 2 * dx, cy, crop)
        _put(cells, cx, cy + dy, crop)
        _put(cells, cx, cy + 2 * dy, crop)
    # Alignment laser bar sweeping across sheet during shutter check
    if phase in (1, 2):
        ly = 9 if phase == 1 else 18
        for x in range(3, 24):
            _put(cells, x, ly, "W")
    return cells


def bg_collatz():
    cells = _bg_grid(5, "M")
    # Coordinate axes
    for i in range(2, 26):
        cells[(2, i)] = "B"
        cells[(i, 25)] = "B"
    return cells


def art_collatz(phase=0):
    """3n+1 hailstone trajectory with dithered area-under-curve, glowing nodes & hopping comet tracer."""
    seq = [6]
    while seq[-1] != 1:
        seq.append(seq[-1] // 2 if seq[-1] % 2 == 0 else 3 * seq[-1] + 1)
    peak = max(seq)
    pts = [(round(3 + 22 * i / (len(seq) - 1)), round(23 - 19 * (v - 1) / (peak - 1))) for i, v in enumerate(seq)]
    cells = {}
    # Ordered-dither fill under the curve
    for a, b in zip(pts, pts[1:]):
        steps = max(abs(b[0] - a[0]), 1)
        for i in range(steps + 1):
            x = round(a[0] + (b[0] - a[0]) * i / steps)
            y_top = round(a[1] + (b[1] - a[1]) * i / steps)
            for y in range(y_top + 1, 25):
                if BAYER4[y % 4][x % 4] < 4:
                    _put(cells, x, y, "B")
    # Glowing trajectory polyline (2px thickness via shadow + bright line)
    for a, b in zip(pts, pts[1:]):
        raster_line(cells, (a[0], a[1] + 1), (b[0], b[1] + 1), "B")
        raster_line(cells, a, b, "N")
    # Vertex beads
    for px, py in pts[:-1]:
        _put(cells, px, py, "L")
        _put(cells, px, py - 1, "P" if phase == 0 else "L")
    # Target bullseye at 1
    tx, ty = pts[-1]
    for dx in (-2, -1, 0, 1, 2):
        for dy in (-2, -1, 0, 1, 2):
            if abs(dx) + abs(dy) == 2:
                _put(cells, tx + dx, ty + dy, "N")
            elif abs(dx) + abs(dy) == 1:
                _put(cells, tx + dx, ty + dy, "L")
    _put(cells, tx, ty, "W")
    # Glowing comet tracer hopping step-by-step down the 3n+1 path
    if phase > 0:
        idx = min(phase - 1, len(pts) - 1)
        hx, hy = pts[idx]
        for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1)):
            _put(cells, hx + dx, hy + dy, "P")
        _put(cells, hx, hy, "W")
    return cells


def bg_helix():
    cells = _bg_dither_glow(14, 14, 14, "M", 0.32)
    # Tiny 3D viewport XYZ axis gizmo in bottom-left corner
    for i in range(4):
        _put(cells, 3, 24 - i, "B")
        _put(cells, 3 + i, 24, "B")
    _put(cells, 3, 20, "L")
    _put(cells, 7, 24, "N")
    return cells


def art_helix(phase=0):
    """Volumetric 3D cartoon alpha-helix ribbon rotating smoothly with real Z-depth shading."""
    back, front, rungs = {}, {}, {}
    rot = phase * (math.pi / 3)
    # Subtle hydrogen-bond dashed rungs across turns
    for k in range(5):
        u = 0.14 + k * 0.18
        x = round(3.5 + 21 * u)
        yc = round(14 - 4.5 * (u - 0.5))
        for dy in (-4, -2, 0, 2, 4):
            _put(rungs, x, yc + dy, "M")
    for i in range(1200):
        u = i / 1199
        a = 2 * math.pi * 2.5 * u + rot
        cx = 3.5 + 21 * u + 2.2 * math.cos(a)
        cy = 14 + 8.0 * math.sin(a) - 4.5 * (u - 0.5)
        z = math.cos(a)
        ix, iy = round(cx), round(cy)
        if z < 0:
            # Front-facing ribbon (thick 3px sculpted band with specular center)
            _put(front, ix, iy + 1, "K")
            _put(front, ix + 1, iy + 1, "L")
            _put(front, ix, iy, "P")
            _put(front, ix - 1, iy, "L")
            _put(front, ix, iy - 1, "W" if z < -0.55 else "P")
        else:
            # Far back ribbon shaded into depth
            _put(back, ix, iy + 1, "B")
            _put(back, ix, iy, "N")
            _put(back, ix - 1, iy, "B")
    return {**rungs, **back, **front}


def bg_lissajous():
    cells = _bg_dither_glow(13.5, 13.5, 12.5, "M", 0.30)
    # Faint oscilloscope center crosshair
    for i in range(2, 26, 2):
        cells.setdefault((i, 14), "M")
        cells.setdefault((14, i), "M")
    return cells


def art_lissajous(phase=0):
    """Phosphor CRT 3:2 Lissajous curve with glowing multi-tier beam head & afterglow tail."""
    cells = {}
    samples = 720
    # Base dim phosphor curve
    for i in range(samples):
        s = 2 * math.pi * i / samples
        x = round(13.5 + 11.2 * math.sin(3 * s + math.pi / 2))
        y = round(13.5 + 10.6 * math.sin(2 * s))
        _put(cells, x, y, "B")
        _put(cells, x, y + 1, "K")
    for i in range(samples):
        s = 2 * math.pi * i / samples
        x = round(13.5 + 11.2 * math.sin(3 * s + math.pi / 2))
        y = round(13.5 + 10.6 * math.sin(2 * s))
        _put(cells, x, y, "N")
    # Phosphor glowing tail & bright beam head tracing around the curve
    head = (phase / 12.0) * 2 * math.pi
    for k in range(110):
        s = head - (k / 110.0) * (2 * math.pi * 0.22)
        x = round(13.5 + 11.2 * math.sin(3 * s + math.pi / 2))
        y = round(13.5 + 10.6 * math.sin(2 * s))
        col = "W" if k < 10 else ("P" if k < 38 else "L")
        _put(cells, x, y, col)
    hx = round(13.5 + 11.2 * math.sin(3 * head + math.pi / 2))
    hy = round(13.5 + 10.6 * math.sin(2 * head))
    for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1)):
        _put(cells, hx + dx, hy + dy, "P")
    _put(cells, hx, hy, "W")
    return cells


def bg_orbit():
    cells = {}
    # Deep starfield backdrop
    for sx, sy, col in ((3, 4, "M"), (24, 5, "L"), (5, 23, "M"), (23, 22, "M"),
                        (18, 3, "M"), (2, 14, "B"), (25, 13, "M"), (10, 25, "M")):
        cells[(sx, sy)] = col
    return cells


def art_orbit(phase=0):
    """Radiant multi-ringed pixel Sun with counter-rotating orbital defense turrets."""
    cells, c = {}, 13.5
    # Dotted orbital rings
    for i in range(360):
        a = 2 * math.pi * i / 360
        if i % 6 < 4:
            _put(cells, round(c + 7.4 * math.cos(a)), round(c + 7.4 * math.sin(a)), "B")
        if i % 5 < 3:
            _put(cells, round(c + 11.6 * math.cos(a)), round(c + 11.6 * math.sin(a)), "N")
    # Radiant layered Sun (W core -> P photosphere -> L corona -> pulsing N flare tips)
    for y in range(7, 21):
        for x in range(7, 21):
            d = math.hypot(x - c, y - c)
            if d <= 1.8:
                _put(cells, x, y, "W")
            elif d <= 3.1:
                _put(cells, x, y, "P")
            elif d <= 4.1:
                _put(cells, x, y, "L")
            elif d <= 5.2 and BAYER4[y % 4][x % 4] < 7:
                _put(cells, x, y, "N")
    # Solar flare corona pixels alternating each step
    flare_r = 5 if phase % 2 == 0 else 6
    for dx, dy in ((flare_r, 0), (-flare_r, 0), (0, flare_r), (0, -flare_r)):
        _put(cells, round(c + dx), round(c + dy), "L" if phase % 2 == 0 else "P")
    # Shaded 3×3 orbital turrets counter-rotating on the 2 rings
    shift_in, shift_out = phase * 45, -phase * 30
    for r, angles, shift in ((7.4, (25, 205), shift_in), (11.6, (85, 215, 330), shift_out)):
        for idx, deg in enumerate(angles):
            ang = math.radians(deg + shift)
            tx, ty = round(c + r * math.cos(ang)), round(c + r * math.sin(ang))
            for dx in (-1, 0, 1):
                for dy in (-1, 0, 1):
                    _put(cells, tx + dx, ty + dy, "K" if dx == 1 and dy == 1 else "L")
            _put(cells, tx, ty, "W")
            # Outward directional barrel tip
            bx, by = round(tx + 1.8 * math.cos(ang)), round(ty + 1.8 * math.sin(ang))
            _put(cells, bx, by, "P")
            if phase % 4 == 1 and idx == 0 and r > 9:
                # Subtle 1-frame defense pulse outward
                lx, ly = round(tx + 3.2 * math.cos(ang)), round(ty + 3.2 * math.sin(ang))
                _put(cells, lx, ly, "W")
    return cells


def bg_tree():
    cells = _bg_grid(6, "M")
    # Evolutionary distance tick bar along the bottom
    for x in range(3, 25, 4):
        cells[(x, 25)] = "B"
    return cells


def art_tree(phase=0):
    """Crisp bioinformatics cladogram with speciation nodes, taxon badges & root-to-leaf trace."""
    cells = {}
    leaves = [4, 9, 14, 19, 23]
    # Clade structure with shadow depth
    segs = [
        ((2, 14), (6, 14)),     # root
        ((6, 9), (6, 21)),      # split 1
        ((6, 9), (12, 9)),      # upper clade
        ((12, 4), (12, 14)),    # split 2
        ((12, 4), (18, 4)),
        ((12, 14), (18, 14)),
        ((18, 4), (18, 9)),     # leaf pair A
        ((6, 21), (16, 21)),    # lower clade
        ((16, 19), (16, 23)),   # leaf pair B
    ]
    for a, b in segs:
        raster_line(cells, (a[0], a[1] + 1), (b[0], b[1] + 1), "K")
    for a, b in segs:
        raster_line(cells, a, b, "N")
    for y in leaves:
        start_x = 18 if y in (4, 9, 14) else 16
        raster_line(cells, (start_x, y), (22, y), "N")
        # Taxon specimen badge on right margin
        _put(cells, 23, y, "L")
        _put(cells, 24, y, "P")
        _put(cells, 25, y, "P")
        _put(cells, 24, y - 1, "L")
    # Internal speciation nodes
    for nx, ny in ((6, 14), (6, 9), (12, 9), (18, 4), (16, 21)):
        _put(cells, nx, ny, "L")
    # Animated evolutionary path trace from root -> top clade -> leaf
    trace = [
        ((2, 14), (6, 14)),
        ((6, 14), (6, 9)),
        ((6, 9), (12, 9)),
        ((12, 9), (12, 4)),
        ((12, 4), (18, 4)),
        ((18, 4), (22, 4)),
    ]
    if 1 <= phase <= len(trace):
        for seg in trace[:phase]:
            raster_line(cells, seg[0], seg[1], "L")
        cur = trace[phase - 1]
        raster_line(cells, cur[0], cur[1], "P")
        _put(cells, cur[1][0], cur[1][1], "W")
        if phase == len(trace):
            for x in (23, 24, 25):
                _put(cells, x, 4, "W")
            _put(cells, 24, 3, "W")
    return cells


BGS = dict(placebo=bg_placebo, flag=bg_flag, laude=bg_laude, sylvi=bg_sylvi, collatz=bg_collatz,
           helix=bg_helix, lissajous=bg_lissajous, tree=bg_tree, orbit=bg_orbit)
ARTS = dict(placebo=art_placebo, flag=art_flag, laude=art_laude, sylvi=art_sylvi, collatz=art_collatz,
            helix=art_helix, lissajous=art_lissajous, tree=art_tree, orbit=art_orbit)

# Per-project micro-animation schedule: (phases_to_render, period_s, order_of_indices)
# Index 0 is always the clean resting/still base frame.
ART_MOTION = {
    "placebo":   ([0, 1, 2, 3],                    2.4, [0, 1, 2, 3]),
    "flag":      ([0, 1, 2, 3],                    3.6, [0, 0, 1, 2, 3, 2, 1, 0]),
    "laude":     ([0, 1],                          4.8, [0, 0, 0, 0, 0, 0, 1, 1, 0, 0]),
    "sylvi":     ([0, 1, 2],                       5.2, [0, 0, 0, 0, 0, 0, 0, 1, 2, 0]),
    "collatz":   ([0, 1, 2, 3, 4, 5, 6, 7, 8, 9],  4.8, [0, 0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 0]),
    "helix":     ([0, 1, 2, 3, 4, 5],              3.2, [0, 1, 2, 3, 4, 5]),
    "lissajous": (list(range(12)),                 3.6, list(range(12))),
    "orbit":     ([0, 1, 2, 3, 4, 5, 6, 7],        4.8, [0, 1, 2, 3, 4, 5, 6, 7]),
    "tree":      ([0, 1, 2, 3, 4, 5, 6],           5.0, [0, 0, 0, 1, 2, 3, 4, 5, 6, 6, 0, 0]),
}


def _cells_svg(cells, x, y, scale):
    rows = ["".join(cells.get((c, r), ".") for c in range(GRID)) for r in range(GRID)]
    return pixels(rows, x, y, scale, ART_PALETTE)


def art_frame(x, y, outer_size, pad, stroke_col, art_key, scale, animate=False, begin=0.8):
    """Double-bezel notched pixel viewport: outer deep bezel + recessed dark-navy inner screen +
    top bevel highlight + static textured backdrop + animated 28×28 illustration."""
    inner = outer_size - pad * 2
    ix, iy = x + pad, y + pad
    art_x = ix + (inner - GRID * scale) / 2
    art_y = iy + (inner - GRID * scale) / 2
    chrome = (
        box(x, y, outer_size, outer_size, BRAND["deep"], 4 if outer_size >= 96 else 3, stroke_col)
        + box(ix, iy, inner, inner, "#08084a", 2, "#24249e")
        + f'<rect x="{ix + 3}" y="{iy + 1}" width="{inner - 6}" height="1" fill="#4242dc" opacity="0.65" shape-rendering="crispEdges"/>'
    )
    bg_svg = _cells_svg(BGS[art_key](), art_x, art_y, scale) if art_key in BGS else ""
    fn = ARTS[art_key]
    if not animate or art_key not in ART_MOTION:
        fg_svg = _cells_svg(fn(0), art_x, art_y, scale)
    else:
        phases, period, order = ART_MOTION[art_key]
        fg_svg = frames([_cells_svg(fn(ph), art_x, art_y, scale) for ph in phases], period, begin, order)
    return chrome + bg_svg + fg_svg


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
            out.append(f'<g>{nudge_in(delay(k), 3)}{box(x, y, w, 22, s["soft"], 2)}'
                       f'{ts.text(more, "body-bold", 12, x + 7, y + 15.5, s["muted"])[0]}</g>')
            break
        out.append(f'<g>{nudge_in(delay(k), 3)}{box(x, y, w, 22, s["chip"], 2, s["line"])}{inner}</g>')
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
    idx = PROJECTS.index(p)
    icon_svg = art_frame(12, 16, 64, 3, s["line"], p["art"], PIXEL, animate, begin=0.6 + idx * 0.45)
    pill, px = status(ts, theme, p, CARD_W - SHADE - 12, 14, animate)
    size = fit(p["name"], "title", 18, px - 8 - 88)
    lsize = fit(p["line"], "body", 13, CARD_W - SHADE - 12 - 88)
    text_block = (pill
                  + ts.text(p["name"], "title", size, 88, 30, s["text"])[0]
                  + ts.text(p["line"], "body", lsize, 88, 52, s["muted"])[0])
    at = (lambda k: 0.30 + k * 0.05) if animate else (lambda k: None)
    body = [sheet(theme, CARD_W, CARD_H, p["name"]),
            f'<g>{nudge_in(0.14, 4) if animate else ""}{icon_svg}</g>',
            f'<g>{nudge_in(0.20, 3) if animate else ""}{text_block}</g>',
            chips(ts, theme, [full for _, full in p["stack"]], 88, 64, CARD_W - SHADE - 12, at)]
    where = (f"{'public' if p['repo'] else 'private'} repository"
             + (f", with {p['repo'].split('/')[0]}" if p["repo"] and "/" in p["repo"] else "")
             + (", live demo" if p.get("live") else ""))
    alt = (f"{p['name']}, {where}: {p['line']} {p['detail']}. "
           f"Built with {', '.join(full for _, full in p['stack'])}.")
    return svg_doc(CARD_W, CARD_H, ts.defs_svg() + printed(f"pc{slug(p['name'])}", CARD_W, CARD_H, body, animate, dur=0.40), alt), alt


def feature_card(p, theme, layout, animate=True):
    """The featured project: big animated 28×28 double-bezel pixel art, story, award band and full stack."""
    s = PAPER[theme]
    ts = Typesetter("ft")
    wide = layout == "wide"
    W = 840 if wide else 400
    right = W - SHADE - 14
    art_box, pad, scale = (152, 4, 5) if wide else (96, 4, 3)
    art_svg = art_frame(18, 18 if wide else 20, art_box, pad, s["line"], p["art"], scale, animate, begin=0.6)
    body = [f'<g>{nudge_in(0.14, 4) if animate else ""}{art_svg}</g>']
    tx = 18 + art_box + 22
    pill, px = status(ts, theme, p, right if wide else tx - status(ts, theme, p, 0, 0, False)[1], 18 if wide else 66,
                      animate)
    tsize = fit(p["name"], "title", 30 if wide else 24, (px - 12 if wide else right) - tx)
    copy_parts = [pill, ts.text(p["name"], "title", tsize, tx, 54 if wide else 52, s["text"])[0]]
    if wide:
        copy_parts.append(ts.text(p["line"], "body", 15.5, tx, 82, s["text"])[0])
        story, y = paragraph(ts, p["story"], "body", 13.5, tx, 104, right - tx, s["muted"])
        ax = tx
    else:
        line, y = paragraph(ts, p["line"], "body", 15, 18, 146, right - 18, s["text"])
        story, y = paragraph(ts, p["story"], "body", 13.5, 18, y + 22, right - 18, s["muted"])
        copy_parts.append(line)
        ax = 18
    copy_parts.append(story)
    body.append(f'<g>{nudge_in(0.22, 3) if animate else ""}{"".join(copy_parts)}</g>')
    # the award, on a band of its own with the handcrafted 16×16 cup + stepped sheen & sparkle
    title, event = p["award"]
    by = y + 14
    bh = 34 if wide else 50
    cscale = 1.5
    cx, cy = ax + 8, by + (bh - 16 * cscale) / 2
    pal = (dict(P=s["text"], L="#4e4ec8", N=BRAND["neon"], D=BRAND["paper"]) if theme == "light"
           else dict(P=BRAND["paper"], L="#b8b8ec", N=BRAND["neon"], D=BRAND["deep"]))
    glint_col = BRAND["paper"] if theme == "light" else "#ffffff"
    cup_svg = pixels(CUP_HACK, cx, cy, cscale, pal)
    if animate:
        for idx, off in enumerate((7, 11, 15)):
            t0 = 0.04 + idx * 0.035
            t1 = t0 + 0.035
            cup_svg += (f'<g opacity="0"><animate attributeName="opacity" values="0;1;0" '
                        f'keyTimes="0;{t0:.4f};{t1:.4f}" calcMode="discrete" dur="5.0s" begin="1.2s" '
                        f'repeatCount="indefinite"/>{pixels(sheen_mask(CUP_HACK, off), cx, cy, cscale, {"S": glint_col})}</g>')
        cup_svg += sparkle(cx + 13 * cscale, cy + cscale, cscale, glint_col, 5.0, 1.2)
    if wide:
        tw = text_width(title, "title", 14)
        award_txt = (ts.text(title, "title", 14, ax + 40, by + 22, s["text"])[0]
                     + ts.text(event, "body", 13, ax + 40 + tw + 12, by + 22, s["muted"])[0])
    else:
        award_txt = (ts.text(title, "title", 14, ax + 40, by + 21, s["text"])[0]
                     + ts.text(event, "body", fit(event, "body", 12.5, right - ax - 48), ax + 40, by + 39, s["muted"])[0])
    body.append(f'<g>{nudge_in(0.32, 3) if animate else ""}{box(ax, by, right - ax, bh, s["soft"], 2) + cup_svg + award_txt}</g>')
    cy = by + bh + 12
    at = (lambda k: 0.38 + k * 0.05) if animate else (lambda k: None)
    body.append(chips(ts, theme, [full for _, full in p["stack"]], ax, cy, right + 2, at))
    H = int(max(cy + 22, 20 + art_box) + 16 + SHADE)
    body.insert(0, sheet(theme, W, H, f"feature{layout}"))
    alt = (f"{p['name']}, featured, private repository with a live demo: {p['line']} {p['story']} "
           f"{title} {event}. Built with {', '.join(full for _, full in p['stack'])}.")
    return svg_doc(W, H, ts.defs_svg() + printed(f"ft{layout}", W, H, body, animate, dur=0.46), alt), alt


def slug(name):
    return name.lower().replace(" ", "-")


def block():
    lead, rest = PROJECTS[0], PROJECTS[1:]
    stem = f"projects/{slug(lead['name'])}-feature"
    fsvg, falt = feature_card(lead, "light", "wide")
    hero = wide_scene(stem, f"{stem}-narrow", falt, query="v=" + stamp(fsvg))
    cells = []
    for p in rest:
        psvg, alt = project_card(p, "light")
        pic = scene(f"projects/{slug(p['name'])}", alt, CARD_W, CARD_H, query="v=" + stamp(psvg))
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
