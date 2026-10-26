# Lab equipment

Every figure on the profile is generated here: Python for the data and the 2D figures, Rust for the 3D renders.
Install once with `pip install -r lab/requirements.txt` (Python 3.12 or newer, like the workflow); the renderer builds itself on first use (`cargo build --release` in `render3d/`).

| Script | Makes | Runs |
|---|---|---|
| `build_banner.py` | `assets/banner-*.svg`: the animated banner (plotter portrait, scan, chromatogram, terminal) | by hand, after changing the photo or name |
| `wordmark.py` | the hive lettering for the name (used by the banner) | imported |
| `build_record.py` | `assets/record-*.svg`: the intake form | by hand; edit `FIELDS` |
| `build_drawers.py` | `assets/drawers/*`: cabinet fronts and pulled-out trays | by hand; edit `SPECIMENS` and `NOTES` |
| `specimen_of_the_day.py` | the colour turntable `assets/specimen-*.webp`, the label `specimen-*.svg`, the cartoon `specimen.stl`, and the SPECIMEN block with the README's one inline 3D viewer | nightly |
| `vitals.py` | bedside monitor (ECG weekly, PLETH daily, RESP monthly), plasmid pLLX (`helix.stl`), karyotype on a lab floor, metaphase spindle (`spindle.stl`), radial tree of life, and the VITALS and PHYLOGENY blocks; the two models open full-page from their renders | nightly (needs `GITHUB_TOKEN`) |
| `build_assay.py` | `assets/assay-*.svg`: a pipetting robot loads one well per picoGym flag, then the plate reader glows; and the ASSAY block, from `data/picoctf.json` | nightly and on every edit to the JSON |
| `build_stream.py` | `assets/stream-*.svg`: the bloodstream strips between sections, where the IDS engulfs a threat | by hand; edit `VARIANTS` |
| `build_shelf.py` | `assets/shelf-*.svg`: the stack as a reagent shelf | by hand; edit `SHELF` |
| `grow_culture.py` | `assets/culture-*.webp`, dissolving into the page at its edges, and the CULTURE block | Mondays |
| `build_notes.py` | `assets/eq-*.svg`: the typeset equations | by hand |
| `build_headers.py` | `assets/labels/*.svg`: the label-maker section headers | by hand |
| `turntable.py` | builds 3D scenes from data (cartoon protein, supercoiled plasmid, spindle) and turns renderer frames into animated WebP | imported |
| `render3d/` (Rust) | a dependency-free ray tracer: BVH, studio lights, shadows, ambient occlusion, bloom, depth fog, and a vignette into the exact page colour | called by `turntable.py` |
| `notebook.py` | shared palette, fonts, type-as-paths, the drifting `ambient()` layer, README block editing | imported |
| `stl.py` | tiny mesh builder for GitHub's 3D viewer (one inline viewer per page: GitHub gives up on the rest) | imported |

## Things you edit

- **picoGym**: `data/picoctf.json`. Per category: easy, medium and hard solves plus the category's total. Optional `score`, `rank`, `profile_url` and up to three `recent` captures. Push, and the plate redraws itself.
- **Portrait**: `data/portrait.png` is grayscale with an alpha mask around you. To change it, replace the file and run `python lab/build_banner.py`.
- **Stack**: add the security tools you actually use to `SHELF` in `build_shelf.py`.

## Palette and type

Red alert: `#ff1f3d` on near-black in dark mode, `#e0002a` on white in light mode, defined once in `notebook.THEMES`.
Type: Tektur letterforms grown into hex cells for the name, Jura for labels and text, Geist Mono for the terminal,
Nothing You Could Do for red-pen notes, Big Shoulders on the label tape. All under the SIL Open Font License (see `fonts/LICENSES.md`).
Lettering is drawn as vector paths, so every visitor sees the same type.
