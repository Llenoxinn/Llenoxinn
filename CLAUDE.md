# dexterslab: repository notes

Dexter Juevesano's (@Llenoxinn) GitHub profile, drawn as an original 2000s real-time-strategy command console: riveted gunmetal plates with bevelled rims, gold-orange trim, chrome title lettering, glass orbs and recessed resource slots. Black Ops One for chrome titles, Russo One for headings and buttons, Barlow Condensed for text and labels, Teko for numbers. Every section of the README is drawn by `lab/`. Three earlier looks were copied or rejected and are retired: the Notion cards, the DOS-blue pixel "lab sheets" (copied bit by bit), and an amber instrument-panel re-skin. Do not bring them back, and never use AI-generated images: everything is drawn in vector by the generators.

The style is inspired by classic RTS HUDs (Battle Realms, C&C Generals) but every ornament, emblem, medal and glyph is original: no game logos, icons, emblems or artwork.

## Ground rules

- Never hand-edit generated `assets/`; change the generator and rerun it.
- README blocks between `<!-- NAME:START -->` and `<!-- NAME:END -->` belong to their generators. Preserve all five pairs: `STACK`, `PROJECTS`, `CONTRIBUTIONS`, `LEETCODE`, `ASSAY`. Order: hero title screen, commander console, units deployed (projects), medals earned (wins), training grounds (GitHub panel, then LeetCode and picoGym), build menu (stack), commands (contact).
- No Markdown headings: section titles are banner images from `build_headers.py`, wrapped in `<h3>`.
- Brief copy in plain sentences, in Dexter's voice. No middle-dot strings, no `CS @`, no em dashes.
- Facts are real. No invented stats, levels, ranks or counters. Private repos are labelled, never linked. GitHub numbers come from `vitals.py` (GraphQL), LeetCode from its public API, picoGym from `lab/data/picoctf.json`.
- Kit and paints live in `lab/rts.py` (`defs()`, `plaque()`, `well()`, `bar()`, `orb()`, `logo()`, `banner()`, `glint()`, `INK`); fonts in `FACES` in `lab/notebook.py`. Project logos are the projects' own favicons in `lab/data/logos/` (PlacebAIStudio from its live site, PhyTree from its build); projects without one get an original line glyph. Tool logos come from `lab/icons.py`.
- Every visual ships `-dark` and `-light`; anything animated also `-still`; full-width pieces (hero, console, banners, medals, hero unit, GitHub panel) add `-narrow` phone layouts served under `(max-width: 600px)`.
- Motion is purposeful and SMIL only: the hero radar sweeps and its contacts blink, chrome title and gold buttons catch a glint now and then, win orbs light in turn, resource slots fill, the minimap lifts its fog column by column, build slots come online one by one, medals catch a shine. The finished frame is the base value. No scripts, no fonts or images fetched at render time.
- Layout: everything sits on an 828 px column (`W` in `rts.py`): full pieces at 828, or two 412 halves per row (project plaques, LeetCode and picoGym, contact keys).

## Check changes

```sh
python lab/build_static.py
python lab/build_assay.py
python lab/check_profile.py
```

Preview light/dark and narrow/wide GitHub-style layouts in Chromium with the viewport grown to the page height. Verify each image loads and the page has no horizontal overflow.

## Workflow

Lab rounds run hourly at :37 and redraw the GitHub panel and LeetCode; edits to `lab/data/picoctf.json` redraw picoGym immediately. A commit happens only when a number changes. Optional secret `LAB_TOKEN` includes private contributions.
