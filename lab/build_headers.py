#!/usr/bin/env python3
"""Draw the README's section headers and the trophy shelf.

Headers replace Markdown headings (and their rule lines): an index tag, an Inter
title, one line of context, a pixel rule, and a navy window on the right where a
sprite plays two frames. The shelf is one lab sheet with every result standing on
a plank (wide) or stacked (phones); cups glint. Everything that loops ships a
still for prefers-reduced-motion.

    python lab/build_headers.py
"""
from notebook import (ASSETS, BRAND, PAPER, SHADE, THEMES, Typesetter, box, fit, flip, print_clip, sheet,
                      sprite_at, step_in, svg_doc, text_width)
from pixel import (CHEVRON, FLASK, MEDAL, MONITOR_A, MONITOR_B, TESLA_A, TESLA_B, TROPHY, TROPHY_GLINT, WAVE_A,
                   WAVE_B)

W, H = 840, 100
SECTIONS = [  # key, index, title, line
    ("projects", "01 Projects", "Experiments that shipped.", "Web apps, 3D visualizers, a CTF platform, and a tower defense game."),
    ("wins", "02 Trophies", "Trophy shelf.", "Recent wins and placements from hackathons and CTF competitions."),
    ("stack", "03 Bench", "Tools on the bench.", "Languages, frameworks, and tools I build and ship with."),
    ("live", "04 Readings", "Readings, every hour.", "Live progress from GitHub, LeetCode, and picoGym, updated hourly."),
    ("contact", "05 Door", "Knock on the lab door.", "Open to projects, internships, and CTF or hackathon teams."),
]


def bubbled(rows):
    """Second frame for the flask: every bubble rises one row; the top one escapes."""
    grid = [list(r) for r in rows]
    for r, row in enumerate(rows):
        for c, v in enumerate(row):
            if v == "P" and r >= 6:
                grid[r][c] = "N" if r >= 8 else "."
                grid[r - 1][c] = "P"
    return ["".join(r) for r in grid]


SPRITES = {
    "stack": (FLASK, bubbled(FLASK)),
    "projects": (TESLA_A, TESLA_B),
    "live": (MONITOR_A, MONITOR_B),
    "wins": (TROPHY, TROPHY_GLINT),
    "contact": (WAVE_A[:14], WAVE_B[:14]),   # head and shoulders: the wave reads at badge size
}


# How each section's sprite behaves: (period in seconds, rhythm of its two frames).
RHYTHM = {
    "projects": (2.4, "0110100011010010"),   # the coil crackles unevenly
    "wins": (4.8, "000000000100"),           # the cup glints once in a while
    "stack": (2.0, "00001111"),              # the flask's bubbles rise and settle
    "live": (2.0, "01"),                     # the trace scrolls across the monitor
    "contact": (4.2, "0101010000000000"),    # three waves, then a rest
}


def ink_box(*frames):
    """(left, top, right, bottom) of the drawn pixels across every frame, in cells."""
    cells = [(c, r) for f in frames for r, row in enumerate(f) for c, v in enumerate(row) if v != "."]
    xs, ys = [c for c, _ in cells], [r for _, r in cells]
    return min(xs), min(ys), max(xs) + 1, max(ys) + 1


def window(key, x, y, size, animate):
    """A navy notched badge with the section's sprite. The sprite is centred on the pixels
    it actually draws (across both frames), at a whole-pixel scale, so it sits optically
    centred and stays crisp."""
    a, b = SPRITES[key]
    left, top, right, bottom = ink_box(a, b)
    inner = size - 12
    scale = max(1, int(min(inner / (right - left), inner / (bottom - top))))
    sx = round(x + (size - (right - left) * scale) / 2 - left * scale)
    sy = round(y + (size - (bottom - top) * scale) / 2 - top * scale)
    fa, fb = sprite_at(a, sx, sy, scale), sprite_at(b, sx, sy, scale)
    return (box(x, y, size, size, BRAND["deep"], 4) + box(x + 4, y + 4, size - 8, size - 8, BRAND["ink"], 3)
            + (flip(fa, fb, *RHYTHM[key]) if animate else fa))


def pixel_rule(theme, y, w, animate=False, uid="rule"):
    """A dashed rule of pixel blocks, ending in a chevron. Animated, it draws itself in
    left to right, one block at a time, and the chevron lands last."""
    s = PAPER[theme]
    xs = list(range(0, w - 24, 8))
    d = "".join(f"M{x} {y}h4v4h-4Z" for x in xs)
    rule = f'<path d="{d}" fill="{s["line"]}" shape-rendering="crispEdges"/>'
    chevron = sprite_at(CHEVRON, w - 14, y - 5, 2, {"P": s["muted"]})
    if not animate:
        return rule + chevron
    start, dur = 0.3, 0.6
    total = start + dur + 0.01
    widths = [0] + [x + 8 for x in xs]
    times = [0] + [(start + dur * i / len(xs)) / total for i in range(len(xs))]
    anim = (f'<animate attributeName="width" values="{";".join(str(v) for v in widths)}" '
            f'keyTimes="{";".join(f"{t:.4f}" for t in times)}" calcMode="discrete" dur="{total:.2f}s" fill="freeze"/>')
    return (f'<clipPath id="{uid}"><rect x="0" y="{y - 6}" width="{w}" height="16">{anim}</rect></clipPath>'
            f'<g clip-path="url(#{uid})">{rule}</g><g>{step_in(start + dur)}{chevron}</g>')


def header(key, index, title, line, theme, animate=True, layout="wide"):
    """The section's badge leads the heading: badge on the left, centred on the tag, title and
    line beside it, and the pixel rule running under both. layout="narrow" is the phone version."""
    s = PAPER[theme]
    ts = Typesetter("h")
    w, badge = (W, 68) if layout == "wide" else (400, 56)
    tx = badge + 18
    room = w - tx - 8
    out = [window(key, 0, (84 - badge) / 2 + 2, badge, animate)]
    tw = text_width(index, "body-bold", 12, 1) + 18
    out.append(box(tx, 4, tw, 22, s["soft"], 2) + ts.text(index, "body-bold", 12, tx + 9, 19.5, s["text"], tracking=1)[0])
    out.append(ts.text(title, "title", fit(title, "title", 31 if layout == "wide" else 23, room), tx, 58, s["text"])[0])
    out.append(ts.text(line, "body", fit(line, "body", 14.5 if layout == "wide" else 12.5, room), tx, 80, s["muted"])[0])
    out.append(pixel_rule(theme, H - 6, w, animate, f"rule{key}{layout[0]}"))
    return svg_doc(w, H, ts.defs_svg() + "".join(out), f"{title} {line}")


# Real results only; newest first.
WINS = [
    dict(slug="malfunction", award="trophy", title="Champion, Rage Quit Award", event="MALFUNCTION Hackathon 2026",
         org="iDE.A iAcademy", when="21 Nov 2026", note="Team Dexter's Fun Club"),
    dict(slug="hackforgov", award="medal", title="Top 2 Student Performer", event="HackforGov5 Region 7",
         org="DICT Region 7", when="Oct 2026", note="National wildcard qualifier"),
    dict(slug="champion", award="trophy", title="Champion", event="Mission: CTF", org="UP Computer Science Guild",
         when="Sep 2026", note="1st place overall"),
]


def award(w, theme, x, floor, scale, animate):
    """The cup or medal, standing on `floor`, centred on x. Trophies glint."""
    s = PAPER[theme]
    ink = dict(P=s["text"], N=s["text"], L=s["muted"]) if theme == "light" else None
    rows, glint = (TROPHY, TROPHY_GLINT) if w["award"] == "trophy" else (MEDAL, None)
    cols = len(rows[0])
    x0, y0 = x - cols * scale / 2, floor - len(rows) * scale
    a = sprite_at(rows, x0, y0, scale, ink)
    if glint is None or not animate:
        return a
    b = sprite_at(glint, x0, y0, scale, dict(ink, L=BRAND["neon"]) if ink else None)
    return flip(a, b, 4.8, 0.9 + 1.3 * WINS.index(w), rhythm="000000000100")


def shelf(theme, layout, animate=True):
    """Every result on one shelf: cups and the medal stand on a plank, labelled underneath."""
    s = PAPER[theme]
    ts = Typesetter("sh")
    body, n = [], len(WINS)
    if layout == "wide":
        W, H, plank = 840, 252, 150
        col = (W - SHADE) / n
        body.append(f'<g shape-rendering="crispEdges">'
                    f'<rect x="28" y="{plank}" width="{W - SHADE - 56}" height="10" fill="{BRAND["ink"]}"/>'
                    f'<rect x="28" y="{plank}" width="{W - SHADE - 56}" height="3" fill="{BRAND["neon"]}"/>'
                    + "".join(f'<rect x="{bx}" y="{plank + 10}" width="10" height="14" fill="{BRAND["ink"]}"/>'
                              for bx in (70, W - SHADE - 80)) + "</g>")
        for k, w in enumerate(WINS):
            cx = col * (k + 0.5)
            item = (ts.text(w["when"], "body-bold", 12, cx, 40, s["muted"], anchor="middle", tracking=0.4)[0]
                    + award(w, theme, cx, plank, 7 if w["award"] == "trophy" else 6, animate)
                    + ts.text(w["title"], "title", fit(w["title"], "title", 15.5, col - 24), cx, 194, s["text"],
                              anchor="middle")[0]
                    + ts.text(f"{w['event']}, {w['org']}", "body",
                              fit(f"{w['event']}, {w['org']}", "body", 12.5, col - 20), cx, 214, s["muted"],
                              anchor="middle")[0]
                    + ts.text(w["note"], "body-bold", 12, cx, 233, s["text"], anchor="middle")[0])
            body.append(f'<g>{step_in(0.8 + k * 0.15) if animate else ""}{item}</g>')
    else:
        W, pitch = 400, 92
        H = 20 + n * pitch
        right = W - SHADE - 14
        for k, w in enumerate(WINS):
            y = 16 + k * pitch
            floor = y + 62
            item = (f'<rect x="16" y="{floor}" width="64" height="6" fill="{BRAND["ink"]}" shape-rendering="crispEdges"/>'
                    + award(w, theme, 48, floor, 5 if w["award"] == "trophy" else 4, animate)
                    + ts.text(w["title"], "title", fit(w["title"], "title", 15, right - 96), 96, y + 22, s["text"])[0]
                    + ts.text(f"{w['event']}, {w['org']}", "body",
                              fit(f"{w['event']}, {w['org']}", "body", 12.5, right - 96), 96, y + 42, s["muted"])[0]
                    + ts.text(f"{w['note']}, {w['when']}", "body-bold", 12, 96, y + 62, s["text"])[0])
            body.append(f'<g>{step_in(0.8 + k * 0.15) if animate else ""}{item}</g>')
    body.insert(0, sheet(theme, W, H, f"shelf{layout}"))
    inner = "".join(body)
    if animate:
        defs, clip = print_clip(f"shelf{layout}", W, H, steps=12, dur=0.7)
        inner = f"<defs>{defs}</defs><g{clip}>{inner}</g>"
    alt = "Trophy shelf. " + " ".join(f"{w['title']}: {w['event']}, {w['org']}, {w['when']}. {w['note']}." for w in WINS)
    return svg_doc(W, H, ts.defs_svg() + inner, alt), alt


if __name__ == "__main__":
    out = ASSETS / "headers"
    out.mkdir(parents=True, exist_ok=True)
    for old in out.glob("*.svg"):
        old.unlink()
    for theme in THEMES:
        for key, index, title, line in SECTIONS:
            (out / f"{key}-{theme}.svg").write_text(header(key, index, title, line, theme), encoding="utf-8")
            (out / f"{key}-still-{theme}.svg").write_text(header(key, index, title, line, theme, False), encoding="utf-8")
            (out / f"{key}-narrow-{theme}.svg").write_text(header(key, index, title, line, theme, True, "narrow"),
                                                           encoding="utf-8")
            (out / f"{key}-narrow-still-{theme}.svg").write_text(
                header(key, index, title, line, theme, False, "narrow"), encoding="utf-8")
        for layout, stem in (("wide", "shelf"), ("narrow", "shelf-narrow")):
            (out / f"{stem}-{theme}.svg").write_text(shelf(theme, layout)[0], encoding="utf-8")
            (out / f"{stem}-still-{theme}.svg").write_text(shelf(theme, layout, False)[0], encoding="utf-8")
    print(f"wrote {len(SECTIONS)} section headers and the trophy shelf per theme")
