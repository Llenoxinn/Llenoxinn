# dexterslab: lab equipment

This folder draws every picture on the GitHub profile as one original RTS command console: riveted gunmetal plates, gold trim, chrome lettering, glass orbs and resource slots (kit in `rts.py`). Black Ops One, Russo One, Barlow Condensed and Teko.

## Run the lab

Use Python 3.12 or newer.

```sh
pip install -r lab/requirements.txt
python lab/build_static.py     # hero, section headers, trophy case, stack keys, projects
python lab/build_assay.py      # picoGym module, from data/picoctf.json
python lab/leetcode.py         # LeetCode module, from the public GraphQL API
python lab/vitals.py           # GitHub panel; needs GITHUB_TOKEN
python lab/check_profile.py
```

On PowerShell, set the token with `$env:GITHUB_TOKEN`. Keep credentials out of source files. The optional `LAB_TOKEN` Actions secret adds private contributions. `vitals.py --from-json` and `leetcode.py --from-json` redraw from a saved API response.

## What draws what

| Source | Output | README |
|---|---|---|
| `build_banner.py` | Hero title screen, commander console, contact command keys | Hero, console, commands |
| `build_headers.py` | Section banners and the medals plaque | Banners, medals |
| `build_projects.py` | Hero unit and unit plaques with each project's own logo | `PROJECTS` |
| `vitals.py` | GitHub training panel: contributions, PRs merged, issues closed, commits, streak, minimap, languages | `CONTRIBUTIONS` |
| `leetcode.py`, `build_assay.py` | LeetCode and picoGym production panels | `LEETCODE`, `ASSAY` |
| `build_shelf.py` | Build menu: one steel slot per tool, gold group plates | `STACK` |
| `rts.py`, `notebook.py` | Kit and paints; type as paths, block editing, motion helpers | |
| `icons.py`, `data/logos/` | Tool marks; project logos | |
| `check_profile.py` | Links, theme pairs, SVG integrity, markers, no Markdown headings | |

## Lab rounds

`.github/workflows/lab-rounds.yml` runs hourly at :37 and on edits to `data/picoctf.json`, redraws the three live panels, checks the profile and commits only when a number changed.

See [font licenses](fonts/LICENSES.md).
