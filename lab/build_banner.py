#!/usr/bin/env python3
"""Build the profile hero and the contact cards.

The hero comes in a wide and a narrow (phone) layout, each animated and still;
<picture> picks one by screen width and prefers-reduced-motion.
"""
from notebook import (ASSETS, BRAND, SHEET, THEMES, Typesetter, bob, card, caret, dot_grid, fade, mark, packet,
                      pixels, rise, strip, svg_doc, text_width)
from pixel import SCIENTIST, sprite

TITLE = "/dev/dexter"
TAGLINE = "Let the code begin."
COMMAND = "open dexterslab-dev.vercel.app"
NAME, ROLE = "Dexter Juevesano", "CS @ UP Cebu · DOST scholar"
NAV = [("S", "Stack"), ("P", "Projects"), ("L", "Live"), ("C", "Contact")]
MONOGRAM = ["XXXXX..", "X....X.", "X.....X", "X.....X", "X.....X", "X....X.", "XXXXX.."]
TROPHY = ["XXXXXXXXXX", "XXXXXXXXXX", "X.XXXXXX.X", "X.XXXXXX.X", ".XXXXXXXX.",
          "..XXXXXX..", "....XX....", "....XX....", "...XXXX...", "..XXXXXX.."]
CHIP = [".X.X.X.X..", "XXXXXXXXX.", ".X.....X..", "XX.XXX.XX.", ".X.XXX.X..",
        "XX.XXX.XX.", ".X.....X..", "XXXXXXXXX.", ".X.X.X.X..", ".........."]
TOASTS = [(TROPHY, "ctf > champion"), (CHIP, "stats > live")]

# Everything that differs between the wide and the phone layout
LAYOUTS = {
    "wide": dict(w=840, h=340, title=80, title_y=176, tagline=[(TAGLINE, 222)], tag_size=22, pill_y=246, code=15,
                 toast_y=264, toast_x=28, nav=True,
                 traces=["M0 104H54V196H110V264", "M840 128H790V196H{rx}V264"]),
    "narrow": dict(w=400, h=380, title=60, title_y=150, tagline=[(TAGLINE, 192)], tag_size=19, pill_y=214, code=13,
                   toast_y=310, toast_x=14, nav=False,
                   traces=["M0 76H24V290H40V310", "M400 100H380V296H{rx}V310"]),
}


def toast_width(line):
    return text_width(line, "code-bold", 13) + 64


def banner(theme, animate=True, layout="wide"):
    L, b = LAYOUTS[layout], BRAND
    W, H = L["w"], L["h"]
    ts = Typesetter(f"hero{layout[0]}")
    widths = [toast_width(line) for _, line in TOASTS]
    xs = [L["toast_x"], W - L["toast_x"] - widths[1]]
    traces = [t.format(rx=round(xs[1] + widths[1] * 0.35)) for t in L["traces"]]

    out = [f'<defs><clipPath id="frame{layout[0]}"><rect width="{W}" height="{H}" rx="12"/></clipPath></defs>',
           f'<g clip-path="url(#frame{layout[0]})"><rect width="{W}" height="{H}" fill="{b["ink"]}"/>',
           dot_grid(W, H, b["lavender"], f"hero{layout}", opacity=0.12, twinkle=(26 if layout == "wide" else 16) if animate else 0)]
    for k, d in enumerate(traces):
        out.append(f'<path d="{d}" fill="none" stroke="{b["neon"]}" stroke-width="1.5" stroke-dasharray="3 4"/>')
        if animate:
            out.append(packet(d, b["paper"], 4.2, begin=k * 1.4) + packet(d, b["lavender"], 4.2, begin=k * 1.4 + 2.1))
    out.append("</g>")

    # top bar: monogram, wordmark, bracket-key navigation
    out.append(f'<rect x="24" y="18" width="33" height="33" rx="5" fill="none" stroke="{b["lavender"]}" stroke-width="1.5"/>'
               + pixels(MONOGRAM, 30, 24, 3, {"X": b["paper"]}))
    out.append(ts.text("dexterslab", "code-bold", 15, 68, 40, b["paper"])[0])
    x = W - 24
    for key, word in reversed(NAV):
        if L["nav"]:
            x -= text_width(word, "code", 13)
            out.append(ts.text(word, "code", 13, x, 40, b["paper"])[0])
        label = f"[{key}] " if L["nav"] else f"[{key}]"
        x -= text_width(label, "code", 13)
        out.append(ts.text(label, "code", 13, x, 40, b["lavender"])[0])
        x -= 18 if L["nav"] else 8

    def part(svg, motion):
        return f'<g>{motion if animate else ""}{svg}</g>'

    # the title, misprinted in neon; every few seconds the plates slip
    glitch = ('<animateTransform attributeName="transform" type="translate" values="0 0;0 0;{a} 0;{b} 0;0 0" '
              'keyTimes="0;0.9;0.93;0.96;1" dur="6.5s" begin="2s" repeatCount="indefinite"/>')
    ty = L["title_y"]
    shadow = ts.text(TITLE, "headline", L["title"], W / 2 + 4, ty + 4, b["neon"], anchor="middle")[0]
    face = ts.text(TITLE, "headline", L["title"], W / 2, ty, b["paper"], anchor="middle")[0]
    if animate:
        shadow = f'<g>{glitch.format(a=4, b=-2)}{shadow}</g>'
        face = f'<g>{glitch.format(a=-3, b=2)}{face}</g>'
    out.append(part(shadow + face, rise(0.05, 14, 0.5)))
    out.append(part("".join(ts.text(t, "text", L["tag_size"], W / 2, y, b["lavender"], anchor="middle")[0]
                            for t, y in L["tagline"]), rise(0.15, 10, 0.45)))

    # the command pill types itself out
    size, py = L["code"], L["pill_y"]
    cw = text_width(f"$ {COMMAND}", "code", size)
    pw = cw + 84
    px = (W - pw) / 2
    base = py + 22 + size * 0.35
    pill = [f'<rect x="{px:.1f}" y="{py}" width="{pw:.1f}" height="44" rx="4" fill="#ffffff"/>',
            ts.text("$ ", "code", size, px + 20, base, b["neon"])[0]]
    sx = px + 20 + text_width("$ ", "code", size)
    typed, done = ts.text(COMMAND, "code", size, sx, base, b["ink"], reveal=(0.6, 0.03) if animate else None)
    pill.append(typed)
    end = sx + text_width(COMMAND, "code", size) + 3
    pill.append(caret(end, py + 14, 8, 17, b["neon"], done) if animate
                else f'<rect x="{end:.1f}" y="{py + 14}" width="8" height="17" fill="{b["neon"]}"/>')
    pill.append(f'<path d="M{px + pw - 32:.1f} {py + 13}h10v3h-7v14h-3Z M{px + pw - 27:.1f} {py + 18}h11v15h-11Z" '
                f'fill="none" stroke="{b["ink"]}" stroke-width="1.5"/>')
    out.append(part("".join(pill), rise(0.3, 10, 0.4)))

    # floating status toasts; the scientist rides the lab's
    ty = L["toast_y"]
    for k, ((icon, line), tx, tw) in enumerate(zip(TOASTS, xs, widths)):
        head, tail = line.split(" > ")
        toast = (f'<rect x="{tx:.1f}" y="{ty}" width="{tw:.1f}" height="44" rx="6" fill="#ffffff"/>'
                 + pixels(icon, tx + 12, ty + 9, 2.6, {"X": b["ink"]})
                 + ts.text(f"{head} > ", "code", 13, tx + 50, ty + 27, b["neon"])[0]
                 + ts.text(tail, "code-bold", 13, tx + 50 + text_width(f"{head} > ", "code", 13), ty + 27, b["ink"])[0])
        if k == 1:
            toast += sprite(SCIENTIST, tx + tw - 58, ty - 54, 3)
        motion = rise(1.7 + k * 0.15, 10, 0.4) if animate else ""
        float_ = bob(4, 4.5, begin=2.4 + k * 1.3) if animate else ""
        out.append(f'<g>{motion}<g>{float_}{toast}</g></g>')
    return svg_doc(W, H, ts.defs_svg() + "".join(out),
                   f"dexterslab: {TITLE}. {TAGLINE} {NAME}, {ROLE}. Open the portfolio.")


# Contact cards: a typed command over the network's mark, like the project cards
CONTACTS = [("linkedin", "LinkedIn", "linkedin.com/in/dsjuevesano", "Say hello"),
            ("github", "GitHub", "github.com/Llenoxinn", "Follow the lab")]
CONTACT_W, CONTACT_H = 376, 96


def contact(key, label, url, action, theme):
    s = SHEET[theme]
    ts = Typesetter("ct")
    head, typed = strip(ts, CONTACT_W, 0, [("$ ", BRAND["neon"]), (f"open {url}", BRAND["paper"])],
                        start=0.15, rate=0.018, top=True)
    body = (card(theme, CONTACT_W, CONTACT_H) + head
            + f'<g opacity="1">{fade(typed + 0.05)}'
            + mark(key, 16, 46, 32, s["text"])
            + ts.text(label, "label", 17, 62, 63, s["text"])[0]
            + ts.text(action, "text", 13, 62, 82, s["muted"])[0]
            + ts.text("→", "text", 22, CONTACT_W - 18, 72, s["muted"], anchor="end")[0] + "</g>")
    return svg_doc(CONTACT_W, CONTACT_H, ts.defs_svg() + body, f"{label}: {url}")


if __name__ == "__main__":
    for theme in THEMES:
        for layout, stem in (("wide", "banner"), ("narrow", "banner-narrow")):
            (ASSETS / f"{stem}-{theme}.svg").write_text(banner(theme, True, layout), encoding="utf-8")
            (ASSETS / f"{stem}-still-{theme}.svg").write_text(banner(theme, False, layout), encoding="utf-8")
        for key, label, url, action in CONTACTS:
            (ASSETS / f"contact-{key}-{theme}.svg").write_text(contact(key, label, url, action, theme), encoding="utf-8")
    print("wrote the wide and narrow hero, their stills and the contact cards")
