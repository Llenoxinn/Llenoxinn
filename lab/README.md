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
| `build_headers.py` | Section headers (animated and still), trophy cards | Section headers, trophies |
| `build_shelf.py` | 48 px notched icon tiles with group labels | `STACK` |
| `build_projects.py` | One lab sheet per project: pixel icon, one line, stack chips | `PROJECTS` |
| `vitals.py` | Contributions card: 12-month total, 26-week heatmap, streak | `CONTRIBUTIONS` |
| `leetcode.py` | LeetCode card: solved, difficulty meters, latest solve | `LEETCODE` |
| `build_assay.py` | picoGym card: one well per flag, top categories | `ASSAY` |
| `notebook.py` | Palette (`PAPER`), sheets, boxes, fonts, stepped motion, block editing | |
| `pixel.py` | Sprites from the portfolio's `lib/pixel-art.ts` | |
| `icons.py` | One-colour marks, copied as path data | |
| `check_profile.py` | Links, theme pairs, SVG integrity, markers, no Markdown headings | |

## Update the profile

- **Projects:** edit `PROJECTS` in `build_projects.py` (name, `repo` or `None` for private, optional `live` URL, one line, stack), then `build_static.py`. A private project with a live demo links to the demo.
- **Tools:** edit `SHELF` in `build_shelf.py`.
- **picoGym:** edit `data/picoctf.json`, including its real `updated` date. picoCTF has no public API.
- **Trophies:** edit `WINS` in `build_headers.py`, newest first, and the trophy row in the README. Use only real results.
- **Theme and type:** edit `BRAND`, `PAPER`, `FACES` and `TRACK` in `notebook.py`, then rerun everything.

## Motion

- Stepped, never eased. Cards print in top to bottom in ten hard bands, then their chips and cells cut in one by one.
- Big numbers tick up through eight values and hold.
- Sprites play two frames: the scientist waves, the Tesla coil sparks, the flask bubbles, the orb crackles, the trophy glints. Project icons hop one pixel; chevrons step right; LEDs blink.
- Everything that loops ships a `-still` twin for `prefers-reduced-motion`. The finished frame is the base value, so a renderer without SMIL shows the final picture.
- SMIL runs only while an image is on screen, so cards animate as they scroll into view.

## Lab rounds

`.github/workflows/lab-rounds.yml` runs hourly at :37 and on edits to `data/picoctf.json`. It redraws the three live cards, checks the profile and commits only when a number changed.

`specimen_of_the_day.py`, `grow_culture.py`, `turntable.py`, `render3d/` and `vitals.py --telemetry` belong to the earlier lab section. They are no longer on the profile or in the workflow.

See [font licenses](fonts/LICENSES.md).
