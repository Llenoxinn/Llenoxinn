# DEXTER / XED: lab equipment

This folder draws every picture on the GitHub profile. The light theme is **DEXTER** ("I build things that ship"), and the dark theme is **XED** ("I break things to see how they work"), the same lab after hours. Both are a cartoon lab drawn by hand in code: thick ink outlines, flat fills with one hard cel step, a fine gouache grain gathered at the edges, and the phoenix palette with acid-green spill.

## Run the lab

Use Python 3.12 or newer.

```sh
pip install -r lab/requirements.txt
python lab/build_static.py     # the whole profile, then content-hash every image URL
python lab/build_assay.py      # picoGym rack, from data/picoctf.json
python lab/leetcode.py         # LeetCode Nixie counter, from the public GraphQL API
python lab/vitals.py           # GitHub scope; needs GITHUB_TOKEN
python lab/check_profile.py
```

On PowerShell, set the token with `$env:GITHUB_TOKEN`. Keep credentials out of source files. The optional `LAB_TOKEN` Actions secret adds private contributions. `vitals.py --from-json` and `leetcode.py --from-json` redraw from a saved API response.

## What draws what

| Source | Draws | README |
|---|---|---|
| `build_lab.py` | Calls everything below and writes `README.md` | the whole page |
| `build_hero.py` | Hero: Dexter behind the DEX/TER gold blocks, the hanging nameplate, the lab; XED turns the DEX block over | Hero |
| `panels.py` | Section headers (title on a wall shelf) and the featured project as a painted lab scene | Headers, first card of `PROJECTS` |
| `rooms.py` | Project drawers, trophy wall, chemical cabinet (stack), contact intercoms | `PROJECTS`, trophies, `STACK`, contact |
| `console.py` | The readings console: GitHub scope, LeetCode Nixie counter, picoGym tube rack, one tile each | `CONTRIBUTIONS`, `LEETCODE`, `ASSAY` |
| `vitals.py`, `leetcode.py`, `build_assay.py` | Fetch a reading, save it to `data/`, redraw one console tile | one live block each |
| `kid.py` | Dexter as a cartoon (warrior cut, browline glasses, crimson gauntlets) and the spill splats | |
| `toon.py` | Palette (`PHOENIX`), ink outlines, tapered folds, clips, the grain and paper filters | |
| `notebook.py` | Fonts as outlined paths, `svg_doc`, `<picture>` helpers, README block editing | |
| `icons.py` | One-colour marks for the stack jars and contact buttons | |
| `check_profile.py` | Links, theme pairs, still twins, phone layouts, SVG integrity, markers, no Markdown headings | |

## Update the profile

- **Featured project:** `FEATURE` in `panels.py`.
- **Projects:** `PROJECTS` (name, `repo` or `None` for private, one line, where the code lives) and `STACKS` in `rooms.py`.
- **Trophies:** `WINS` in `rooms.py`. Use only real results.
- **Tools:** `SHELF` in `rooms.py`.
- **Header lines:** `LINES` in `rooms.py`, as (DEXTER, XED). XED's section names are `TITLES` in `panels.py`.
- **picoGym:** edit `data/picoctf.json`, including its real `updated` date. picoCTF has no public API.
- **Palette and type:** `PHOENIX` in `toon.py` and `FACES` in `notebook.py`, then rerun everything.

Then run `python lab/build_static.py` and `python lab/check_profile.py`.

## Rules the drawings follow

- Every object stands on, hangs from, is screwed to or plugs into something. Nothing floats.
- Readouts stay clean in both themes. XED's mess (spill, scorch, cracks, tape) goes on frames, corners and walls, never over a name or a number.
- Every picture ships `-light` and `-dark`. Anything that moves also ships `-still`, and full-column pieces also ship `-narrow` for screens up to 600 px.
- Motion is stepped, never eased or faded. The finished frame is the base value, so a renderer without SMIL shows the final picture. SMIL runs only while an image is on screen, so pieces animate as they scroll into view.
- Text is outlined from the fonts in `fonts/`. Nothing is fetched at render time, and there are no SVG scripts.

## Lab rounds

`.github/workflows/lab-rounds.yml` runs hourly at :37 and on edits to `data/picoctf.json`. It refreshes the three console tiles, checks the profile and commits only when a number changes.

## Painted backplates (optional)

`python lab/build_hero.py --preview --plates` writes the bare hero set. Paint it in Code Painter (paint.jas.black, riso or acrylic with vector outlines on), then save it as `plates/hero-<wide|narrow>-<light|dark>.png`. The hero then uses it in place of the vector wall. Code Painter is © JAS.BLACK; only its output is used here.

See [font licenses](fonts/LICENSES.md).
