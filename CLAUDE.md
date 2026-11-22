# dexterslab: repository notes

Dexter Juevesano's (@Llenoxinn) GitHub profile, drawn in the language of the live portfolio (dexterslab-dev.vercel.app): DOS blue, paper and lavender; a pixel lab at night for the hero; "lab sheets" for cards (torn pixel edges, notched square corners, a hard offset shadow, no rounded bezels); Pixelify Sans for words in tags and the wordmark, Chakra Petch for text and all digits, Inter Bold for titles. Every section of the README is drawn by `lab/`. The Nov 2026 redesign replaced the Notion-style cards (terminal strips, typed commands, `[S] /dev` paths) after they were copied; do not bring those back.

## Ground rules

- Never hand-edit generated `assets/`; change the generator and rerun it.
- README blocks between `<!-- NAME:START -->` and `<!-- NAME:END -->` belong to their generators. Preserve all five pairs: `STACK`, `PROJECTS`, `CONTRIBUTIONS`, `LEETCODE`, `ASSAY`. Section order: hero, projects, trophies, stack, readings, contact.
- No Markdown headings: GitHub draws rule lines under them. Section headers are images from `build_headers.py`, wrapped in `<h3>` for structure.
- Brief copy. One short line per element; no paragraphs, no copying the portfolio's text word for word.
- Facts are real. No invented stats, solves, proficiency percentages, roles, proof URLs or tools. Private repos are labelled, never linked.
- Palette, card tokens and fonts live in `lab/notebook.py` (`BRAND`, `PAPER`, `FACES`, `TRACK`; `sheet()`, `box()`, `reading()`). Keep data-semantic difficulty and CTF category colours. Pixelify's 2, 5 and B misread at small sizes: never set digits in it.
- Every visual ships as `-dark` and `-light`. Anything that loops (hero, section headers, project, trophy, live and contact cards) also ships a `-still` twin that `<picture>` serves under `prefers-reduced-motion`; the hero adds `banner-narrow-*` for screens up to 600 px.
- Motion is stepped, like a sprite, never eased: cards print in top to bottom in hard bands (`print_clip`), parts cut in (`step_in`), numbers tick up (`count_up`), pixel art swaps two frames (`flip`, `hop`), LEDs blink (`blink`). No fades, typing or travelling packets. Stack tiles have no loop. The finished frame is always the base value, so non-SMIL renderers show it. Use outlined text, no fonts or icons fetched at render time, no SVG scripts; animation is SMIL.
- Cards are fixed-size inline images so rows wrap on phones: stack tiles 48 px; project (376 × 104), trophy (376 × 100) and contact (376 × 92) cards; live cards 252 × 188.
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
