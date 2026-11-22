#!/usr/bin/env python3
"""Build the profile hero and the contact cards.

The hero is the portfolio's lab at night, drawn in pixels: LED cabinets that
blink in steps, a checker floor, the pixel scientist waving next to a sparking
Tesla coil, and the dexterslab wordmark. Its bottom edge tears into the page.
It comes wide and narrow (phones), each animated and still; <picture> picks one.
"""
import random

from notebook import (ASSETS, BRAND, PAPER, SHADE, THEMES, Typesetter, blink, box, flip, mark, print_clip, sheet,
                      sprite_at, step_in, svg_doc, text_width, torn_path)
from pixel import CHEVRON, FLASK, TESLA_A, TESLA_B, WAVE_A, WAVE_B

WORDMARK = "dexterslab"
TAGLINE = "Let the code begin."
WHO = "Dexter Juevesano · CS @ UP Cebu · DOST scholar"
WHERE = "CEBU, PH · UTC+8"
BUTTON = "Open the portfolio"
NIGHT = dict(wall="#0b0b52", cabinet="#15156c", seam="#2626a0", floor_a="#14149a", floor_b="#0f0f7c",
             leds=["#ff7eb6", "#5ce1e6", "#ffd166", BRAND["lavender"], BRAND["neon"]])

LAYOUTS = {
    "wide": dict(w=840, h=340, floor=284, text_x=48, where_y=70, word=74, word_y=146, tag=24, tag_y=186,
                 who=14.5, who_y=214, btn_y=234, dexter=(620, 6), tesla=(730, 5), flask=(548, 4),
                 cabinets=[(0, 40, 36, 244), (800, 40, 40, 244)], centre=False),
    "narrow": dict(w=400, h=380, floor=168, text_x=200, where_y=206, word=52, word_y=254, tag=19, tag_y=284,
                   who=12.5, who_y=308, btn_y=324, dexter=(150, 5), tesla=(250, 4), flask=(96, 3),
                   cabinets=[(0, 20, 28, 148), (372, 20, 28, 148)], centre=True),
}


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


def banner(theme, animate=True, layout="wide"):
    L, b = LAYOUTS[layout], BRAND
    W, H = L["w"], L["h"]
    ts = Typesetter(f"hero{layout[0]}")
    at = (lambda t: t) if animate else (lambda t: None)
    out = [f'<rect width="{W}" height="{H}" fill="{NIGHT["wall"]}"/>']
    for k, c in enumerate(L["cabinets"]):
        out.append(cabinet(*c, f"{layout}{k}", animate))
    out.append(floor(L["floor"], W, H))

    # the scene: scientist, coil, flask, standing on the floor line
    fl = L["floor"]
    dx, ds = L["dexter"]
    wa, wb = sprite_at(WAVE_A, dx, fl - len(WAVE_A) * ds, ds), sprite_at(WAVE_B, dx, fl - len(WAVE_B) * ds, ds)
    out.append(flip(wa, wb, 0.9) if animate else wa)
    tx, tsz = L["tesla"]
    ta = sprite_at(TESLA_A, tx, fl - len(TESLA_A) * tsz, tsz)
    tb = sprite_at(TESLA_B, tx, fl - len(TESLA_B) * tsz, tsz)
    out.append(flip(ta, tb, 0.5) if animate else ta)
    fx_, fsz = L["flask"]
    out.append(sprite_at(FLASK, fx_, fl - len(FLASK) * fsz, fsz))

    # the words
    x, anchor = L["text_x"], ("middle" if L["centre"] else "start")
    out.append(f'<g>{step_in(at(0.15))}'
               + ts.text(WHERE, "body-bold", 12, x, L["where_y"], b["lavender"], anchor=anchor, tracking=1.6)[0] + "</g>")
    word = (ts.text(WORDMARK, "pixel", L["word"], x + 4, L["word_y"] + 4, b["neon"], anchor=anchor)[0]
            + ts.text(WORDMARK, "pixel", L["word"], x, L["word_y"], b["paper"], anchor=anchor)[0])
    out.append(f'<g>{step_in(at(0.3))}{word}</g>')
    out.append(f'<g>{step_in(at(0.5))}'
               + ts.text(TAGLINE, "title", L["tag"], x, L["tag_y"], b["lavender"], anchor=anchor)[0] + "</g>")
    out.append(f'<g>{step_in(at(0.65))}'
               + ts.text(WHO, "body", L["who"], x, L["who_y"], b["paper"], anchor=anchor)[0] + "</g>")
    bw = text_width(BUTTON, "body-bold", 14) + 52
    bx = x - bw / 2 if L["centre"] else x
    by = L["btn_y"]
    chev = sprite_at(CHEVRON, bx + bw - 26, by + 11, 2, {"P": b["ink"]})
    if animate:
        chev = (f'<g><animateTransform attributeName="transform" type="translate" values="0 0;4 0" keyTimes="0;0.5" '
                f'calcMode="discrete" dur="0.9s" repeatCount="indefinite"/>{chev}</g>')
    out.append(f'<g>{step_in(at(0.8))}'
               + box(bx + 4, by + 4, bw, 36, b["neon"], 3) + box(bx, by, bw, 36, b["paper"], 3)
               + ts.text(BUTTON, "body-bold", 14, bx + 16, by + 23, b["ink"])[0] + chev + "</g>")

    # the bottom edge tears into the page, as the portfolio's sheets do
    page = PAPER[theme]["page"]
    tear = torn_path(W, 12, f"hero{layout}", top=True, bottom=False)
    out.append(f'<path transform="translate(0 {H - 10})" d="{tear}" fill="{page}" shape-rendering="crispEdges"/>')
    return svg_doc(W, H, ts.defs_svg() + "".join(out),
                   f"{WORDMARK}: {TAGLINE} {WHO}. Open the portfolio.")


CONTACTS = [("linkedin", "LinkedIn", "linkedin.com/in/dsjuevesano"),
            ("github", "GitHub", "github.com/Llenoxinn")]
CONTACT_W, CONTACT_H = 376, 92


def contact(key, label, url, theme, animate=True):
    s = PAPER[theme]
    ts = Typesetter("ct")
    right = CONTACT_W - SHADE - 14
    chev = sprite_at(CHEVRON, right - 14, 34, 2, {"P": s["text"]})
    if animate:
        chev = (f'<g><animateTransform attributeName="transform" type="translate" values="0 0;4 0" keyTimes="0;0.5" '
                f'calcMode="discrete" dur="0.9s" repeatCount="indefinite"/>{chev}</g>')
    body = [sheet(theme, CONTACT_W, CONTACT_H, key),
            box(14, 14, 60, 60, BRAND["ink"], 3), mark(key, 28, 28, 32, BRAND["paper"]),
            ts.text(label, "title", 18, 88, 40, s["text"])[0],
            ts.text(url, "body", 13, 88, 61, s["muted"])[0],
            box(right - 22, 26, 30, 30, s["soft"], 2), chev]
    inner = "".join(body)
    if animate:
        defs, clip = print_clip(f"ct{key}", CONTACT_W, CONTACT_H)
        inner = f"<defs>{defs}</defs><g{clip}>{inner}</g>"
    return svg_doc(CONTACT_W, CONTACT_H, ts.defs_svg() + inner, f"{label}: {url}")


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
