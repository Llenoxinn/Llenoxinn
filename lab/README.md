# dexterslab: lab equipment

This folder draws every picture on the GitHub profile, in the live portfolio's language: DOS blue, paper and lavender, a pixel lab at night for the hero, and lab-sheet cards with torn pixel edges, notched corners and hard shadows. Pixelify Sans for tag words and the wordmark, Chakra Petch for text and digits, Inter Bold for titles.

## Run the lab

Use Python 3.12 or newer.

```sh
pip install -r lab/requirements.txt
python lab/build_static.py     # hero, section headers, stack tiles, project cards
python lab/build_assay.py      # picoGym card, from data/picoctf.json
python lab/leetcode.py         # LeetCode card, from the public GraphQL API
python lab/vitals.py           # contributions card; needs GITHUB_TOKEN
python lab/check_profile.py
```

On PowerShell, set the token with `$env:GITHUB_TOKEN`. Keep credentials out of source files. The optional `LAB_TOKEN` Actions secret adds private contributions. `vitals.py --from-json` and `leetcode.py --from-json` redraw from a saved API response.

## What draws what

| Source | Output | README |
|---|---|---|
| `build_banner.py` | Hero (wide and narrow, each animated and still), contact cards | Hero, contact |
| `build_headers.py` | Section headers and the trophy shelf (wide and phone, animated and still) | Section headers, trophies |
| `build_shelf.py` | 48 px notched icon tiles with group labels | `STACK` |
| `build_projects.py` | Featured project sheet (wide and phone), then one lab sheet per project | `PROJECTS` |
| `vitals.py` | Contributions card: 12-month total, 26-week heatmap, streak | `CONTRIBUTIONS` |
| `leetcode.py` | LeetCode card: solved, difficulty meters, latest solve | `LEETCODE` |
| `build_assay.py` | picoGym card: one well per flag, top categories | `ASSAY` |
| `notebook.py` | Palette (`PAPER`), sheets, boxes, fonts, stepped motion, block editing | |
| `pixel.py` | Sprites from the portfolio's `lib/pixel-art.ts` | |
| `icons.py` | One-colour marks, copied as path data | |
| `check_profile.py` | Links, theme pairs, SVG integrity, markers, no Markdown headings | |

## Update the profile

- **Projects:** edit `PROJECTS` in `build_projects.py` (name, `repo` or `None` for private, optional `live` URL, one line, stack), then `build_static.py`. The first entry is featured and also needs `story` and `award`. A private project with a live demo links to the demo.
- **Tools:** edit `SHELF` in `build_shelf.py`.
- **picoGym:** edit `data/picoctf.json`, including its real `updated` date. picoCTF has no public API.
- **Trophies:** edit `WINS` in `build_headers.py`, newest first (`award`: `hack`, `medal`, or `ctf`). Use only real results.
- **Theme and type:** edit `BRAND`, `PAPER`, `FACES` and `TRACK` in `notebook.py`, then rerun everything.

## Motion

- Entrances: every sheet feeds in behind an ease-out moving neon/paper print-head line with a dithered trailing fringe and carriage brackets (`print_line_reveal`); the hero wordmark sweeps in left-to-right behind a matching horizontal phosphor scanline (`scan_reveal_x`). Semantic chunks (icons, copy, chips, trophies, stack tiles) then settle in reading order with a crisp 2-step upward nudge (`nudge_in`).
- Numbers race up and settle (ease-out over ten ticks), their unit moving with them. Header rules draw in block by block and the chevron lands last.
- Loops act instead of ticking: sprites follow stepped rhythms in `flip()` and `frames()`. The scientist waves three times and rests, the coil crackles unevenly, the monitor scrolls its ECG trace, flask bubbles climb, the 16×16 trophies and medallion catch a staggered 3-step diagonal sheen with a pixel rim sparkle, each project's pixel art runs a domain-specific micro-loop, and each live card pairs a staggered 8×8 source micro-sprite with a rare stepped chart sheen (no generic blinking LEDs). Project status lights stay still.
- Everything that loops ships a `-still` twin for `prefers-reduced-motion`. The finished frame is the base value, so a renderer without SMIL shows the final picture.
- SMIL runs only while an image is on screen, so cards animate as they scroll into view.

## Lab rounds

`.github/workflows/lab-rounds.yml` runs hourly at :37 and on edits to `data/picoctf.json`. It redraws the three live cards, checks the profile and commits only when a number changed.

See [font licenses](fonts/LICENSES.md).
