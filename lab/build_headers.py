#!/usr/bin/env python3
"""Draw the README's section headers and the trophy shelf.

Headers replace Markdown headings (and their rule lines): an index tag, an Inter
title, one line of context, a pixel rule, and a navy window on the right where a
sprite plays two frames. The shelf is one lab sheet with every result standing on
a plank (wide) or stacked (phones); cups glint. Everything that loops ships a
still for prefers-reduced-motion.

    python lab/build_headers.py
"""
from notebook import (ASSETS, BAYER, BRAND, PAPER, SHADE, THEMES, Typesetter, box, fit, flip, frames, nudge_in,
                      pixels, printed, sheet, sparkle, sprite_at, step_in, svg_doc, text_width)
from pixel import (CHEVRON, CUP_CTF, CUP_HACK, FLASK, MEDAL_2, MONITOR_FRAMES, TESLA_A, TESLA_B, WAVE_A, WAVE_B,
                   sheen_mask)

W, H = 840, 100
SECTIONS = [  # key, index, title, line
    ("projects", "01 Projects", "Experiments that shipped.", "Web apps, 3D visualizers, a CTF platform, and a tower defense game."),
    ("wins", "02 Trophies", "Trophy shelf.", "Recent wins and placements from hackathons and CTF competitions."),
    ("stack", "03 Bench", "Tools on the bench.", "Languages, frameworks, and tools I build and ship with."),
    ("live", "04 Readings", "Readings, every hour.", "Live progress from GitHub, LeetCode, and picoGym, updated hourly."),
    ("contact", "05 Door", "Knock on the lab door.", "Open to projects, internships, and CTF or hackathon teams."),
]


def bubbled(rows):
    """Next frame for the flask: every bubble rises one row; the top one escapes."""
    grid = [list(r) for r in rows]
    for r, row in enumerate(rows):
        for c, v in enumerate(row):
            if v == "P" and r >= 6:
                grid[r][c] = "N" if r >= 8 else "."
                grid[r - 1][c] = "P"
    return ["".join(r) for r in grid]


FLASK_B = bubbled(FLASK)
FLASK_C = bubbled(FLASK_B)


def _cup_badge_frames():
    """CUP_HACK plus 3 stepped diagonal sheen frames for the 02 Trophies header badge."""
    return [CUP_HACK] + [sheen_mask(CUP_HACK, off) for off in (7, 11, 15)]


SPRITES = {
    "stack": [FLASK, FLASK_B, FLASK_C],
    "projects": [TESLA_A, TESLA_B],
    "live": MONITOR_FRAMES,
    "wins": [CUP_HACK],
    "contact": [WAVE_A[:14], WAVE_B[:14]],   # head and shoulders: the wave reads at badge size
}


# How each section's sprite behaves: (period in seconds, frame-index sequence).
RHYTHM = {
    "projects": (2.4, [int(c) for c in "0110100011010010"]),   # the coil crackles unevenly
    "stack":    (2.4, [0, 0, 1, 1, 2, 2]),                    # bubbles climb smoothly up the flask
    "live":     (2.4, list(range(12))),                       # phosphor ECG write-head sweeps across CRT
    "contact":  (4.2, [int(c) for c in "0101010000000000"]),  # three waves, then a rest
}


def ink_box(*sprite_frames):
    """(left, top, right, bottom) of the drawn pixels across every frame, in cells."""
    cells = [(c, r) for f in sprite_frames for r, row in enumerate(f) for c, v in enumerate(row) if v != "."]
    xs, ys = [c for c, _ in cells], [r for _, r in cells]
    return min(xs), min(ys), max(xs) + 1, max(ys) + 1


def sheen_award(rows, x0, y0, scale, pal, glint_colour, animate, period=6.0, begin=1.0,
                hit=0.06, spark_cell=(13, 1), spark2_cell=None, hop=0):
    """Draw a 16×16 pixel award with a 3-step diagonal specular sheen, dual pixel rim sparkles,
    and an optional crisp 1-step celebratory lift synced to `hit` (fraction of `period`)."""
    base = pixels(rows, x0, y0, scale, pal)
    if not animate:
        return base
    sheens = []
    for idx, off in enumerate((7, 11, 15)):
        layer = pixels(sheen_mask(rows, off), x0, y0, scale, {"S": glint_colour})
        t0 = hit + idx * 0.032
        t1 = t0 + 0.032
        sheens.append(
            f'<g opacity="0"><animate attributeName="opacity" values="0;1;0" '
            f'keyTimes="0;{t0:.4f};{t1:.4f}" calcMode="discrete" dur="{period}s" '
            f'begin="{begin:.2f}s" repeatCount="indefinite"/>{layer}</g>'
        )
    sp = sparkle(x0 + spark_cell[0] * scale, y0 + spark_cell[1] * scale, scale, glint_colour,
                 period, begin + hit * period - 0.04 * period)
    if spark2_cell:
        sp += sparkle(x0 + spark2_cell[0] * scale, y0 + spark2_cell[1] * scale, max(2, scale - 1),
                      glint_colour, period, begin + (hit + 0.05) * period - 0.04 * period)
    content = base + "".join(sheens) + sp
    if hop:
        t0, t1, t2 = hit, hit + 0.032, hit + 0.096
        return (f'<g><animateTransform attributeName="transform" type="translate" '
                f'values="0 0;0 {-hop};0 {-hop};0 0" keyTimes="0;{t0:.4f};{t1:.4f};{t2:.4f}" '
                f'calcMode="discrete" dur="{period}s" begin="{begin:.2f}s" repeatCount="indefinite"/>'
                f'{content}</g>')
    return content


def window(key, x, y, size, animate):
    """A navy notched badge with the section's sprite. The sprite is centred on the pixels
    it actually draws (across all frames), at a whole-pixel scale, so it sits optically
    centred and stays crisp."""
    frame_list = SPRITES[key]
    left, top, right, bottom = ink_box(*frame_list)
    inner = size - 12
    scale = max(1, int(min(inner / (right - left), inner / (bottom - top))))
    sx = round(x + (size - (right - left) * scale) / 2 - left * scale)
    sy = round(y + (size - (bottom - top) * scale) / 2 - top * scale)
    chrome = box(x, y, size, size, BRAND["deep"], 4) + box(x + 4, y + 4, size - 8, size - 8, BRAND["ink"], 3)
    if key == "wins":
        pal = dict(P=BRAND["paper"], L=BRAND["lavender"], N=BRAND["neon"], D=BRAND["deep"])
        return chrome + sheen_award(CUP_HACK, sx, sy, scale, pal, "#ffffff", animate, period=4.8, begin=0.6)
    rendered = [sprite_at(f, sx, sy, scale) for f in frame_list]
    if not animate or len(rendered) == 1:
        return chrome + rendered[0]
    period, order = RHYTHM[key]
    return chrome + frames(rendered, period, 0.0, order)


def pixel_rule(theme, y, w, animate=False, uid="rule", pulse=False):
    """A dashed rule of pixel blocks, ending in a chevron. Animated, it draws itself in
    left to right, one block at a time, and the chevron lands last. When `pulse=True`
    (used on 04 Readings), a quiet 3-block telemetry pulse glides down the rule every 6s."""
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
    runner = ""
    chev_out = f'<g>{step_in(start + dur)}{chevron}</g>'
    if pulse and len(xs) > 6:
        steps = 22
        pxs = [xs[round(i * (len(xs) - 3) / (steps - 1))] for i in range(steps)]
        travel = 0.38
        kt = [f"{travel * i / steps:.4f}" for i in range(steps)] + [f"{travel:.4f}", "1"]
        x_vals = ";".join(str(v) for v in pxs) + f";{pxs[-1]};{pxs[0]}"
        op_vals = ";".join(["1"] * steps + ["0", "0"])
        pcol = BRAND["paper"] if theme == "dark" else BRAND["neon"]
        # 3 consecutive pixel blocks lit together
        runner = (f'<g opacity="0" shape-rendering="crispEdges">'
                  f'<animate attributeName="opacity" values="{op_vals}" keyTimes="{";".join(kt)}" '
                  f'calcMode="discrete" dur="6.0s" begin="1.1s" repeatCount="indefinite"/>'
                  f'<g><animateTransform attributeName="transform" type="translate" '
                  f'values="{";".join(f"{v} 0" for v in pxs)};{pxs[-1]} 0;{pxs[0]} 0" '
                  f'keyTimes="{";".join(kt)}" calcMode="discrete" dur="6.0s" begin="1.1s" repeatCount="indefinite"/>'
                  f'<rect x="0" y="{y}" width="4" height="4" fill="{s["led"]}" opacity="0.5"/>'
                  f'<rect x="8" y="{y}" width="4" height="4" fill="{s["led"]}"/>'
                  f'<rect x="16" y="{y}" width="4" height="4" fill="{pcol}"/></g></g>')
        chev_out = (f'<g>{step_in(start + dur)}<g>'
                    f'<animateTransform attributeName="transform" type="translate" values="0 0;3 0;0 0;0 0" '
                    f'keyTimes="0;0.37;0.43;1" calcMode="discrete" dur="6.0s" begin="1.1s" '
                    f'repeatCount="indefinite"/>{chevron}</g></g>')
    return (f'<clipPath id="{uid}"><rect x="0" y="{y - 6}" width="{w}" height="16">{anim}</rect></clipPath>'
            f'<g clip-path="url(#{uid})">{rule}</g>{runner}{chev_out}')


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
    out.append(pixel_rule(theme, H - 6, w, animate, f"rule{key}{layout[0]}", pulse=(key == "live")))
    return svg_doc(w, H, ts.defs_svg() + "".join(out), f"{title} {line}")


# Real results only; newest first.
WINS = [
    dict(slug="malfunction", award="hack", title="Champion, Rage Quit Award", event="MALFUNCTION Hackathon 2026",
         org="iDE.A iAcademy", when="21 Nov 2026", note="Team Dexter's Fun Club"),
    dict(slug="hackforgov", award="medal", title="Top 2 Student Performer", event="HackforGov5 Region 7",
         org="DICT Region 7", when="Oct 2026", note="National wildcard qualifier"),
    dict(slug="champion", award="ctf", title="Champion", event="Mission: CTF", org="UP Computer Science Guild",
         when="Sep 2026", note="1st place overall"),
]

AWARD_ART = {
    "hack":  (CUP_HACK, (13, 1), (2, 12)),
    "medal": (MEDAL_2,  (11, 5), (4, 12)),
    "ctf":   (CUP_CTF,  (13, 1), (2, 12)),
}

SHELF_PERIOD = 6.0
SHELF_BEGIN = 1.0
SHELF_HITS = (0.06, 0.21, 0.36)   # synced to the shelf-edge light runner passing under each award


def _dither_cone(cx, top_y, bot_y, half_top, half_bot, colour, opacity):
    """Subtle ordered-dither spotlight cone above each trophy, echoing the hero's hanging lamp."""
    cell, cone = 4, []
    for r, y in enumerate(range(int(top_y), int(bot_y), cell)):
        t = (y - top_y) / max(bot_y - top_y, 1)
        half = half_top + t * (half_bot - half_top)
        density = 0.34 - 0.24 * t
        for c, x in enumerate(range(round(cx - half), round(cx + half), cell)):
            if BAYER[r % 4][c % 4] < density * 16:
                cone.append(f"M{x} {y}h{cell}v{cell}h-{cell}Z")
    return f'<path d="{"".join(cone)}" fill="{colour}" opacity="{opacity}" shape-rendering="crispEdges"/>'


def _spotlight_motes(cx, floor_y, colour, seed_idx):
    """Two quiet 3px pixel motes drifting gently upward through a spotlight cone."""
    out = []
    specs = [(-38, 3.4, 0.4 + seed_idx * 0.9), (34, 4.1, 1.8 + seed_idx * 0.7)]
    for dx, dur, begin in specs:
        x = round(cx + dx)
        ys = ";".join(str(floor_y - 10 - s * 10) for s in range(7))
        out.append(
            f'<rect x="{x}" y="{floor_y - 10}" width="3" height="3" fill="{colour}" opacity="0" '
            f'shape-rendering="crispEdges">'
            f'<animate attributeName="y" values="{ys}" calcMode="discrete" dur="{dur:.1f}s" '
            f'begin="{begin:.1f}s" repeatCount="indefinite"/>'
            f'<animate attributeName="opacity" values="0;0.35;0.45;0.45;0.3;0.15;0" calcMode="discrete" '
            f'dur="{dur:.1f}s" begin="{begin:.1f}s" repeatCount="indefinite"/></rect>'
        )
    return "".join(out)


def _shelf_runner(x0, x1, y, colour, period=SHELF_PERIOD, begin=SHELF_BEGIN):
    """A crisp bright pixel sheen gliding left-to-right along the shelf's neon bevel edge,
    triggering each trophy's gleam as it passes underneath."""
    steps = 18
    w = 32
    xs = [round(x0 + (x1 - x0 - w) * i / (steps - 1)) for i in range(steps)]
    # Travel takes 0..0.46 of the cycle, then rests invisible until next sweep
    travel = 0.46
    kt = [f"{travel * i / steps:.4f}" for i in range(steps)] + [f"{travel:.4f}", "1"]
    x_vals = ";".join(str(v) for v in xs) + f";{xs[-1]};{xs[0]}"
    op_vals = ";".join(["0.85"] * steps + ["0", "0"])
    return (f'<rect x="{xs[0]}" y="{y}" width="{w}" height="3" fill="{colour}" opacity="0" '
            f'shape-rendering="crispEdges">'
            f'<animate attributeName="x" values="{x_vals}" keyTimes="{";".join(kt)}" calcMode="discrete" '
            f'dur="{period}s" begin="{begin:.2f}s" repeatCount="indefinite"/>'
            f'<animate attributeName="opacity" values="{op_vals}" keyTimes="{";".join(kt)}" calcMode="discrete" '
            f'dur="{period}s" begin="{begin:.2f}s" repeatCount="indefinite"/></rect>')


def _corbel(x, y, side, body_col, hi_col):
    """Stepped pixel L-bracket supporting the shelf plank."""
    dx_hi = 0 if side == "left" else 8
    dx_mid = 12 if side == "left" else -8
    dx_tip = 20 if side == "left" else -14
    return (f'<rect x="{x}" y="{y}" width="12" height="20" fill="{body_col}"/>'
            f'<rect x="{x + dx_hi}" y="{y}" width="4" height="20" fill="{hi_col}"/>'
            f'<rect x="{x + dx_mid}" y="{y}" width="8" height="12" fill="{body_col}"/>'
            f'<rect x="{x + dx_tip}" y="{y}" width="6" height="6" fill="{body_col}"/>')


def award(w, theme, x, floor, scale, animate, hop=4):
    """Handcrafted 16×16 cup or medallion standing on `floor`, centred on x, with stepped sheen,
    dual pixel rim sparkles, and celebratory micro-lift synced to the shelf runner."""
    s = PAPER[theme]
    pal = (dict(P=s["text"], L="#4e4ec8", N=BRAND["neon"], D=BRAND["paper"]) if theme == "light"
           else dict(P=BRAND["paper"], L="#b8b8ec", N=BRAND["neon"], D=BRAND["deep"]))
    glint_col = BRAND["paper"] if theme == "light" else "#ffffff"
    rows, spark_cell, spark2_cell = AWARD_ART[w["award"]]
    x0 = round(x - len(rows[0]) * scale / 2)
    y0 = round(floor - len(rows) * scale)
    idx = WINS.index(w)
    hit = SHELF_HITS[idx % len(SHELF_HITS)]
    return sheen_award(rows, x0, y0, scale, pal, glint_col, animate, period=SHELF_PERIOD, begin=SHELF_BEGIN,
                       hit=hit, spark_cell=spark_cell, spark2_cell=spark2_cell, hop=hop)


def shelf(theme, layout, animate=True):
    """Every result on one architectural pixel shelf: bespoke 16×16 awards, stepped corbels,
    dithered spotlights with rising motes, a shelf-edge light runner synced to each award's
    gleam + lift, date chips and clean three-tier plaques."""
    s = PAPER[theme]
    ts = Typesetter("sh")
    body, n = [], len(WINS)
    plank_col = "#1818a8" if theme == "dark" else BRAND["ink"]
    plank_bot = "#080842" if theme == "dark" else BRAND["deep"]
    hi_col = "#3a3ad4" if theme == "dark" else "#4d4de0"
    if layout == "wide":
        W, H, plank = 840, 264, 148
        col = (W - SHADE) / n
        # Subtle overhead dithered spotlights + floating light motes behind the awards
        cone_col = BRAND["lavender"] if theme == "dark" else BRAND["neon"]
        cone_op = "0.11" if theme == "dark" else "0.09"
        for k in range(n):
            cx = col * (k + 0.5)
            body.append(_dither_cone(cx, 54, plank, 18, 62, cone_col, cone_op))
            if animate:
                body.append(_spotlight_motes(cx, plank, cone_col, k))
        # Beveled shelf plank, underside shadow, stepped pixel corbel brackets, and synced light runner
        runner_col = BRAND["paper"] if theme == "dark" else "#ffffff"
        body.append(
            f'<g shape-rendering="crispEdges">'
            f'<rect x="24" y="{plank + 10}" width="{W - SHADE - 48}" height="5" fill="{plank_bot}" '
            f'opacity="{"0.8" if theme == "dark" else "0.18"}"/>'
            + _corbel(42, plank + 10, "left", BRAND["ink"], hi_col)
            + _corbel(W - SHADE - 54, plank + 10, "right", BRAND["ink"], hi_col)
            + f'<rect x="24" y="{plank}" width="{W - SHADE - 48}" height="10" fill="{plank_col}"/>'
            + f'<rect x="24" y="{plank}" width="{W - SHADE - 48}" height="3" fill="{BRAND["neon"]}"/>'
            + (_shelf_runner(24, W - SHADE - 24, plank, runner_col) if animate else "")
            + f'<rect x="24" y="{plank + 8}" width="{W - SHADE - 48}" height="2" fill="{plank_bot}"/>'
            + "".join(f'<rect x="{round(col * i)}" y="{plank + 24}" width="1" height="72" fill="{s["line"]}" '
                      f'opacity="0.5"/>' for i in range(1, n))
            + "</g>"
        )
        for k, w in enumerate(WINS):
            cx = col * (k + 0.5)
            hit = SHELF_HITS[k % len(SHELF_HITS)]
            chip_w = round(text_width(w["when"], "body-bold", 11, 0.4) + 18)
            chip = (box(round(cx - chip_w / 2), 24, chip_w, 20, s["soft"], 2)
                    + ts.text(w["when"], "body-bold", 11, cx, 38, s["muted"], anchor="middle", tracking=0.4)[0])
            # Contact shadow tightens briefly while the trophy lifts!
            if animate:
                t0, t1, t2 = hit, hit + 0.032, hit + 0.096
                contact = (f'<rect x="{round(cx - 28)}" y="{plank}" width="56" height="3" fill="{plank_bot}" '
                           f'opacity="0.55" shape-rendering="crispEdges">'
                           f'<animate attributeName="opacity" values="0.55;0.25;0.25;0.55" '
                           f'keyTimes="0;{t0:.4f};{t1:.4f};{t2:.4f}" calcMode="discrete" dur="{SHELF_PERIOD}s" '
                           f'begin="{SHELF_BEGIN:.2f}s" repeatCount="indefinite"/></rect>')
            else:
                contact = (f'<rect x="{round(cx - 28)}" y="{plank}" width="56" height="3" fill="{plank_bot}" '
                           f'opacity="0.55" shape-rendering="crispEdges"/>')
            sub = f"{w['org']}, {w['note']}"
            item = (chip + contact + award(w, theme, cx, plank, 4, animate, hop=4)
                    + ts.text(w["title"], "title", fit(w["title"], "title", 15.5, col - 24), cx, 192, s["text"],
                              anchor="middle")[0]
                    + ts.text(w["event"], "body-bold", fit(w["event"], "body-bold", 12.5, col - 22), cx, 213,
                              s["muted"], anchor="middle")[0]
                    + ts.text(sub, "body", fit(sub, "body", 11.5, col - 20), cx, 232, s["muted"],
                              anchor="middle", opacity="0.85")[0])
            body.append(f'<g>{nudge_in(0.34 + k * 0.10, 4) if animate else ""}{item}</g>')
    else:
        W, pitch = 400, 96
        H = 24 + n * pitch
        right = W - SHADE - 14
        for k, w in enumerate(WINS):
            y = 18 + k * pitch
            floor = y + 66
            sub = f"{w['org']}, {w['when']}"
            item = (f'<g shape-rendering="crispEdges">'
                    f'<rect x="16" y="{floor}" width="64" height="6" fill="{plank_col}"/>'
                    f'<rect x="16" y="{floor}" width="64" height="2" fill="{BRAND["neon"]}"/></g>'
                    + award(w, theme, 48, floor, 3, animate, hop=3)
                    + ts.text(w["title"], "title", fit(w["title"], "title", 15, right - 96), 96, y + 22, s["text"])[0]
                    + ts.text(w["event"], "body-bold", fit(w["event"], "body-bold", 12.5, right - 96), 96, y + 41,
                              s["muted"])[0]
                    + ts.text(sub, "body", fit(sub, "body", 11.5, right - 96), 96, y + 58, s["muted"], opacity="0.85")[0]
                    + ts.text(w["note"], "body-bold", fit(w["note"], "body-bold", 11.5, right - 96), 96, y + 75,
                              s["led"])[0])
            body.append(f'<g>{nudge_in(0.34 + k * 0.10, 4) if animate else ""}{item}</g>')
    body.insert(0, sheet(theme, W, H, f"shelf{layout}"))
    alt = "Trophy shelf. " + " ".join(f"{w['title']}: {w['event']}, {w['org']}, {w['when']}. {w['note']}." for w in WINS)
    return svg_doc(W, H, ts.defs_svg() + printed(f"shelf{layout}", W, H, body, animate, dur=0.46), alt), alt


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
