#!/usr/bin/env python3
"""Draw the README's section headers and the CTF result cards.

Headers replace Markdown headings (and their rule lines): a bracket-key path, a
tight headline, one line of context and a two-tone pixel icon wired into a
circuit trace. A packet runs the trace and a few dots twinkle; each header also
ships a still for prefers-reduced-motion.

    python lab/build_headers.py
"""
from notebook import (ASSETS, BRAND, SHEET, THEMES, Typesetter, card, dot_grid, fade, packet, pixels, svg_doc,
                      text_width)

W, H = 840, 92
SECTIONS = [
    ("stack", "[S] /dev/stack", "Tools of the trade.", "Languages, runtimes, frameworks & instruments"),
    ("projects", "[P] /dev/projects", "Built, broken, shipped.", "Selected software, algorithms, and experiments"),
    ("live", "[L] /dev/live", "Live from the lab.", "Hourly telemetry: GitHub, LeetCode, and CTF progress"),
    ("contact", "[C] /dev/contact", "Ping me.", "Direct channels, networks, and collaborations"),
]
TRACE = "M776 38H580V64H420"


def icon_rows(kind):
    """16 × 16 two-tone pixel icons: P paper, L lavender, N neon."""
    grid = [["." for _ in range(16)] for _ in range(16)]

    def put(x, y, v):
        if 0 <= x < 16 and 0 <= y < 16:
            grid[y][x] = v

    if kind == "stack":                      # three plates, one above the other
        for top, v in ((2, "P"), (6, "L"), (10, "N")):
            for dy, (x0, x1) in enumerate(((4, 11), (2, 13), (4, 11))):
                for x in range(x0, x1 + 1):
                    put(x, top + dy, v)
    elif kind == "projects":                 # a code window: title bar, then </>
        for x in range(16):
            for y in range(1, 15):
                put(x, y, "L" if y < 4 else ("L" if x in (0, 15) or y == 14 else "."))
        for x in (2, 4, 6):
            put(x, 2, "P")
        for x, y in ((5, 6), (4, 7), (3, 8), (4, 9), (5, 10), (9, 6), (9, 7), (8, 8), (8, 9), (7, 10),
                     (10, 6), (11, 7), (12, 8), (11, 9), (10, 10)):
            put(x, y, "N" if x < 7 or x > 9 else "P")
        for x, y in ((6, 6), (6, 10), (11, 6), (11, 10)):
            put(x, y, ".")
    elif kind == "live":                     # rising bars under a pulse
        for x0, h in ((1, 4), (5, 7), (9, 10), (13, 13)):
            for x in (x0, x0 + 1):
                for y in range(15 - h, 15):
                    put(x, y, "L")
        for x, y in ((0, 6), (1, 6), (2, 5), (3, 3), (4, 6), (5, 8), (6, 6), (7, 4), (8, 1), (9, 4), (10, 6),
                     (11, 6), (12, 5), (13, 6), (14, 6), (15, 6)):
            put(x, y, "P")
    elif kind == "contact":                  # an envelope with a signal above it
        for x in range(1, 15):
            for y in range(6, 15):
                put(x, y, "L" if x in (1, 14) or y in (6, 14) else ".")
        for k in range(7):                   # the flap folds to a point
            put(1 + k, 6 + k, "P")
            put(14 - k, 6 + k, "P")
        for x, y in ((7, 1), (8, 1), (5, 2), (10, 2), (7, 3), (8, 3)):
            put(x, y, "N")
    return ["".join(r) for r in grid]


def icon_svg(key, box_x=774, box_y=14, box_size=48, scale=2.1):
    """Render a pixel icon mathematically and optically centered in its box."""
    rows = icon_rows(key)
    min_x = min(x for r in rows for x, c in enumerate(r) if c != '.')
    max_x = max(x for r in rows for x, c in enumerate(r) if c != '.')
    min_y = min(y for y, r in enumerate(rows) for c in r if c != '.')
    max_y = max(y for y, r in enumerate(rows) for c in r if c != '.')

    box_cx = box_x + box_size / 2
    box_cy = box_y + box_size / 2

    center_c = (min_x + max_x + 1) / 2
    center_r = (min_y + max_y + 1) / 2

    x = box_cx - center_c * scale
    y = box_cy - center_r * scale

    return pixels(rows, x, y, scale, {"P": BRAND["paper"], "L": BRAND["lavender"], "N": BRAND["neon"]})


def header(key, path, title, desc, theme, animate=True):
    s, b = SHEET[theme], BRAND
    ts = Typesetter("h")
    is_dark = (theme == "dark")
    out = [dot_grid(W, H, s["muted"], f"h{key}", opacity=0.18, twinkle=12 if animate else 0, focus=(776, 38, 260))]
    out.append(f'<path d="{TRACE}" fill="none" stroke="{b["neon"]}" stroke-width="1.5" stroke-dasharray="3 4"/>'
               f'<circle cx="418" cy="64" r="3" fill="{b["neon"]}"/>')
    if animate:
        out.append(packet(TRACE, s["text"], 3.2) + packet(TRACE, b["neon"], 3.2, begin=1.6))

    # Icon container: double-bezel concentric frame with mathematically centered pixel artwork
    inner_border = s["inner_edge"] if is_dark else BRAND["lavender"]
    icon_box = (f'<rect x="774" y="14" width="48" height="48" rx="8" fill="{b["ink"]}" stroke="{s["edge"]}" stroke-width="1.2"/>'
                f'<rect x="775.5" y="15.5" width="45" height="45" rx="6.5" fill="none" stroke="{inner_border}" stroke-width="1" opacity="0.35"/>'
                + icon_svg(key, 774, 14, 48, scale=2.1))
    out.append(icon_box)

    # Left typography hierarchy (always immediately legible, no opacity lag)
    path_svg = ts.text(path, "code-bold", 12.5, 2, 20, s["muted"])[0]
    size = 29
    while text_width(title, "headline", size) > 520:
        size -= 1
    title_svg = ts.text(title, "headline", size, 0, 54, s["text"])[0]
    desc_svg = ts.text(desc, "text", 13, 0, 76, s["muted"])[0]

    out += [path_svg, title_svg, desc_svg]

    # Subtle bottom hairline divider
    divider = f'<line x1="0" y1="90" x2="840" y2="90" stroke="{s["edge"]}" stroke-width="1" opacity="0.6"/>'
    out.append(divider)

    return svg_doc(W, H, ts.defs_svg() + "".join(out), title)


# CTF results, drawn as cards so they sit with the live stats
TROPHY = ["XXXXXXXXXX", "XXXXXXXXXX", "X.XXXXXX.X", "X.XXXXXX.X", ".XXXXXXXX.",
          "..XXXXXX..", "....XX....", "....XX....", "...XXXX...", "..XXXXXX.."]
WINS = [("champion", "Champion", "Mission: CTF · UP CS Guild · Sep 2026", "1st place"),
        ("hackforgov", "Top 2 student performer", "HackforGov5 Region 7 · DICT · Oct 2026", "wildcard")]
WIN_W, WIN_H = 376, 72


def win(slug, title, line, tag, theme):
    s, b = SHEET[theme], BRAND
    ts = Typesetter("w")
    tag_upper = tag.upper()
    tw = text_width(tag_upper, "code-bold", 11) + 18
    body = (card(theme, WIN_W, WIN_H, radius=8)
            + f'<g opacity="1">{fade(0.1, 0.35)}'
            + f'<rect x="12" y="12" width="48" height="48" rx="8" fill="{b["ink"]}"/>'
            + pixels(TROPHY, 21, 21, 3, {"X": b["paper"]})
            + ts.text(title, "label", 15.5, 72, 33, s["text"])[0]
            + ts.text(line, "text", 12.5, 72, 53, s["muted"])[0])
    body += (f'<rect x="{WIN_W - 14 - tw:.1f}" y="14" width="{tw:.1f}" height="20" rx="4" fill="{s["soft"]}" stroke="{s["inner_edge"]}" stroke-width="1"/>'
             + ts.text(tag_upper, "code-bold", 11, WIN_W - 14 - tw / 2, 28, s["text"], anchor="middle")[0] + "</g>")
    return svg_doc(WIN_W, WIN_H, ts.defs_svg() + body, f"{title}: {line}")


if __name__ == "__main__":
    out = ASSETS / "headers"
    out.mkdir(parents=True, exist_ok=True)
    for theme in THEMES:
        for key, path, title, desc in SECTIONS:
            (out / f"{key}-{theme}.svg").write_text(header(key, path, title, desc, theme), encoding="utf-8")
            (out / f"{key}-still-{theme}.svg").write_text(header(key, path, title, desc, theme, False), encoding="utf-8")
        for slug, title, line, tag in WINS:
            (out / f"win-{slug}-{theme}.svg").write_text(win(slug, title, line, tag, theme), encoding="utf-8")
    print(f"wrote {len(SECTIONS)} section headers and {len(WINS)} CTF cards per theme")
