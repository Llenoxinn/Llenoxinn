#!/usr/bin/env python3
"""Draw the section banners and the medals plaque.

Banners replace Markdown headings (and their rule lines): a gold double rule broken
by an iron cartouche with the section's name. Medals stand on one riveted plate, one
per real result, each catching a glint in turn.

    python lab/build_headers.py
"""
from notebook import ASSETS, Typesetter, svg_doc, write_pair
from rts import INK, W, banner, defs, plaque, text

SECTIONS = [  # key, banner title, meta at the right
    ("projects", "Units deployed", "9 projects"),
    ("wins", "Medals earned", "3 results"),
    ("live", "Training grounds", "live, hourly"),
    ("stack", "Build menu", "43 structures"),
    ("contact", "Commands", None),
]

# Real results only; newest first.
WINS = [
    dict(slug="malfunction", award="gold", title="Champion, Rage Quit Award", event="MALFUNCTION Hackathon 2026",
         org="iDE.A iAcademy", when="21 Nov 2026", note="Team Dexter's Fun Club"),
    dict(slug="hackforgov", award="silver", title="Top 2 Student Performer", event="HackforGov5 Region 7",
         org="DICT Region 7", when="Oct 2026", note="National wildcard qualifier"),
    dict(slug="champion", award="gold", title="Champion", event="Mission: CTF", org="UP Computer Science Guild",
         when="Sep 2026", note="1st place overall"),
]
METAL = {"gold": ("#ffcf6a", "#4a2a08"), "silver": ("#d9dee4", "#3a3d42")}


def header(key, title, meta, theme, animate=True, layout="wide"):
    w = W if layout == "wide" else 400
    ts = Typesetter("h")
    art = banner(ts, title, w, meta if layout == "wide" else None)     # set the type first, then its glyph defs
    return svg_doc(w, 46, ts.defs_svg() + defs() + art, title)


def medal(cx, top, kind, k, animate):
    face, edge = METAL[kind]
    star = (f'<path d="M{cx} {top + 36}l4 9 10 1-7 7 2 10-9-5-9 5 2-10-7-7 10-1z" fill="#fff" fill-opacity=".85"/>')
    shine = ""
    if animate:
        shine = (f'<circle cx="{cx}" cy="{top + 52}" r="24" fill="#fff" opacity="0">'
                 f'<animate attributeName="opacity" values="0;.45;0;0" keyTimes="0;.04;.1;1" dur="5.4s" '
                 f'begin="{1 + k * 1.8:.1f}s" repeatCount="indefinite"/></circle>')
    return (f'<path d="M{cx - 17} {top}h12l8 30h-16zM{cx + 5} {top}h12l-6 30h-14z" fill="#7a1d08" stroke="#2a0a04"/>'
            f'<path d="M{cx - 13} {top}h4l8 30h-4zM{cx + 9} {top}h4l-6 30h-4z" fill="#c2410c"/>'
            f'<circle cx="{cx}" cy="{top + 52}" r="26" fill="{face}" stroke="{edge}" stroke-width="3"/>'
            f'<circle cx="{cx}" cy="{top + 52}" r="19" fill="none" stroke="#fff" stroke-opacity=".6" stroke-width="1.5"/>'
            + star + shine)


def case(theme, layout, animate=True):
    ts = Typesetter("md")
    wide = layout == "wide"
    if wide:
        w, h, n = W, 200, len(WINS)
        col = (w - 2 * 12) / n
        body = [defs(), plaque(0, 0, w, h, pattern=True)]
        for k, win in enumerate(WINS):
            cx = 12 + col * (k + .5)
            if k:
                body.append(f'<rect x="{12 + col * k:.0f}" y="20" width="1" height="{h - 40}" fill="#5d6168" opacity=".5"/>')
            body.append(medal(cx, 14, win["award"], k, animate)
                        + text(ts, win["when"].upper(), "bold", 11, cx, 112, INK["amber"], anchor="middle", track=.16)
                        + text(ts, win["title"], "head", 16, cx, 134, INK["text"], anchor="middle")
                        + text(ts, win["event"], "semi", 14, cx, 156, INK["soft"], anchor="middle")
                        + text(ts, f"{win['org']}, {win['note']}", "body", 12.5, cx, 176, INK["dim"], anchor="middle"))
    else:
        w, pitch = 400, 104
        h = 16 + len(WINS) * pitch
        body = [defs(), plaque(0, 0, w, h, pattern=True)]
        for k, win in enumerate(WINS):
            y = 10 + k * pitch
            body.append(medal(54, y, win["award"], k, animate)
                        + text(ts, win["when"].upper(), "bold", 10.5, 104, y + 22, INK["amber"], track=.14)
                        + text(ts, win["title"], "head", 15, 104, y + 42, INK["text"])
                        + text(ts, win["event"], "semi", 13.5, 104, y + 61, INK["soft"])
                        + text(ts, f"{win['org']}, {win['note']}", "body", 12, 104, y + 79, INK["dim"]))
    alt = "Medals earned. " + " ".join(f"{w['title']}: {w['event']}, {w['org']}, {w['when']}. {w['note']}." for w in WINS)
    return svg_doc(w, h, ts.defs_svg() + "".join(body), alt), alt


if __name__ == "__main__":
    out = ASSETS / "headers"
    out.mkdir(parents=True, exist_ok=True)
    for old in out.glob("*.svg"):
        old.unlink()
    for key, title, meta in SECTIONS:
        write_pair(out, key, lambda t, a: header(key, title, meta, t, a))
        write_pair(out, f"{key}-narrow", lambda t, a: header(key, title, meta, t, a, "narrow"))
    write_pair(out, "shelf", lambda t, a: case(t, "wide", a)[0])
    write_pair(out, "shelf-narrow", lambda t, a: case(t, "narrow", a)[0])
    print(f"wrote {len(SECTIONS)} banners and the medals plaque")
