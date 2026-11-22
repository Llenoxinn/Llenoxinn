#!/usr/bin/env python3
"""Build the profile hero and the contact cards.

The hero is the portfolio's lab at night, drawn in pixels: LED cabinets that
blink in steps, a checker floor, the pixel scientist waving next to a sparking
Tesla coil, and the dexterslab wordmark. Its bottom edge tears into the page.
It comes wide and narrow (phones), each animated and still; <picture> picks one.
"""
import random

from notebook import (ASSETS, BRAND, PAPER, SHADE, THEMES, Typesetter, blink, box, flip, mark, nudge_in,
                      printed, scan_reveal_x, sheet, sprite_at, svg_doc, text_width, torn_path)
from pixel import CHEVRON, FLASK, TESLA_A, TESLA_B, TUBES, WAVE_A, WAVE_B

WORDMARK = "dexterslab"
TAGLINE = "Let the code begin."
WHO = "I'm Dexter, a computer science student at UP Cebu."
BUTTON = "Open the portfolio"
NIGHT = dict(wall="#0b0b52", cabinet="#15156c", seam="#2626a0", floor_a="#14149a", floor_b="#0f0f7c",
             leds=["#ff7eb6", "#5ce1e6", "#ffd166", BRAND["lavender"], BRAND["neon"]])

LAYOUTS = {
    "wide": dict(w=840, h=340, floor=284, text_x=48, word=74, word_y=126, tag=24, tag_y=170,
                 who=15, who_y=200, btn_y=222, dexter=(620, 6), tesla=(730, 5),
                 bench=(496, 238, 116, 3), window=(694, 40, 96, 72),
                 cabinets=[(0, 40, 36, 244), (800, 40, 40, 244)], centre=False),
    "narrow": dict(w=400, h=380, floor=168, text_x=200, word=52, word_y=236, tag=19, tag_y=270,
                   who=13.5, who_y=298, btn_y=318, dexter=(150, 5), tesla=(250, 4),
                   bench=(52, 128, 86, 2), window=(292, 28, 66, 50),
                   cabinets=[(0, 20, 28, 148), (372, 20, 28, 148)], centre=True),
}
NIGHT.update(pipe="#1b1b7e", pipe_hi="#2e2eaa", sky="#05052e", shadow="#07073f", glow=BRAND["lavender"],
             bench="#1d1d86", bench_top="#3434b8")


def cabinet(x, y, w, h, seed, animate):
    """A wall of lab equipment: a notched cabinet with a grid of LEDs, a few blinking out of step."""
    rng = random.Random(seed)
    out = [box(x, y, w, h, NIGHT["cabinet"], 4, NIGHT["seam"])]
    for ly in range(y + 12, y + h - 10, 14):
        for lx in range(x + 8, x + w - 8, 10):
            if rng.random() < 0.55:
                led = f'<rect x="{lx}" y="{ly}" width="5" height="5" fill="{rng.choice(NIGHT["leds"])}"'
                if animate and rng.random() < 0.3:
                    led += f'>{blink(rng.choice((0.8, 1.2, 1.6, 2.4)), rng.uniform(0, 2), 0.5, 0.15)}</rect>'
                else:
                    led += f' opacity="{rng.choice((0.55, 0.8, 1))}"/>'
                out.append(led)
    return f'<g shape-rendering="crispEdges">{"".join(out)}</g>'


def floor(y, w, h):
    d_a, d_b = [], []
    size = 16
    for row, fy in enumerate(range(y, h, size)):
        for col, fx in enumerate(range(0, w, size)):
            (d_a if (row + col) % 2 else d_b).append(f"M{fx} {fy}h{size}v{size}h-{size}Z")
    return (f'<g shape-rendering="crispEdges"><path d="{"".join(d_a)}" fill="{NIGHT["floor_a"]}"/>'
            f'<path d="{"".join(d_b)}" fill="{NIGHT["floor_b"]}"/>'
            f'<rect x="0" y="{y}" width="{w}" height="3" fill="{BRAND["neon"]}" opacity="0.6"/></g>')


def crisp(*parts):
    return f'<g shape-rendering="crispEdges">{"".join(parts)}</g>'


def pipe(w, y):
    """A ceiling pipe across the room, with a collar every few metres."""
    collars = "".join(f'<rect x="{x}" y="{y - 2}" width="8" height="10" fill="{NIGHT["pipe_hi"]}"/>'
                      for x in range(60, w, 140))
    return crisp(f'<rect x="0" y="{y}" width="{w}" height="6" fill="{NIGHT["pipe"]}"/>',
                 f'<rect x="0" y="{y}" width="{w}" height="2" fill="{NIGHT["pipe_hi"]}"/>', collars)


def window(x, y, w, h, seed, animate):
    """A high window onto the night: a pixel moon and stars that twinkle at their own pace."""
    rng = random.Random(seed)
    out = [box(x - 4, y - 4, w + 8, h + 8, NIGHT["cabinet"], 3, NIGHT["seam"]),
           f'<rect x="{x}" y="{y}" width="{w}" height="{h}" fill="{NIGHT["sky"]}"/>']
    mx, my, r = x + w * 0.72, y + h * 0.34, max(5, h // 9)
    moon = "".join(f"M{mx + dx * 2:.0f} {my + dy * 2:.0f}h2v2h-2Z"
                   for dx in range(-r, r) for dy in range(-r, r)
                   if dx * dx + dy * dy < r * r and (dx + r * 0.45) ** 2 + (dy - r * 0.2) ** 2 >= (r * 0.8) ** 2)
    out.append(f'<path d="{moon}" fill="{BRAND["paper"]}"/>')
    for _ in range(9):
        sx, sy = x + rng.randrange(4, w - 6, 2), y + rng.randrange(4, h - 6, 2)
        if abs(sx - mx) < r * 2.6 and abs(sy - my) < r * 2.6:
            continue
        size = rng.choice((2, 2, 3))
        twinkle = blink(rng.uniform(2.6, 5.0), rng.uniform(0, 3), rhythm=rng.choice(
            ("1111110111", "1101111111", "1111111011"))) if animate else ""
        out.append(f'<rect x="{sx}" y="{sy}" width="{size}" height="{size}" fill="{BRAND["lavender"]}">{twinkle}</rect>')
    # mullions: the window is two panes by two
    out.append(f'<rect x="{x + w // 2 - 2}" y="{y}" width="4" height="{h}" fill="{NIGHT["cabinet"]}"/>'
               f'<rect x="{x}" y="{y + h // 2 - 2}" width="{w}" height="4" fill="{NIGHT["cabinet"]}"/>')
    return crisp(*out)


def lamp(cx, top, floor_y, spread, seed):
    """A hanging lamp and its cone of light, drawn as an ordered dither that thins toward the floor."""
    from notebook import BAYER
    shade_y = top + 24
    out = [f'<rect x="{cx - 1}" y="{top}" width="2" height="24" fill="{NIGHT["pipe_hi"]}"/>',
           f'<path d="M{cx - 10} {shade_y}h20v4h6v6h-32v-6h6Z" fill="{NIGHT["pipe_hi"]}"/>',
           f'<rect x="{cx - 6}" y="{shade_y + 10}" width="12" height="3" fill="{BRAND["paper"]}"/>']
    cell, cone = 4, []
    y0 = shade_y + 14
    for r, y in enumerate(range(y0, floor_y, cell)):
        depth = (y - y0) / max(floor_y - y0, 1)
        half = 14 + depth * spread
        density = 0.42 - 0.30 * depth
        for c, x in enumerate(range(int(cx - half), int(cx + half), cell)):
            if BAYER[r % 4][c % 4] < density * 16:
                cone.append(f"M{x} {y}h{cell}v{cell}h-{cell}Z")
    out.append(f'<path d="{"".join(cone)}" fill="{NIGHT["glow"]}" opacity="0.16"/>')
    return crisp(*out)


def pool(cx, floor_y, half):
    """The lamp's light on the floor: stepped rows, widest nearest the viewer."""
    rows = "".join(f'<rect x="{cx - half + k * 6}" y="{floor_y + 3 + k * 4}" width="{2 * half - k * 12}" height="4"/>'
                   for k in range(4))
    return crisp(f'<g fill="{NIGHT["glow"]}" opacity="0.12">{rows}</g>')


def shadow(cx, floor_y, half):
    return crisp(f'<rect x="{cx - half}" y="{floor_y + 3}" width="{2 * half}" height="4" fill="{NIGHT["shadow"]}"/>',
                 f'<rect x="{cx - half + 6}" y="{floor_y + 7}" width="{2 * half - 12}" height="3" fill="{NIGHT["shadow"]}"/>')


def bench(x, top, w, scale, floor_y, animate):
    """A lab bench holding a rack of tubes and the flask; bubbles climb out of the flask now and then."""
    out = [f'<rect x="{x}" y="{top}" width="{w}" height="6" fill="{NIGHT["bench"]}"/>',
           f'<rect x="{x}" y="{top}" width="{w}" height="2" fill="{NIGHT["bench_top"]}"/>',
           f'<rect x="{x + 6}" y="{top + 6}" width="5" height="{floor_y - top - 6}" fill="{NIGHT["bench"]}"/>',
           f'<rect x="{x + w - 11}" y="{top + 6}" width="5" height="{floor_y - top - 6}" fill="{NIGHT["bench"]}"/>']
    fx = x + 6
    out.append(sprite_at(FLASK, fx, top - len(FLASK) * scale, scale))
    rx = x + w - len(TUBES[0]) * (scale - 1) - 6
    out.append(sprite_at(TUBES, rx, top - len(TUBES) * (scale - 1), scale - 1))
    if animate:     # three bubbles leave the neck one after another, stepping up as they go
        neck_x, neck_y = fx + 5 * scale, top - len(FLASK) * scale
        for k in range(3):
            ys = ";".join(f"{neck_y - 4 - s * 2 * scale}" for s in range(6))
            out.append(f'<rect x="{neck_x + (k % 2) * scale}" y="{neck_y}" width="{scale}" height="{scale}" '
                       f'fill="{BRAND["lavender"]}" opacity="0">'
                       f'<animate attributeName="y" values="{ys}" calcMode="discrete" dur="1.8s" begin="{k * 0.6}s" '
                       f'repeatCount="indefinite"/>'
                       f'<animate attributeName="opacity" values="0;0.9;0.9;0.9;0.6;0" calcMode="discrete" dur="1.8s" '
                       f'begin="{k * 0.6}s" repeatCount="indefinite"/></rect>')
    return crisp(*out), fx + len(FLASK[0]) * scale / 2


def arc(x0, y0, x1, y1, seed, W, H, animate):
    """Now and then the coil throws a bolt at the cabinet, and the room flashes."""
    if not animate:
        return ""
    rng = random.Random(seed)
    steps, pts = 7, []
    for i in range(steps + 1):
        t = i / steps
        jitter = 0 if i in (0, steps) else rng.randint(-8, 8)
        pts.append((round(x0 + (x1 - x0) * t), round(y0 + (y1 - y0) * t + jitter)))
    cells = []
    for (ax, ay), (bx, by) in zip(pts, pts[1:]):
        n = max(abs(bx - ax), abs(by - ay)) // 2 or 1
        for i in range(n + 1):
            cells.append(f"M{round(ax + (bx - ax) * i / n)} {round(ay + (by - ay) * i / n)}h3v3h-3Z")
    rhythm = "000000001010000000000100"
    on = blink(4.8, 0.9, rhythm=rhythm)
    return (f'<g opacity="0">{on}<path d="{"".join(cells)}" fill="{BRAND["paper"]}" shape-rendering="crispEdges"/>'
            f'<rect width="{W}" height="{H}" fill="{BRAND["lavender"]}" opacity="0.05"/></g>')


def banner(theme, animate=True, layout="wide"):
    L, b = LAYOUTS[layout], BRAND
    W, H = L["w"], L["h"]
    ts = Typesetter(f"hero{layout[0]}")
    at = (lambda t: t) if animate else (lambda t: None)
    fl = L["floor"]
    dx, ds = L["dexter"]
    tx, tsz = L["tesla"]
    dexter_cx = dx + 8 * ds
    coil_cx, coil_top = tx + 6 * tsz, fl - len(TESLA_A) * tsz
    pipe_y = 12 if layout == "wide" else 8

    # back to front: wall, pipe, window, cabinets, lamp light, floor, shadows, then the actors
    out = [f'<rect width="{W}" height="{H}" fill="{NIGHT["wall"]}"/>',
           crisp(*(f'<rect x="0" y="{y}" width="{W}" height="1" fill="{NIGHT["cabinet"]}"/>'
                   for y in range(pipe_y + 40, fl, 56))),           # faint wall panel seams
           pipe(W, pipe_y), window(*L["window"], f"win{layout}", animate)]
    for k, c in enumerate(L["cabinets"]):
        out.append(cabinet(*c, f"{layout}{k}", animate))
    out.append(lamp(dexter_cx, pipe_y + 6, fl, 70 if layout == "wide" else 44, layout))
    out.append(floor(fl, W, H))
    out.append(pool(dexter_cx, fl, 60 if layout == "wide" else 40))
    out.append(shadow(dexter_cx, fl, 5 * ds) + shadow(coil_cx, fl, 4 * tsz))
    bx, btop, bw, bscale = L["bench"]
    out.append(shadow(bx + bw / 2, fl, bw / 2))
    bench_svg, _ = bench(bx, btop, bw, bscale + 1, fl, animate)
    out.append(bench_svg)

    wa, wb = sprite_at(WAVE_A, dx, fl - len(WAVE_A) * ds, ds), sprite_at(WAVE_B, dx, fl - len(WAVE_B) * ds, ds)
    out.append(flip(wa, wb, 4.2, 0.6, rhythm="0101010000000000") if animate else wa)
    ta = sprite_at(TESLA_A, tx, coil_top, tsz)
    tb = sprite_at(TESLA_B, tx, coil_top, tsz)
    out.append(flip(ta, tb, 2.4, 0, rhythm="0110100011010010") if animate else ta)
    cab_x = L["cabinets"][1][0]
    out.append(arc(coil_cx, coil_top + 2 * tsz, cab_x + 2, coil_top - 10, layout, W, H, animate))

    # the words
    x, anchor = L["text_x"], ("middle" if L["centre"] else "start")
    word = (ts.text(WORDMARK, "pixel", L["word"], x + 4, L["word_y"] + 4, b["neon"], anchor=anchor)[0]
            + ts.text(WORDMARK, "pixel", L["word"], x, L["word_y"], b["paper"], anchor=anchor)[0])
    if animate:      # horizontal phosphor scanline sweeps across the wordmark left-to-right
        ww = text_width(WORDMARK, "pixel", L["word"]) + 10
        wx = x - ww / 2 if L["centre"] else x - 2
        wh = L["word"] * 1.05
        out.append(scan_reveal_x(f"word{layout[0]}", wx, L["word_y"] - wh + 14, ww, wh, word, 0.12, 0.44))
    else:
        out.append(word)
    out.append(f'<g>{nudge_in(at(0.42), 4)}'
               + ts.text(TAGLINE, "title", L["tag"], x, L["tag_y"], b["lavender"], anchor=anchor)[0] + "</g>")
    out.append(f'<g>{nudge_in(at(0.54), 3)}'
               + ts.text(WHO, "body", L["who"], x, L["who_y"], b["paper"], anchor=anchor)[0] + "</g>")
    bw = text_width(BUTTON, "body-bold", 14) + 52
    bx = x - bw / 2 if L["centre"] else x
    by = L["btn_y"]
    chev = sprite_at(CHEVRON, bx + bw - 26, by + 11, 2, {"P": b["ink"]})
    if animate:
        chev = (f'<g><animateTransform attributeName="transform" type="translate" values="0 0;3 0;0 0;0 0" '
                f'keyTimes="0;0.10;0.20;1" calcMode="discrete" dur="2.8s" begin="1.2s" repeatCount="indefinite"/>{chev}</g>')
    out.append(f'<g>{nudge_in(at(0.66), 4)}'
               + box(bx + 4, by + 4, bw, 36, b["neon"], 3) + box(bx, by, bw, 36, b["paper"], 3)
               + ts.text(BUTTON, "body-bold", 14, bx + 16, by + 23, b["ink"])[0] + chev + "</g>")

    # the bottom edge tears into the page, as the portfolio's sheets do
    page = PAPER[theme]["page"]
    tear = torn_path(W, 12, f"hero{layout}", top=True, bottom=False)
    out.append(f'<path transform="translate(0 {H - 10})" d="{tear}" fill="{page}" shape-rendering="crispEdges"/>')
    return svg_doc(W, H, ts.defs_svg() + "".join(out),
                   f"{WORDMARK}: {TAGLINE} {WHO} Open the portfolio.")


CONTACTS = [("linkedin", "LinkedIn", "linkedin.com/in/dsjuevesano"),
            ("github", "GitHub", "github.com/Llenoxinn")]
CONTACT_W, CONTACT_H = 376, 92


def contact(key, label, url, theme, animate=True):
    s = PAPER[theme]
    ts = Typesetter("ct")
    right = CONTACT_W - SHADE - 14
    # the arrow's button: centred on the network icon's row, the chevron centred on its drawn pixels
    bs, by = 32, 14 + 30 - 16
    bx = right - bs
    cols = max(r.rstrip(".").__len__() for r in CHEVRON)          # drawn width in cells (5 of 7)
    cx = bx + (bs - cols * 2) / 2
    cy = by + (bs - len(CHEVRON) * 2) / 2
    chev = sprite_at(CHEVRON, cx, cy, 2, {"P": s["text"]})
    if animate:     # a small nudge toward the link now and then, from the centred rest position
        chev = (f'<g><animateTransform attributeName="transform" type="translate" values="0 0;2 0;0 0;0 0" '
                f'keyTimes="0;0.1;0.2;1" calcMode="discrete" dur="2.4s" begin="1s" repeatCount="indefinite"/>{chev}</g>')
    body = [sheet(theme, CONTACT_W, CONTACT_H, key),
            f'<g>{nudge_in(0.14, 4) if animate else ""}{box(14, 14, 60, 60, BRAND["ink"], 3) + mark(key, 28, 28, 32, BRAND["paper"])}</g>',
            f'<g>{nudge_in(0.22, 3) if animate else ""}'
            + ts.text(label, "title", 18, 88, 40, s["text"])[0]
            + ts.text(url, "body", 13, 88, 61, s["muted"])[0] + '</g>',
            f'<g>{nudge_in(0.28, 3) if animate else ""}{box(bx, by, bs, bs, s["soft"], 2) + chev}</g>']
    return svg_doc(CONTACT_W, CONTACT_H, ts.defs_svg() + printed(f"ct{key}", CONTACT_W, CONTACT_H, body, animate, dur=0.38), f"{label}: {url}")


if __name__ == "__main__":
    for theme in THEMES:
        for layout, stem in (("wide", "banner"), ("narrow", "banner-narrow")):
            (ASSETS / f"{stem}-{theme}.svg").write_text(banner(theme, True, layout), encoding="utf-8")
            (ASSETS / f"{stem}-still-{theme}.svg").write_text(banner(theme, False, layout), encoding="utf-8")
        for key, label, url in CONTACTS:
            (ASSETS / f"contact-{key}-{theme}.svg").write_text(contact(key, label, url, theme), encoding="utf-8")
            (ASSETS / f"contact-{key}-still-{theme}.svg").write_text(contact(key, label, url, theme, False),
                                                                    encoding="utf-8")
    print("wrote the wide and narrow hero, their stills and the contact cards")
