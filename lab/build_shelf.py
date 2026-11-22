#!/usr/bin/env python3
"""Draw the tech stack as compact icon tiles and fill the README's STACK block.

Each tool is its own small image, so the row wraps on narrow screens. Names live
in alt text and hover titles; there are no skill levels or percentages. Tiles
are notched pixel squares that cut in one after another, without a fade.

    python lab/build_shelf.py
"""
import re

from notebook import (ASSETS, BRAND, PAPER, Typesetter, box, mark, replace_block, step_in, svg_doc,
                      text_width, themed)

OUT = ASSETS / "stack"
TILE = 48
SHELF = [
    ("lang", ["C", "C++", "C#", "Haskell", "Kotlin", "Prolog", "Python", "JavaScript", "TypeScript", "HTML", "CSS",
              "LaTeX"]),
    ("web", ["React", "Next.js", "Svelte", "Vite", "Tailwind CSS", "Zustand", "D3.js", "Three.js", "Electron"]),
    ("backend", ["Node.js", "Supabase", "PostgreSQL", "Drizzle"]),
    ("ship", ["Docker", "Vercel", "GitHub Actions", "Vitest", "Playwright"]),
    ("tools", ["Godot", "WSL", "UCSF ChimeraX", "Audacity"]),
    ("design", ["Figma", "Adobe Photoshop", "Adobe InDesign", "Adobe Illustrator", "Canva"]),
]
GROUP = {"lang": "Languages", "web": "Web", "backend": "Back end", "ship": "Test and ship", "tools": "Tools",
         "design": "Design"}
NEW_LINE = {"web", "backend", "tools"}    # ship shares a line with backend, design with tools, on wide screens


def slug(name):
    return re.sub(r"[^a-z0-9]+", "-", name.lower().replace("+", "p").replace("#", "sharp")).strip("-")


def tile(name, theme, n):
    """A notched pixel tile with the tool's mark; it cuts in on its turn, left to right."""
    s = PAPER[theme]
    body = (f'<g>{step_in(min(n * 0.02, 0.9))}' + box(4, 4, TILE - 5, TILE - 5, s["shadow"], 3)
            + box(1, 1, TILE - 5, TILE - 5, s["sheet"], 3, s["line"])
            + mark(name, 11, 11, 22, s["text"]) + "</g>")
    return svg_doc(TILE, TILE, body, name)


def group_tile(group, theme, n):
    """An ink label that opens each group of tools."""
    ts = Typesetter("g")
    label = GROUP[group].upper()
    w = round(text_width(label, "body-bold", 11.5, 1)) + 28
    body = (f'<g>{step_in(min(n * 0.02, 0.9))}' + box(1, 1, w - 5, TILE - 5, BRAND["ink"], 3)
            + ts.text(label, "body-bold", 11.5, 13, 27.5, BRAND["paper"], tracking=1)[0] + "</g>")
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
    return '<p align="center">\n' + "\n".join(cells) + "\n</p>"


if __name__ == "__main__":
    OUT.mkdir(parents=True, exist_ok=True)
    for old in OUT.glob("*.svg"):
        old.unlink()
    for theme in PAPER:
        for kind, name, n in items():
            if kind == "group":
                (OUT / f"group-{name}-{theme}.svg").write_text(group_tile(name, theme, n)[0], encoding="utf-8")
            else:
                (OUT / f"{slug(name)}-{theme}.svg").write_text(tile(name, theme, n), encoding="utf-8")
    changed = replace_block("STACK", block())
    print(f"wrote {sum(len(t) + 1 for _, t in SHELF)} stack tiles per theme, README {'updated' if changed else 'unchanged'}")
