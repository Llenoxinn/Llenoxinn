#!/usr/bin/env python3
"""Draw the tech stack as the build menu and fill the README's STACK block.

Each tool is a bevelled steel build slot with its logo; each group opens with a gold
plate that names it. Every slot is its own small image, so the rows wrap on narrow
screens. Names live in alt text and hover titles; there are no skill levels or
percentages. When the section loads, the slots come online one by one.

    python lab/build_shelf.py
"""
import re

from notebook import ASSETS, THEMES, Typesetter, mark, replace_block, stamp, svg_doc, text_width, themed
from rts import defs, text

OUT = ASSETS / "stack"
TILE = 48
SHELF = [
    ("lang", ["C", "C++", "C#", "Haskell", "Kotlin", "Prolog", "Python", "JavaScript", "TypeScript", "HTML", "CSS",
              "LaTeX"]),
    ("web", ["React", "Next.js", "Svelte", "Vite", "Tailwind CSS", "Zustand", "D3.js", "Three.js", "Electron"]),
    ("backend", ["Node.js", "Supabase", "PostgreSQL", "Drizzle"]),
    ("ship", ["Docker", "Vercel", "GitHub Actions", "Vitest", "Playwright"]),
    ("tools", ["Godot", "WSL", "UCSF ChimeraX", "Audacity"]),
    ("ai", ["Antigravity", "Codex", "Claude", "OpenCode"]),
    ("design", ["Figma", "Adobe Photoshop", "Adobe InDesign", "Adobe Illustrator", "Canva"]),
]
GROUP = {"lang": "Languages", "web": "Web", "backend": "Back end", "ship": "Test and ship", "tools": "Tools",
         "ai": "AI agents", "design": "Design"}
NEW_LINE = {"web", "backend", "tools", "design"}    # ship shares backend's line, AI agents share tools' line


def slug(name):
    return re.sub(r"[^a-z0-9]+", "-", name.lower().replace("+", "p").replace("#", "sharp")).strip("-")


def appear(n):
    """Slots come online one by one in reading order, like a build menu filling in."""
    t = 0.25 + n * 0.025
    return (f'<animate attributeName="opacity" values="0;1" keyTimes="0;{t / (t + .01):.4f}" calcMode="discrete" '
            f'dur="{t + .01:.2f}s" fill="freeze"/>')


def tile(name, theme, n):
    """A bevelled steel build slot with the tool's logo."""
    body = (f'<g>{appear(n)}<rect x="2" y="3" width="44" height="44" rx="3" fill="#000" opacity=".5"/>'
            f'<rect x="1" y="1" width="44" height="44" rx="3" fill="url(#steel)" stroke="#8d939b" stroke-width="1"/>'
            f'<rect x="4" y="3" width="38" height="1" fill="#fff" opacity=".25"/>'
            + mark(name, 11, 11, 24, "#ece5d6") + "</g>")
    return svg_doc(TILE, TILE, defs() + body, name)


def group_tile(group, theme, n):
    """The gold plate that names a group of slots."""
    ts = Typesetter("g")
    label = GROUP[group].upper()
    w = round(text_width(label, "bold", 12, 12 * .14)) + 30
    body = (f'<g>{appear(n)}<rect x="2" y="3" width="{w - 3}" height="44" rx="3" fill="#000" opacity=".5"/>'
            f'<rect x="1" y="1" width="{w - 3}" height="44" rx="3" fill="url(#gold)" stroke="#fff2c4" stroke-width="1"/>'
            + text(ts, label, "bold", 12, (w - 2) / 2, 28, "#1c1005", anchor="middle", track=.14) + "</g>")
    return svg_doc(w, TILE, ts.defs_svg() + defs() + body, GROUP[group]), w


def items():
    """(kind, name, index) in reading order, so the press ripple runs left to right."""
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
                cells.append("<br>")     # each line starts with its group key, never orphaning it
            gsvg, gw = group_tile(name, "light", n)
            cells.append(themed(f"stack/group-{name}", f"{GROUP[name]}:", gw, TILE,
                                title=GROUP[name], query="v=" + stamp(gsvg)))
        else:
            tsvg = tile(name, "light", n)
            cells.append(themed(f"stack/{slug(name)}", name, TILE, TILE, title=name, query="v=" + stamp(tsvg)))
    return '<p align="center">\n' + "\n".join(cells) + "\n</p>"


if __name__ == "__main__":
    OUT.mkdir(parents=True, exist_ok=True)
    for old in OUT.glob("*.svg"):
        old.unlink()
    for theme in THEMES:
        for kind, name, n in items():
            if kind == "group":
                (OUT / f"group-{name}-{theme}.svg").write_text(group_tile(name, theme, n)[0], encoding="utf-8")
            else:
                (OUT / f"{slug(name)}-{theme}.svg").write_text(tile(name, theme, n), encoding="utf-8")
    changed = replace_block("STACK", block())
    print(f"wrote {sum(len(t) + 1 for _, t in SHELF)} keys per theme, README {'updated' if changed else 'unchanged'}")
