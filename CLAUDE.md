# DEXTER / XED: repository notes

Dexter Juevesano's (@Llenoxinn) GitHub profile, drawn as a cartoon lab in the late-90s TV-cartoon style. The light theme is **DEXTER** ("I build things that ship."); the dark theme is **XED** ("I break things to see how they work."), the same lab after hours, wrecked and spilling. GitHub's theme setting decides who a visitor meets. Both themes show the same facts and links; only art, palette, texture and captions differ. Every section of the README is drawn by `lab/`. Two earlier designs (Notion cards, then DOS-blue pixel lab sheets) were copied; never bring either back, nor pixel art.

## Ground rules

- Never hand-edit generated `assets/`; change the generator and rerun it. `lab/build_lab.py` writes `README.md` too.
- README blocks between `<!-- NAME:START -->` and `<!-- NAME:END -->` belong to their generators. Preserve all five pairs: `STACK`, `PROJECTS`, `CONTRIBUTIONS`, `LEETCODE`, `ASSAY`. Section order: hero, projects, trophies, stack, readings, contact.
- No Markdown headings: GitHub draws rule lines under them. Section headers are images, wrapped in `<h3>`.
- XED renames the sections: Projects → Experiments, Trophies → Loot, Stack → Chemicals, Readings → Vitals, Contact → Signal (`TITLES` in `panels.py`). Header lines are (DEXTER, XED) pairs in `rooms.LINES`.
- Brief copy in plain sentences, in Dexter's voice. One short line per element. No middle-dot strings (`A · B · C`), no `CS @` shorthand, no locale or time-zone strips.
- Facts are real. No invented stats, solves, roles, proof URLs or tools. Private repos are labelled, never linked.

## The character

- Dexter himself, in the show's cartoon construction: black warrior cut (spiky top, chunky fringe), thick half-rim browline glasses, crimson welding gauntlets, rolled-sleeve bone lab coat with a phoenix patch (`lab/kid.py`).
- Never the show's character or cast: no orange hair, no purple gloves, no pale-blue rectangle lenses, no show names or logos.
- XED: one brow cocked, wide grin, one lens spider-webbed and the other blown out, bridge taped, fringe smoking, spill on coat, sleeve, gauntlet and cheek, lit from below by fire.
- Hero: DEXTER punches the gold DEX and TER blocks forward; XED turns the DEX block over so it reads XED, and every few seconds it turns back and snaps over again in stepped frames.

## Look

- Palette, ink and texture live in `lab/toon.py` (`PHOENIX`): bone, prussian/navy, crimson/oxblood, phoenix orange, gold, and acid spill `#A6FF2E`. Gold is the shared mark of both themes. Keep data-semantic LeetCode difficulty colours.
- Ink: near-black union outlines (an ink copy stroked at 2x under the fill), tapered `fold()` slivers for interior marks, one hard cel step per form, the `grain` filter gathered at fill edges, `paper` tooth over each scene.
- Type is outlined at build time from `lab/fonts` (`FACES` in `notebook.py`): Creepster for the wordmark and headers, no font on the gold blocks: their DEX/TER letters are drawn by hand in `lab/letters.py` (pale gold for DEXTER, crimson enamel for XED), Chakra Petch for text and all digits.
- Every object is grounded: it stands on a shelf, bench or console, hangs from a nail or chain, is screwed or bolted on, or plugs into something. No floating boxes or lines.
- XED's mess (spill, scorch, cracks, tape) goes on frames, corners and walls, never over a name, number or tag. Vary it card to card.
- Project cards have no pictures: name, where the code lives, one line, the full stack as text chips. Only the featured project (the first in `panels.FEATURE`) gets a painted scene.

## Motion

- SMIL only, stepped like cartoon timing on twos: snaps, holds and small overshoots. No fades, typing, easing or travelling packets.
- The finished frame is always the base value, so non-SMIL renderers show it. Outlined text only, no fonts or icons fetched at render time, no SVG scripts.
- Every visual ships `-dark` and `-light`. Anything that moves also ships a `-still` twin that `<picture>` serves under `prefers-reduced-motion`. Full-column pieces (hero, headers, featured scene, trophy wall, stack cabinet) also ship `-narrow` for screens up to 600 px. `check_profile.py` enforces the still twins.

## Layout

Below the full-width hero, everything sits on one 760 px column: two 376 cards per row (projects, contact) or three 252 × 300 console tiles; full-column pieces display at `width="760"`. Fixed sizes: project 376 × 104, contact 376 × 92.

## Check changes

```sh
python lab/build_static.py
python lab/build_assay.py
python lab/check_profile.py
```

Preview light/dark and narrow/wide GitHub-style layouts in Chromium, scrolling through the page (SMIL runs only on screen). Verify each image loads and that the page has no horizontal overflow. See `lab/README.md` for what draws what and font licenses.

## Workflow

Lab rounds run hourly at :37: `vitals.py` and `leetcode.py` save their readings to `lab/data/github.json` and `lab/data/leetcode.json` and redraw only their console tile; edits to `lab/data/picoctf.json` redraw the picoGym rack immediately. A commit happens only when a number changes. Optional secret `LAB_TOKEN` includes private contributions. The portfolio content file is the source for real CTF results and contact details.
