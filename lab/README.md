# dexterslab: lab equipment

This folder draws every picture on the GitHub profile. The palette is the portfolio's DOS blue, paper and lavender; the layout and type follow notion.com/product/dev: Inter headlines with tight tracking, iA Writer Mono for commands, bracket-key paths and cards with ink terminal strips.

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
| `build_headers.py` | Section headers (animated and still), CTF result cards | Section headers, CTF cards |
| `build_shelf.py` | 48 px icon tiles with `lang/`, `web/` … labels | `STACK` |
| `build_projects.py` | One card per project: pixel icon, one line, typed stack | `PROJECTS` |
| `vitals.py` | Contributions card: 12-month total, 26-week heatmap, streak | `CONTRIBUTIONS` |
| `leetcode.py` | LeetCode card: solved, difficulty meters, latest solve | `LEETCODE` |
| `build_assay.py` | picoGym card: one well per flag, top categories | `ASSAY` |
| `notebook.py` | Palette, card tokens, fonts, motion helpers, block editing | |
| `icons.py` | One-colour marks, copied as path data | |
| `check_profile.py` | Links, theme pairs, SVG integrity, markers, no Markdown headings | |

## Update the profile

- **Projects:** edit `PROJECTS` in `build_projects.py` (name, repo or `None` for private, one line, stack), then `build_static.py`.
- **Tools:** edit `SHELF` in `build_shelf.py`.
- **picoGym:** edit `data/picoctf.json`, including its real `updated` date. picoCTF has no public API.
- **CTF results:** edit `WINS` in `build_headers.py`. Use only real results.
- **Theme and type:** edit `BRAND`, `SHEET`, `FACES` and `TRACK` in `notebook.py`, then rerun everything.

## Motion

- The hero and section headers loop softly: twinkling dots that fade out around the icon, packets on circuit traces, floating toasts, a brief title glitch.
- Every terminal line (hero pill, project stacks, live commands, contact URLs) types, holds, clears and types again, with a caret that rides along and blinks.
- Live cards keep a quiet pulse: today's heatmap cell breathes, the newest LeetCode segment charges, a scan line sweeps the picoGym plate; project icons get a passing scan line.
- Everything that loops ships a `-still` twin for `prefers-reduced-motion`. Other card content fades in once, in reading order. Nothing moves position except the hero.
- SMIL runs only while an image is on screen, so cards animate as they scroll into view.

## Lab rounds

`.github/workflows/lab-rounds.yml` runs hourly at :37 and on edits to `data/picoctf.json`. It redraws the three live cards, checks the profile and commits only when a number changed.

`specimen_of_the_day.py`, `grow_culture.py`, `turntable.py`, `render3d/` and `vitals.py --telemetry` belong to the earlier lab section. They are no longer on the profile or in the workflow.

See [font licenses](fonts/LICENSES.md).
