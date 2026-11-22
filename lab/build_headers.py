#!/usr/bin/env python3
"""Draw the README's section headers and the trophy cards.

Headers replace Markdown headings (and their rule lines): a Pixelify index tag,
an Inter title, one line of context, a pixel rule, and a navy window on the right
where a sprite from the portfolio plays two frames. Trophy cards are torn lab
sheets. Everything that loops ships a still for prefers-reduced-motion.

    python lab/build_headers.py
"""
from notebook import (ASSETS, BRAND, PAPER, SHADE, THEMES, Typesetter, box, fit, flip, print_clip, sheet,
                      sprite_at, svg_doc, text_width)
from pixel import CHEVRON, FLASK, ORB_A, ORB_B, TESLA_A, TESLA_B, TROPHY, WAVE_A, WAVE_B

W, H = 840, 100
SECTIONS = [  # key, index, title, line
    ("projects", "01 · PROJECTS", "Experiments that shipped.", "Web tools, visualizers, a game and one prank studio."),
    ("wins", "02 · TROPHIES", "Trophy shelf.", "Hackathons and CTFs, newest first."),
    ("stack", "03 · BENCH", "Tools on the bench.", "Languages, frameworks and lab software."),
    ("live", "04 · READINGS", "Readings, every hour.", "GitHub, LeetCode and picoGym, redrawn by a bot."),
    ("contact", "05 · DOOR", "Knock on the lab door.", "Projects, internships, or a CTF team one player short."),
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


SPARKLE = ["N..........N", "............"] + [".." + r for r in TROPHY]
TROPHY_A = ["............", "............"] + [".." + r for r in TROPHY]
SPRITES = {
    "stack": (FLASK, bubbled(FLASK)),
    "projects": (TESLA_A, TESLA_B),
    "live": (ORB_A, ORB_B),
    "wins": (TROPHY_A, SPARKLE),
    "contact": (WAVE_A, WAVE_B),
}


def window(key, x, y, size, animate):
    """A navy notched window with the section's sprite centred, two frames on a beat."""
    a, b = SPRITES[key]
    rows, cols = len(a), max(len(r) for r in a)
    scale = int(min((size - 16) / cols, (size - 16) / rows) * 2) / 2
    sx, sy = x + (size - cols * scale) / 2, y + (size - rows * scale) / 2
    fa, fb = sprite_at(a, sx, sy, scale), sprite_at(b, sx, sy, scale)
    return (box(x, y, size, size, BRAND["deep"], 4) + box(x + 4, y + 4, size - 8, size - 8, BRAND["ink"], 3)
            + (flip(fa, fb, 1.0) if animate else fa))


def pixel_rule(theme, y, w):
    """A dashed rule of pixel blocks, ending in a chevron."""
    s = PAPER[theme]
    d = "".join(f"M{x} {y}h4v4h-4Z" for x in range(0, w - 24, 8))
    return (f'<path d="{d}" fill="{s["line"]}" shape-rendering="crispEdges"/>'
            + sprite_at(CHEVRON, w - 14, y - 5, 2, {"P": s["muted"]}))


def header(key, index, title, line, theme, animate=True):
    s = PAPER[theme]
    ts = Typesetter("h")
    out = []
    tw = text_width(index, "body-bold", 12, 1) + 18
    out.append(box(0, 2, tw, 22, s["soft"], 2) + ts.text(index, "body-bold", 12, 9, 17.5, s["text"], tracking=1)[0])
    size = fit(title, "title", 31, 640)
    out.append(ts.text(title, "title", size, 0, 58, s["text"])[0])
    out.append(ts.text(line, "body", 14.5, 0, 82, s["muted"])[0])
    out.append(pixel_rule(theme, H - 6, W - 104))
    out.append(window(key, W - 84, 6, 84, animate))
    return svg_doc(W, H, ts.defs_svg() + "".join(out), f"{title} {line}")


# Real results only; newest first.
WINS = [
    dict(slug="malfunction", title="Champion · Rage Quit Award", event="MALFUNCTION Hackathon 2026",
         org="iDE.A, iAcademy", when="21 NOV 2026", note="Team Dexter's Fun Club"),
    dict(slug="hackforgov", title="Top 2 student performer", event="HackforGov5 Region 7",
         org="DICT Region 7", when="OCT 2026", note="National wildcard qualifier"),
    dict(slug="champion", title="Champion", event="Mission: CTF", org="UP Computer Science Guild",
         when="SEP 2026", note="1st overall"),
]
WIN_W, WIN_H = 376, 100


def win(w, theme, animate=True):
    s = PAPER[theme]
    ts = Typesetter("w")
    a, b = SPRITES["wins"]
    fa, fb = sprite_at(a, 20, 21, 4), sprite_at(b, 20, 21, 4)
    body = [sheet(theme, WIN_W, WIN_H, w["slug"]),
            box(14, 16, 60, 60, BRAND["ink"], 3) + (flip(fa, fb, 1.4) if animate else fa)]
    right = WIN_W - SHADE - 12
    dw = text_width(w["when"], "body-bold", 11.5, 0.6)
    body.append(ts.text(w["when"], "body-bold", 11.5, right, 28, s["muted"], anchor="end", tracking=0.6)[0])
    size = fit(w["title"], "title", 16, right - dw - 10 - 88)
    body.append(ts.text(w["title"], "title", size, 88, 30, s["text"])[0])
    ev = f"{w['event']} · {w['org']}"
    body.append(ts.text(ev, "body", fit(ev, "body", 13, right - 88), 88, 51, s["muted"])[0])
    nw = text_width(w["note"], "body-bold", 11.5) + 16
    body.append(box(88, 62, nw, 22, s["chip"], 2, s["line"])
                + ts.text(w["note"], "body-bold", 11.5, 96, 77, s["text"])[0])
    inner = "".join(body)
    if animate:
        defs, clip = print_clip(f"win{w['slug']}", WIN_W, WIN_H)
        inner = f"<defs>{defs}</defs><g{clip}>{inner}</g>"
    alt = f"{w['title']}: {w['event']}, {w['org']}, {w['when'].title()}. {w['note']}."
    return svg_doc(WIN_W, WIN_H, ts.defs_svg() + inner, alt), alt


if __name__ == "__main__":
    out = ASSETS / "headers"
    out.mkdir(parents=True, exist_ok=True)
    for old in out.glob("*.svg"):
        old.unlink()
    for theme in THEMES:
        for key, index, title, line in SECTIONS:
            (out / f"{key}-{theme}.svg").write_text(header(key, index, title, line, theme), encoding="utf-8")
            (out / f"{key}-still-{theme}.svg").write_text(header(key, index, title, line, theme, False), encoding="utf-8")
        for w in WINS:
            (out / f"win-{w['slug']}-{theme}.svg").write_text(win(w, theme)[0], encoding="utf-8")
            (out / f"win-{w['slug']}-still-{theme}.svg").write_text(win(w, theme, False)[0], encoding="utf-8")
    print(f"wrote {len(SECTIONS)} section headers and {len(WINS)} trophy cards per theme")
