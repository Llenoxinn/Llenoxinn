# dexterslab: repository notes

Dexter Juevesano's (@Llenoxinn) GitHub profile. The theme is the portfolio's DOS blue, paper and lavender, but the voice and layout are the profile's own, modelled on notion.com/product/dev: a `/dev/dexter` hero, bracket-key paths (`[S] /stack`), tight Inter headlines, iA Writer Mono for commands, and cards with ink terminal strips. Every section of the README is drawn by `lab/`.

## Ground rules

- Never hand-edit generated `assets/`; change the generator and rerun it.
- README blocks between `<!-- NAME:START -->` and `<!-- NAME:END -->` belong to their generators. Preserve all five pairs: `STACK`, `PROJECTS`, `CONTRIBUTIONS`, `LEETCODE`, `ASSAY`.
- No Markdown headings: GitHub draws rule lines under them. Section headers are images from `build_headers.py`, wrapped in `<h3>` for structure.
- Brief copy. One short line per element; no paragraphs, no copying the portfolio's text word for word.
- Facts are real. No invented stats, solves, proficiency percentages, roles, proof URLs or tools. Private repos are labelled, never linked.
- Palette, card tokens and fonts live in `lab/notebook.py` (`BRAND`, `THEMES`, `SHEET`, `FACES`, `TRACK`). Keep data-semantic difficulty and CTF category colours.
- Every visual ships as `-dark` and `-light`. Anything that loops (hero, section headers, project, live and contact cards) also ships a `-still` twin that `<picture>` serves under `prefers-reduced-motion`; the hero adds `banner-narrow-*` for screens up to 600 px.
- Terminal lines type on a loop with a riding caret (`typed()` in `notebook.py`); other card content fades in once, opacity only. Stack tiles have no loop. Use outlined text, no fonts or icons fetched at render time, no SVG scripts; animation is SMIL.
- Cards are fixed-size inline images so rows wrap on phones: stack tiles 48 px, project and contact cards 376 px wide, live cards 252 px.

## Check changes

```sh
python lab/build_static.py
python lab/build_assay.py
python lab/check_profile.py
```

Preview light/dark and narrow/wide GitHub-style layouts in Chromium with the viewport grown to the page height (SMIL runs only on screen). Verify each image loads and that the page has no horizontal overflow. See `lab/README.md` for data commands and font licenses.

## Workflow

Lab rounds run hourly at :37 and redraw the contributions and LeetCode cards; edits to `lab/data/picoctf.json` redraw the picoGym card immediately. A commit happens only when a number changes. Optional secret `LAB_TOKEN` includes private contributions. The portfolio content file is the source for real CTF results and contact details.
