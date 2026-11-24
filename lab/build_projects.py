#!/usr/bin/env python3
"""Draw the hero unit and the unit plaques, and fill the README's PROJECTS block.

The first project is the hero unit: a full-width plate with its logo in a gold-framed
portrait, its story, its award ribbon and its whole stack. The rest are unit plaques
two to a row: the project's own logo in a gold socket, name, one line, status and
stack. Private repositories are labelled rather than linked to a page that would 404.

    python lab/build_projects.py
"""
from icons import ICONS
from notebook import (ASSETS, Typesetter, mark, replace_block, scene, stamp, svg_doc, wide_scene, wrap,
                      write_pair)
from rts import HALF, INK, W, defs, glint, logo, orb, plaque, text

GITHUB = "https://github.com/Llenoxinn"
PROJECTS = [
    dict(name="PlacebAIStudio", repo=None, live="https://placebeat-studio.vercel.app", logo="placebai", art=None,
         line="Every effect works, except none of them touch your audio.",
         story="Reverb echoes your clicks, bass boost drops the buttons, and export hands back a silent master.",
         award=("Champion, Rage Quit Award", "MALFUNCTION Hackathon 2026"),
         stack=["React", "TypeScript", "Vite", "Vitest", "Matter.js", "XState", "Claude"]),
    dict(name="dfCTF", repo="dfCTF", logo="dfctf", art=None, line="Capture flags and climb the weekly leaderboard.",
         stack=["TypeScript", "Next.js", "React", "PostgreSQL", "Drizzle", "Docker"]),
    dict(name="BELaude", repo="BELaude", logo="belaude", art=None, line="Track the GWA you need for UP Latin honors.",
         stack=["React", "TypeScript", "Vite", "Tailwind CSS", "Vitest", "Python"]),
    dict(name="Sylvi", repo="Sylvi", logo="sylvi", art=None, line="Print-ready ID photo sheets, true to size.",
         stack=["TypeScript", "JavaScript", "React", "Vite", "PL/pgSQL", "HTML", "CSS"]),
    dict(name="Olatz-Tol", repo="Olatz-tol", logo="olatz", art=None, line="Watch any 3n + 1 path fall to 1.",
         stack=["React", "Vite", "Tailwind CSS", "Zustand", "Lucide"]),
    dict(name="Protein Structure Viewer Lite", repo="Protein-Structure-Viewer-Lite-", logo=None, art="helix",
         line="3D protein structures on raw Three.js.", stack=["React", "Vite", "Three.js", "React Three Fiber", "Drei"]),
    dict(name="viscal", repo="Viscal", logo="viscal", art=None, line="Generative art driven by pure math.",
         stack=["React", "Vite", "Tailwind CSS"]),
    dict(name="Perk the Star", repo="GeoCeff/perk-the-star", logo=None, art="orbit",
         line="Defend the Sun with orbital towers.", stack=["Godot", "C++"]),
    dict(name="PhyTree", repo=None, logo="phytree", art=None, line="Build and trace phylogenetic trees.",
         stack=["TypeScript", "React", "Vite", "Tailwind CSS", "D3.js", "Zustand"]),
]
CARD_H = 92


def slug(name):
    return name.lower().replace(" ", "-")


def link(p):
    if p["repo"]:
        return f"https://github.com/{p['repo']}" if "/" in p["repo"] else f"{GITHUB}/{p['repo']}"
    return p.get("live")


def status(p):
    if p.get("live") and not p["repo"]:
        return "LIVE DEMO", INK["green"]
    if not p["repo"]:
        return "PRIVATE", INK["muted"]
    return ("WITH GEOCEFF" if "/" in p["repo"] else "PUBLIC"), INK["green"]


def stack_marks(stack, x, y, size=16, gap=6):
    out = []
    for name in stack:
        if name.lower() in ICONS:
            out.append(f'<rect x="{x - 3}" y="{y - 3}" width="{size + 6}" height="{size + 6}" rx="3" fill="url(#steel)" stroke="#5d6168"/>'
                       + mark(name, x, y, size, "#e8e2d4"))
            x += size + 6 + gap
    return "".join(out)


def socket(p, cx, cy, d):
    from build_banner import glyph
    inner = logo(p["logo"], cx - d * .36, cy - d * .36, d * .72) if p["logo"] else glyph(p["art"], cx, cy)
    return orb(cx, cy, d, inner)


def unit(p, theme, animate=True):
    ts = Typesetter("u")
    word, colour = status(p)
    body = [defs(), plaque(0, 0, HALF, CARD_H), socket(p, 42, 44, 50),
            text(ts, p["name"], "head", 16 if len(p["name"]) < 22 else 14, 80, 30, INK["text"]),
            text(ts, word, "bold", 11, HALF - 16, 22, colour, anchor="end", track=.12),
            f'<circle cx="{HALF - 18 - len(word) * 6.6:.0f}" cy="18" r="3" fill="{colour}"/>',
            text(ts, p["line"], "body", 14, 80, 52, INK["soft"]),
            stack_marks(p["stack"], 82, 64)]
    where = status(p)[0].lower()
    alt = f"{p['name']} ({where}): {p['line']} Built with {', '.join(p['stack'])}."
    return svg_doc(HALF, CARD_H, ts.defs_svg() + "".join(body), alt), alt


def hero_unit(p, theme, layout, animate=True):
    ts = Typesetter("hu")
    wide = layout == "wide"
    w = W if wide else 400
    title, event = p["award"]
    if wide:
        h = 176
        tx = 176
        body = [defs(), plaque(0, 0, w, h, pattern=True),
                '<rect x="16" y="16" width="144" height="144" rx="3" fill="#120a1c" stroke="url(#gold)" stroke-width="3"/>',
                logo(p["logo"], 30, 30, 116, 10),
                text(ts, "HERO UNIT", "bold", 11, tx, 30, INK["gold"], track=.2),
                text(ts, p["name"], "title", 32, tx, 64, "url(#chrome)", stroke=("#0d1015", 2.5)),
                text(ts, p["line"], "semi", 18, tx, 90, INK["text"])]
        for i, line in enumerate(wrap(p["story"], "body", 14.5, 380)):
            body.append(text(ts, line, "body", 14.5, tx, 112 + i * 18, INK["muted"]))
        body.append(stack_marks(p["stack"], tx + 2, 146))
        ax = w - 250
        body.append(f'<rect x="{ax}" y="118" width="234" height="42" rx="3" fill="#2a1806" stroke="url(#gold)" stroke-width="1.5"/>'
                    f'<circle cx="{ax + 20}" cy="139" r="12" fill="url(#orbon)" stroke="#a8470c"/>'
                    + text(ts, title.upper(), "bold", 12.5, ax + 40, 135, "#ffe08a", track=.06)
                    + text(ts, event, "body", 13, ax + 40, 152, "#c9a86a"))
        body.append(text(ts, "LIVE DEMO", "bold", 12, w - 18, 30, INK["green"], anchor="end", track=.14)
                    + f'<circle cx="{w - 92}" cy="26" r="3.5" fill="{INK["green"]}"/>')
        if animate:
            body.append(f'<clipPath id="huc"><rect x="{ax}" y="118" width="234" height="42" rx="3"/></clipPath>'
                        f'<g clip-path="url(#huc)">{glint(ax, 118, 234, 42, 5.0, 1.6)}</g>')
    else:
        h = 300
        body = [defs(), plaque(0, 0, w, h, pattern=True),
                '<rect x="16" y="16" width="96" height="96" rx="3" fill="#120a1c" stroke="url(#gold)" stroke-width="3"/>',
                logo(p["logo"], 26, 26, 76, 8),
                text(ts, "HERO UNIT", "bold", 11, 128, 32, INK["gold"], track=.2),
                text(ts, p["name"], "title", 24, 128, 62, "url(#chrome)", stroke=("#0d1015", 2)),
                text(ts, "LIVE DEMO", "bold", 11, 128, 84, INK["green"], track=.14)]
        y = 136
        for line in wrap(p["line"], "semi", 16.5, 364):
            body.append(text(ts, line, "semi", 16.5, 18, y, INK["text"]))
            y += 21
        for line in wrap(p["story"], "body", 14, 364):
            body.append(text(ts, line, "body", 14, 18, y + 4, INK["muted"]))
            y += 18
        body.append(f'<rect x="16" y="{y + 16}" width="368" height="44" rx="3" fill="#2a1806" stroke="url(#gold)" stroke-width="1.5"/>'
                    f'<circle cx="36" cy="{y + 38}" r="12" fill="url(#orbon)" stroke="#a8470c"/>'
                    + text(ts, title.upper(), "bold", 12.5, 56, y + 34, "#ffe08a", track=.06)
                    + text(ts, event, "body", 13, 56, y + 51, "#c9a86a"))
        body.append(stack_marks(p["stack"], 20, y + 76))
    alt = (f"{p['name']}, hero unit, private repository with a live demo: {p['line']} {p['story']} "
           f"{title}, {event}. Built with {', '.join(p['stack'])}.")
    return svg_doc(w, h, ts.defs_svg() + "".join(body), alt), alt


def block():
    lead, rest = PROJECTS[0], PROJECTS[1:]
    stem = f"projects/{slug(lead['name'])}-feature"
    fsvg, falt = hero_unit(lead, "light", "wide")
    top = wide_scene(stem, f"{stem}-narrow", falt, width=W, query="v=" + stamp(fsvg))
    cells = []
    for p in rest:
        psvg, alt = unit(p, "light")
        pic = scene(f"projects/{slug(p['name'])}", alt, HALF, CARD_H, query="v=" + stamp(psvg))
        cells.append(f'<a href="{link(p)}">{pic}</a>' if link(p) else pic)
    return (f'<p align="center">\n<a href="{link(lead)}">{top}</a>\n</p>\n'
            '<p align="center">\n' + "\n".join(cells) + "\n</p>")


if __name__ == "__main__":
    out = ASSETS / "projects"
    out.mkdir(parents=True, exist_ok=True)
    for old in out.glob("*.svg"):
        old.unlink()
    lead = PROJECTS[0]
    write_pair(out, f"{slug(lead['name'])}-feature", lambda t, a: hero_unit(lead, t, "wide", a)[0])
    write_pair(out, f"{slug(lead['name'])}-feature-narrow", lambda t, a: hero_unit(lead, t, "narrow", a)[0])
    for p in PROJECTS[1:]:
        write_pair(out, slug(p["name"]), lambda t, a, p=p: unit(p, t, a)[0])
    changed = replace_block("PROJECTS", block())
    print(f"wrote the hero unit and {len(PROJECTS) - 1} unit plaques, README {'updated' if changed else 'unchanged'}")
