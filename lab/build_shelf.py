#!/usr/bin/env python3
"""Draw the tech stack as compact icon tiles and fill the README's STACK block.

Each tool is its own small image, so the row wraps on narrow screens. Names live
in alt text and hover titles; there are no skill levels or percentages. Tiles
fade in one after another as they come into view.

    python lab/build_shelf.py
"""
import re

from notebook import ASSETS, BRAND, SHEET, Typesetter, fade, mark, replace_block, svg_doc, text_width, themed

OUT = ASSETS / "stack"
TILE = 48
SHELF = [
    ("lang", ["C", "C++", "Haskell", "Python", "JavaScript", "TypeScript", "HTML", "CSS"]),
    ("web", ["React", "Next.js", "Svelte", "Vite", "Tailwind CSS", "Zustand", "D3.js"]),
    ("backend", ["Node.js", "Supabase"]),
    ("tools", ["Godot", "WSL", "UCSF ChimeraX", "Audacity"]),
    ("design", ["Figma", "Adobe Photoshop", "Adobe InDesign", "Adobe Illustrator", "Canva"]),
]
GROUP = {"lang": "Languages", "web": "Web", "backend": "Back end", "tools": "Tools", "design": "Design"}
NEW_LINE = {"web", "backend", "design"}    # tools shares a line with backend on wide screens


def slug(name):
    return re.sub(r"[^a-z0-9]+", "-", name.lower().replace("+", "p")).strip("-")


def tile(name, theme, n):
    s = SHEET[theme]
    body = (f'<g opacity="1">{fade(0.05 + n * 0.03, 0.25)}'
            f'<rect x="0.75" y="0.75" width="{TILE - 1.5}" height="{TILE - 1.5}" rx="6" fill="{s["sheet"]}" '
            f'stroke="{s["edge"]}" stroke-width="1.5"/>'
            + mark(name, 12, 12, 24, s["text"]) + "</g>")
    return svg_doc(TILE, TILE, body, name)


def group_tile(group, theme, n):
    """A mono folder label that opens each group: lang/, web/ …"""
    ts = Typesetter("g")
    label = f"{group}/"
    w = round(text_width(label, "code-bold", 13)) + 28
    body = (f'<g opacity="1">{fade(0.05 + n * 0.03, 0.25)}'
            f'<rect width="{w}" height="{TILE}" rx="6" fill="{BRAND["ink"]}"/>'
            + ts.text(label, "code-bold", 13, 14, 29, BRAND["paper"])[0] + "</g>")
    return svg_doc(w, TILE, ts.defs_svg() + body, GROUP[group]), w


def items():
    """(kind, name, index) in reading order, so the fade-in runs left to right."""
    n = 0
    for group, tools in SHELF:
        yield "group", group, n
        n += 1
        for name in tools:
            yield "tool", name, n
            n += 1


def block():
    cells = []
    for kind, name, n in items():
        if kind == "group":
            if name in NEW_LINE:
                cells.append("<br>")     # each line starts with its folder label, never orphaning it
            cells.append(themed(f"stack/group-{name}", f"{GROUP[name]}:", group_tile(name, "light", n)[1], TILE,
                                title=GROUP[name]))
        else:
            cells.append(themed(f"stack/{slug(name)}", name, TILE, TILE, title=name))
    return "<p>\n" + "\n".join(cells) + "\n</p>"


if __name__ == "__main__":
    OUT.mkdir(parents=True, exist_ok=True)
    for old in OUT.glob("*.svg"):
        old.unlink()
    for theme in SHEET:
        for kind, name, n in items():
            if kind == "group":
                (OUT / f"group-{name}-{theme}.svg").write_text(group_tile(name, theme, n)[0], encoding="utf-8")
            else:
                (OUT / f"{slug(name)}-{theme}.svg").write_text(tile(name, theme, n), encoding="utf-8")
    changed = replace_block("STACK", block())
    print(f"wrote {sum(len(t) + 1 for _, t in SHELF)} stack tiles per theme, README {'updated' if changed else 'unchanged'}")
