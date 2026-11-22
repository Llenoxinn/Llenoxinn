# dexterslab: repository notes

Dexter Juevesano's (@Llenoxinn) GitHub profile, drawn in the language of the live portfolio (dexterslab-dev.vercel.app): DOS blue, paper and lavender; a pixel lab at night for the hero; "lab sheets" for cards (torn pixel edges, notched square corners, a hard offset shadow, no rounded bezels); Pixelify Sans for words in tags and the wordmark, Chakra Petch for text and all digits, Inter Bold for titles. Every section of the README is drawn by `lab/`. The Nov 2026 redesign replaced the Notion-style cards (terminal strips, typed commands, `[S] /dev` paths) after they were copied; do not bring those back.

## Ground rules

- Never hand-edit generated `assets/`; change the generator and rerun it.
- README blocks between `<!-- NAME:START -->` and `<!-- NAME:END -->` belong to their generators. Preserve all five pairs: `STACK`, `PROJECTS`, `CONTRIBUTIONS`, `LEETCODE`, `ASSAY`. Section order: hero, projects, trophies, stack, readings, contact.
- No Markdown headings: GitHub draws rule lines under them. Section headers are images from `build_headers.py`, wrapped in `<h3>` for structure.
- Brief copy in plain sentences, in Dexter's voice. One short line per element; no paragraphs, no copying the portfolio's text word for word. No middle-dot strings (`A · B · C`), no `CS @` shorthand, no locale or time-zone strips.
- Facts are real. No invented stats, solves, proficiency percentages, roles, proof URLs or tools. Private repos are labelled, never linked.
- Palette, card tokens and fonts live in `lab/notebook.py` (`BRAND`, `PAPER`, `FACES`, `TRACK`; `sheet()`, `box()`, `reading()`). Keep data-semantic difficulty and CTF category colours. Pixelify's 2, 5 and B misread at small sizes: never set digits in it.
- Every visual ships as `-dark` and `-light`. Anything that loops (hero, section headers, featured sheet, project cards, trophy shelf, live and contact cards) also ships a `-still` twin that `<picture>` serves under `prefers-reduced-motion`; the hero adds `banner-narrow-*` for screens up to 600 px.
- Motion is stepped, like a sprite, and every piece has one job. Sheets resolve out of an ordered pixel dither that sweeps downward, with a different dither offset per card (`materialize`); parts cut in (`step_in`); numbers race up and settle with their unit travelling beside them (`count_up`); header rules draw in once; the heatmap lands along diagonals. Loops are few and act rather than tick: sprites follow a `rhythm` string (`flip`: the scientist waves three times then rests, the coil crackles unevenly, cups glint once in a while), one LED per live card flickers now and then. Project icons and status lights stay still. No fades, typing or travelling packets. The finished frame is always the base value, so non-SMIL renderers show it. Use outlined text, no fonts or icons fetched at render time, no SVG scripts; animation is SMIL.
- Layout: below the full-width hero, everything sits on one 760 px column (`COLUMN` in `notebook.py`): two 376 cards or three 252 cards per row, and full-column pieces displayed at `width="760"`. Full-column pieces (section headers, the featured project sheet, the trophy shelf) also ship a 400 px phone layout served under `(max-width: 600px)` via `wide_scene()`. Fixed sizes: stack tiles 48 px; project (376 × 104) and contact (376 × 92) cards; live cards 252 × 188.
- Hierarchy: the first project in `PROJECTS` is the featured sheet (big pixel art, story, award band, full stack); the rest are cards. Results all stand on one trophy shelf (`WINS` in `build_headers.py`; `award` is `trophy` or `medal`).
- Sprites come from the portfolio's `lib/pixel-art.ts` (copied into `lab/pixel.py`).

## Check changes

```sh
python lab/build_static.py
python lab/build_assay.py
python lab/check_profile.py
```

Preview light/dark and narrow/wide GitHub-style layouts in Chromium with the viewport grown to the page height (SMIL runs only on screen). Verify each image loads and that the page has no horizontal overflow. See `lab/README.md` for data commands and font licenses.

## Workflow

Lab rounds run hourly at :37 and redraw the contributions and LeetCode cards; edits to `lab/data/picoctf.json` redraw the picoGym card immediately. A commit happens only when a number changes. Optional secret `LAB_TOKEN` includes private contributions. The portfolio content file is the source for real CTF results and contact details.
