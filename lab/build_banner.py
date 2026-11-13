#!/usr/bin/env python3
"""Build the profile hero and the contact cards.

The hero comes in a wide and a narrow (phone) layout, each animated and still;
<picture> picks one by screen width and prefers-reduced-motion.
"""
from notebook import (ASSETS, BRAND, SHEET, THEMES, Typesetter, bob, card, dot_grid, fx, mark, packet, pixels, rise,
                      strip, svg_doc, text_width, typed)
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
TOASTS_WIDE = [(TROPHY, "ctf > champion · 1st"), (CHIP, "stats > live telemetry")]
TOASTS_NARROW = [(TROPHY, "ctf > 1st"), (CHIP, "stats > live")]

# Layout dimensions
LAYOUTS = {
    "wide": dict(w=840, h=340, title=74, title_y=148, tagline=[(TAGLINE, 190)], tag_size=19, pill_y=230, code=13.5,
                 toast_y=270, toast_x=28, nav=True,
                 traces=["M0 96H48V192H96V270", "M840 120H796V192H{rx}V270"]),
    "narrow": dict(w=400, h=360, title=54, title_y=138, tagline=[(TAGLINE, 178)], tag_size=16.5, pill_y=206, code=12,
                   toast_y=294, toast_x=14, nav=False,
                   traces=["M0 72H20V280H36V294", "M400 96H380V280H{rx}V294"]),
}


def toast_width(line):
    return text_width(line, "code-bold", 12.5) + 64


def banner(theme, animate=True, layout="wide"):
    L, b = LAYOUTS[layout], BRAND
    W, H = L["w"], L["h"]
    ts = Typesetter(f"hero{layout[0]}")
    toasts = TOASTS_WIDE if layout == "wide" else TOASTS_NARROW
    widths = [toast_width(line) for _, line in toasts]
    xs = [L["toast_x"], W - L["toast_x"] - widths[1]]
    traces = [t.format(rx=round(xs[1] + widths[1] * 0.35)) for t in L["traces"]]

    is_dark = (theme == "dark")
    bg_color = "#0c0e27" if is_dark else "#fcfcfd"
    border_color = "#34348a" if is_dark else "#d4d4ea"
    inner_border = "#202058" if is_dark else "#f0f0fa"
    dots_color = b["neon"] if is_dark else b["lavender"]
    dots_opacity = 0.16 if is_dark else 0.22
    trace_color = b["neon"] if is_dark else b["lavender"]
    packet_col1 = b["paper"] if is_dark else b["ink"]
    packet_col2 = b["lavender"] if is_dark else b["neon"]

    top_text = b["paper"] if is_dark else b["ink"]
    top_muted = b["lavender"] if is_dark else "#5a5a9e"

    title_face_col = b["paper"] if is_dark else b["ink"]
    title_shadow_col = b["neon"] if is_dark else "#e2e2fa"
    tagline_col = b["lavender"] if is_dark else "#4f4fc4"

    pill_bg = "#15173c" if is_dark else "#ffffff"
    pill_border = "#474780" if is_dark else b["ink"]
    pill_prompt = b["neon"] if is_dark else b["ink"]
    pill_cmd = b["paper"] if is_dark else b["ink"]
    pill_caret = b["neon"] if is_dark else b["neon"]
    pill_btn = b["paper"] if is_dark else b["ink"]

    toast_bg = "#141638" if is_dark else "#ffffff"
    toast_border = "#34348a" if is_dark else "#d4d4ea"
    toast_head = b["neon"] if is_dark else "#6666fd"
    toast_tail = b["paper"] if is_dark else b["ink"]

    out = [f'<defs><clipPath id="frame{layout[0]}"><rect width="{W}" height="{H}" rx="14"/></clipPath></defs>',
           f'<g clip-path="url(#frame{layout[0]})">',
           f'<rect width="{W}" height="{H}" fill="{bg_color}" stroke="{border_color}" stroke-width="2"/>',
           f'<rect x="2.5" y="2.5" width="{W - 5}" height="{H - 5}" rx="11.5" fill="none" stroke="{inner_border}" stroke-width="1" opacity="0.6"/>',
           dot_grid(W, H, dots_color, f"hero{layout}", opacity=dots_opacity, twinkle=(24 if layout == "wide" else 14) if animate else 0)]

    for k, d in enumerate(traces):
        out.append(f'<path d="{d}" fill="none" stroke="{trace_color}" stroke-width="1.5" stroke-dasharray="3 4"/>')
        if animate:
            out.append(packet(d, packet_col1, 4.2, begin=k * 1.4) + packet(d, packet_col2, 4.2, begin=k * 1.4 + 2.1))
    out.append("</g>")

    # Top window bar: traffic control dots + breadcrumbs + bracket keys
    if layout == "wide":
        # 3 discrete window control dots (Notion Dev / macOS style)
        dots = (f'<circle cx="28" cy="24" r="4.5" fill="#ff5f56" opacity="{0.95 if is_dark else 0.9}"/>'
                f'<circle cx="41" cy="24" r="4.5" fill="#ffbd2e" opacity="{0.95 if is_dark else 0.9}"/>'
                f'<circle cx="54" cy="24" r="4.5" fill="#27c93f" opacity="{0.95 if is_dark else 0.9}"/>')
        out.append(dots)
        # Monogram in subtle container
        out.append(f'<rect x="74" y="12" width="24" height="24" rx="5" fill="{b["ink"]}"/>'
                   + pixels(MONOGRAM, 78, 16, 2.2, {"X": b["paper"]}))
        out.append(ts.text("dexterslab", "code-bold", 14, 106, 29, top_text)[0])
        out.append(ts.text("~/dev/dexter", "code", 12, 196, 29, top_muted)[0])
        out.append(ts.text("· UP Cebu · DOST scholar", "code", 11.5, 288, 29, top_muted)[0])
    else:
        dots = (f'<circle cx="22" cy="22" r="4" fill="#ff5f56" opacity="0.95"/>'
                f'<circle cx="34" cy="22" r="4" fill="#ffbd2e" opacity="0.95"/>'
                f'<circle cx="46" cy="22" r="4" fill="#27c93f" opacity="0.95"/>')
        out.append(dots)
        out.append(ts.text("dexterslab", "code-bold", 13, 60, 27, top_text)[0])

    # Right side: bracket key navigation
    x = W - 24
    for key, word in reversed(NAV):
        if L["nav"]:
            x -= text_width(word, "code", 12)
            out.append(ts.text(word, "code", 12, x, 29, top_text)[0])
        label = f"[{key}] " if L["nav"] else f"[{key}]"
        x -= text_width(label, "code", 12)
        out.append(ts.text(label, "code", 12, x, 29, top_muted)[0])
        x -= 16 if L["nav"] else 8

    def part(svg, motion):
        return f'<g>{motion if animate else ""}{svg}</g>'

    # Title: /dev/dexter with rock-solid presence (no jitter/glitch)
    ty = L["title_y"]
    shadow = ts.text(TITLE, "headline", L["title"], W / 2 + 2, ty + 2, title_shadow_col, anchor="middle")[0]
    face = ts.text(TITLE, "headline", L["title"], W / 2, ty, title_face_col, anchor="middle")[0]
    out.append(part(shadow + face, rise(0.04, 8, 0.35)))

    # Tagline
    out.append(part("".join(ts.text(t, "text", L["tag_size"], W / 2, y, tagline_col, anchor="middle")[0]
                            for t, y in L["tagline"]), rise(0.10, 6, 0.35)))

    # Interactive Command Pill
    size, py = L["code"], L["pill_y"]
    cw = text_width(f"$ {COMMAND}", "code", size)
    pw = cw + 88
    px = (W - pw) / 2
    base = py + 22 + size * 0.35
    pill = [f'<rect x="{px:.1f}" y="{py}" width="{pw:.1f}" height="42" rx="8" fill="{pill_bg}" stroke="{pill_border}" stroke-width="1.5"/>',
            f'<rect x="{px + 2:.1f}" y="{py + 2}" width="{pw - 4:.1f}" height="38" rx="6" fill="none" stroke="{inner_border}" stroke-width="1" opacity="0.5"/>',
            ts.text("$ ", "code", size, px + 18, base, pill_prompt)[0]]
    sx = px + 18 + text_width("$ ", "code", size)
    line, _ = typed(ts, [(COMMAND, pill_cmd)], sx, base, size, 0.3 if animate else None, caret_colour=pill_caret)
    pill.append(line)
    # Right-hand ENTER indicator with button-in-button styling
    btn_w = 26
    bx = px + pw - btn_w - 12
    pill.append(f'<rect x="{bx:.1f}" y="{py + 10}" width="{btn_w}" height="22" rx="5" fill="{toast_bg}" stroke="{border_color}" stroke-width="1"/>'
                + ts.text("↵", "code-bold", 12.5, bx + 7, py + 25.5, pill_btn)[0])
    out.append(part("".join(pill), rise(0.16, 6, 0.35)))

    # Floating status toasts (Notion callout blocks)
    ty = L["toast_y"]
    for k, ((icon, line), tx, tw) in enumerate(zip(toasts, xs, widths)):
        head, tail = line.split(" > ")
        toast = [f'<rect x="{tx:.1f}" y="{ty}" width="{tw:.1f}" height="42" rx="8" fill="{toast_bg}" stroke="{toast_border}" stroke-width="1.2"/>',
                 f'<rect x="{tx + 2:.1f}" y="{ty + 2}" width="{tw - 4:.1f}" height="38" rx="6" fill="none" stroke="{inner_border}" stroke-width="1" opacity="0.6"/>',
                 f'<rect x="{tx + 8:.1f}" y="{ty + 7}" width="28" height="28" rx="6" fill="{b["ink"]}"/>',
                 pixels(icon, tx + 13, ty + 12, 2.2, {"X": b["paper"]}),
                 ts.text(f"{head} > ", "code", 12.5, tx + 44, ty + 26, toast_head)[0],
                 ts.text(tail, "code-bold", 12.5, tx + 44 + text_width(f"{head} > ", "code", 12.5), ty + 26, toast_tail)[0]]
        if k == 1:
            toast.append(sprite(SCIENTIST, tx + tw - 54, ty - 52, 2.8))
        motion = rise(0.22 + k * 0.08, 6, 0.35) if animate else ""
        float_ = bob(2.5, 3.5, begin=0.5 + k * 1.0) if animate else ""
        out.append(f'<g>{motion}<g>{float_}{"".join(toast)}</g></g>')

    return svg_doc(W, H, ts.defs_svg() + "".join(out),
                   f"dexterslab: {TITLE}. {TAGLINE} {NAME}, {ROLE}. Open the portfolio.")


# Contact cards: a typed command over the network's mark, like the project cards
CONTACTS = [("linkedin", "LinkedIn", "linkedin.com/in/dsjuevesano", "Say hello"),
            ("github", "GitHub", "github.com/Llenoxinn", "Follow the lab")]
CONTACT_W, CONTACT_H = 376, 96


def contact(key, label, url, action, theme, animate=True):
    s = SHEET[theme]
    ts = Typesetter("ct")
    head, done = strip(ts, CONTACT_W, 0, [("$ ", BRAND["neon"]), (f"open {url}", BRAND["paper"])],
                       start=0.15 if animate else None, rate=0.035, radius=10, top=True)
    body = [card(theme, CONTACT_W, CONTACT_H, radius=10), head,
            f'<g opacity="1">{fx(0.08 if animate else None)}',
            f'<rect x="16" y="42" width="42" height="42" rx="8" fill="{s["soft"]}" stroke="{s["inner_edge"]}" stroke-width="1"/>',
            mark(key, 22, 48, 30, s["text"]),
            ts.text(label, "label", 16.5, 68, 62, s["text"])[0],
            ts.text(action, "text", 13, 68, 80, s["muted"])[0],
            # Button-in-button nested trailing arrow circle
            f'<circle cx="{CONTACT_W - 28}" cy="63" r="14" fill="{s["soft"]}" stroke="{s["inner_edge"]}" stroke-width="1"/>',
            ts.text("↗", "text", 16, CONTACT_W - 28, 68.5, s["text"], anchor="middle")[0],
            "</g>"]
    return svg_doc(CONTACT_W, CONTACT_H, ts.defs_svg() + "".join(body), f"{label}: {url}")


if __name__ == "__main__":
    for theme in THEMES:
        for layout, stem in (("wide", "banner"), ("narrow", "banner-narrow")):
            (ASSETS / f"{stem}-{theme}.svg").write_text(banner(theme, True, layout), encoding="utf-8")
            (ASSETS / f"{stem}-still-{theme}.svg").write_text(banner(theme, False, layout), encoding="utf-8")
        for key, label, url, action in CONTACTS:
            (ASSETS / f"contact-{key}-{theme}.svg").write_text(contact(key, label, url, action, theme), encoding="utf-8")
            (ASSETS / f"contact-{key}-still-{theme}.svg").write_text(contact(key, label, url, action, theme, False),
                                                                    encoding="utf-8")
    print("wrote the wide and narrow hero, their stills and the contact cards")
