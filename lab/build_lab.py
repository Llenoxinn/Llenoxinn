#!/usr/bin/env python3
"""Draw the DEXTER / XED profile and write README.md.

Light theme is DEXTER, dark theme is XED. Every picture ships -light and -dark; anything
that moves also ships a -still twin for reduced motion; full-column pieces also ship a
-narrow layout for phones. The five generated blocks (STACK, PROJECTS, CONTRIBUTIONS,
LEETCODE, ASSAY) are written here too; the hourly lab rounds then refresh the three live
ones through console.write_live().

    python lab/build_lab.py
"""
import re

import build_hero
import console
import panels
import rooms
from notebook import ASSETS, README, esc, scene, stamp, wide_scene

PORTFOLIO = "https://dexterslab-dev.vercel.app"
FEATURE_URL = "https://placebeat-studio.vercel.app"
CONTACT_URLS = {"linkedin": "https://www.linkedin.com/in/dsjuevesano/", "github": "https://github.com/Llenoxinn"}
SECTIONS = ("projects", "wins", "stack", "live", "contact")


def label_of(svg):
    m = re.search(r'aria-label="([^"]*)"', svg)
    return m.group(1).replace("&amp;", "&").replace("&quot;", '"').replace("&#39;", "'") if m else ""


def write(folder, stem, draw, narrow=True):
    """draw(theme, layout, animate) -> svg. Writes the theme x motion (x layout) set, returns
    the light wide svg (for alt text) and a stamp over every variant."""
    out = ASSETS / folder if folder else ASSETS
    out.mkdir(parents=True, exist_ok=True)
    parts = []
    for theme in ("light", "dark"):
        for layout in (("wide", "narrow") if narrow else ("wide",)):
            name = stem if layout == "wide" else f"{stem}-narrow"
            for animate, tag in ((True, ""), (False, "-still")):
                svg = draw(theme, layout, animate)
                (out / f"{name}{tag}-{theme}.svg").write_text(svg, encoding="utf-8")
                parts.append(svg)
    return draw("light", "wide", False), stamp(*parts)


def full(folder, stem, svg_and_stamp, width=760):
    svg, q = svg_and_stamp
    return wide_scene(stem, f"{stem}-narrow", label_of(svg), folder=f"assets/{folder}" if folder else "assets",
                      width=width, query=f"v={q}")


def card(folder, stem, svg_and_stamp, w, h):
    svg, q = svg_and_stamp
    return scene(stem, label_of(svg), w, h, folder=f"assets/{folder}", query=f"v={q}")


def slug(name):
    return re.sub(r"[^a-z0-9]+", "-", name.lower()).strip("-")


def main():
    panels.LINES.update(rooms.LINES)
    hero = write("", "banner", lambda t, l, a: build_hero.hero(t, a, l))
    heads = {k: write("headers", k, lambda t, l, a, k=k: panels.header(k, t, l, a)) for k in SECTIONS}
    feature = write("projects", "placebaistudio", lambda t, l, a: panels.feature(t, l, a))
    cards = []
    for i, p in enumerate(rooms.PROJECTS):
        art = write("projects", slug(p["name"]), lambda t, l, a, p=p, i=i: rooms.project_card(p, t, a, i), narrow=False)
        pic = card("projects", slug(p["name"]), art, 376, 104)
        cards.append(f'<a href="https://github.com/{p["repo"]}">{pic}</a>' if p["repo"] else pic)
    trophies = write("trophies", "wall", lambda t, l, a: rooms.trophy_wall(t, l, a))
    stack = write("stack", "cabinet", lambda t, l, a: rooms.cabinet(t, l, a))
    contacts = []
    for key, label, url in rooms.CONTACTS:
        art = write("contact", key, lambda t, l, a, key=key, label=label, url=url: rooms.intercom(key, label, url, t, a), narrow=False)
        contacts.append(f'<a href="{CONTACT_URLS[key]}">{card("contact", key, art, 376, 92)}</a>')

    def h3(k):
        return f'<h3 align="center">{full("headers", k, heads[k])}</h3>'

    live = {kind: console.live_block(kind) for kind in console.KINDS}
    text = f"""<!--
  DEXTER / XED, the GitHub lab of Dexter Juevesano (@Llenoxinn). Light theme is DEXTER,
  dark theme is XED. Every picture is drawn by lab/ (python lab/build_lab.py). Blocks
  bounded by NAME:START/END belong to their generators; the live ones are refreshed
  hourly by .github/workflows/lab-rounds.yml.
-->

<a href="{PORTFOLIO}">{full("", "banner", hero, "100%")}</a>

{h3("projects")}

<!-- PROJECTS:START -->
<p align="center">
<a href="{FEATURE_URL}">{full("projects", "placebaistudio", feature)}</a>
</p>
<p align="center">
{chr(10).join(cards)}
</p>
<!-- PROJECTS:END -->

{h3("wins")}

<p align="center">
{full("trophies", "wall", trophies)}
</p>

{h3("stack")}

<!-- STACK:START -->
<p align="center">
{full("stack", "cabinet", stack)}
</p>
<!-- STACK:END -->

{h3("live")}

<p align="center">
<!-- CONTRIBUTIONS:START -->
{live["github"]}
<!-- CONTRIBUTIONS:END -->
<!-- LEETCODE:START -->
{live["leetcode"]}
<!-- LEETCODE:END -->
<!-- ASSAY:START -->
{live["picogym"]}
<!-- ASSAY:END -->
</p>

{h3("contact")}

<p align="center">
{chr(10).join(contacts)}
</p>
"""
    README.write_text(text, encoding="utf-8")
    print("profile drawn and README written")


if __name__ == "__main__":
    main()
