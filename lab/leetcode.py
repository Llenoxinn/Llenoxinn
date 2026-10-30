#!/usr/bin/env python3
"""LeetCode progress from the public GraphQL API. assets/leetcode-{dark,light}.svg

Reads solved counts by difficulty, the question bank's size, languages, active days
and the latest accepted solutions, then fills the README's LEETCODE block. No token
is needed. If LeetCode is unreachable, the last reading stays up.

    python lab/leetcode.py
    python lab/leetcode.py --from-json snapshot.json    # redraw from a saved response
"""
import argparse
import datetime as dt
import json
import urllib.request

from notebook import (ASSETS, BRAND, MANILA, SHEET, STAT_H, STAT_W, THEMES, Typesetter, card, fade, footnote, readout,
                      replace_block, stamp, strip, strip_tag, svg_doc, themed)

HANDLE = "Acetylsphae"
PROFILE = f"https://leetcode.com/u/{HANDLE}/"
QUERY = """
query($u: String!) {
  allQuestionsCount { difficulty count }
  matchedUser(username: $u) {
    username
    submitStatsGlobal { acSubmissionNum { difficulty count } }
    languageProblemCount { languageName problemsSolved }
    userCalendar { totalActiveDays }
  }
  recentAcSubmissionList(username: $u, limit: 10) { title timestamp }
}"""
DIFF = ("Easy", "Medium", "Hard")


def fetch():
    body = json.dumps({"query": QUERY, "variables": {"u": HANDLE}}).encode()
    req = urllib.request.Request("https://leetcode.com/graphql", data=body, headers={
        "Content-Type": "application/json", "Referer": "https://leetcode.com", "User-Agent": "dexterslab-lab"})
    with urllib.request.urlopen(req, timeout=30) as r:
        data = json.load(r)
    if data.get("errors") or not (data.get("data") or {}).get("matchedUser"):
        raise RuntimeError(data.get("errors") or "user not found")
    return data["data"]


def analyse(data):
    user = data["matchedUser"]
    solved = {s["difficulty"]: s["count"] for s in user["submitStatsGlobal"]["acSubmissionNum"]}
    bank = {q["difficulty"]: q["count"] for q in data["allQuestionsCount"]}
    seen, recent = set(), []
    for s in data.get("recentAcSubmissionList") or []:   # newest first; a problem can repeat
        if s["title"] not in seen:
            seen.add(s["title"])
            recent.append((s["title"], dt.datetime.fromtimestamp(int(s["timestamp"]), MANILA).date()))
    langs = sorted(((l["languageName"], l["problemsSolved"]) for l in user["languageProblemCount"] or []
                    if l["problemsSolved"]), key=lambda x: -x[1])
    return dict(solved=solved, bank=bank, recent=recent, langs=langs,
                active=(user.get("userCalendar") or {}).get("totalActiveDays") or 0)


def day(d):
    return f"{d.day} {d:%b}"


def leetcard(v, theme):
    """LeetCode card: problems solved, then one segmented meter per difficulty against the question bank."""
    s = SHEET[theme]
    ts = Typesetter("lc")
    total = v["solved"].get("All", 0)
    head, typed = strip(ts, STAT_W, 0, [("leetcode", BRAND["lavender"]), (" > ", BRAND["neon"]),
                                        (HANDLE.lower(), BRAND["paper"])], start=0.1, top=True)
    body = [card(theme, STAT_W, STAT_H), head, strip_tag(ts, STAT_W, "live", live=True),
            readout(ts, theme, total, "solved", typed + 0.1)]
    x0, x1, seg = 76, 196, 7.5
    for k, level in enumerate(DIFF):
        y = 112 + k * 24
        got, of = v["solved"].get(level, 0), v["bank"].get(level, 0)
        colour = s[level.lower()]
        body.append(ts.text(level, "code", 12, 14, y, colour)[0])
        body.append(ts.text(str(got), "code-bold", 12, STAT_W - 14, y, s["text"], anchor="end")[0])
        count = round((x1 - x0) / seg)
        lit = min(count, -(-got * count // of)) if got and of else 0
        for i in range(count):
            fill = colour if i < lit else s["well"]
            anim = fade(typed + 0.3 + k * 0.1 + i * 0.03, 0.15) if i < lit else ""
            body.append(f'<rect x="{x0 + i * seg:.1f}" y="{y - 9}" width="{seg - 2}" height="10" rx="1" fill="{fill}">{anim}</rect>')
    latest = f"latest: {v['recent'][0][0]}" if v["recent"] else f"{v['active']} active days"
    body.append(footnote(ts, theme, latest, typed + 0.9))
    split = ", ".join(f"{v['solved'].get(l, 0)} {l.lower()}" for l in DIFF)
    label = (f"LeetCode @{HANDLE}: {total} problems solved ({split}) over {v['active']} active days"
             + (f"; latest {v['recent'][0][0]}, {day(v['recent'][0][1])}." if v["recent"] else "."))
    return svg_doc(STAT_W, STAT_H, ts.defs_svg() + "".join(body), label), label


def write(v):
    svgs = {theme: leetcard(v, theme) for theme in THEMES}
    for theme, (svg, _) in svgs.items():
        (ASSETS / f"leetcode-{theme}.svg").write_text(svg, encoding="utf-8")
    pic = themed("leetcode", svgs["light"][1], STAT_W, STAT_H, query="v=" + stamp(svgs["light"][0]))
    changed = replace_block("LEETCODE", f'<a href="{PROFILE}">{pic}</a>')
    print(f"leetcode: {v['solved'].get('All', 0)} solved, README {'updated' if changed else 'unchanged'}")


def main():
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--from-json", help="read a saved GraphQL `data` object instead of calling the API")
    args = ap.parse_args()
    if args.from_json:
        data = json.load(open(args.from_json, encoding="utf-8"))
    else:
        try:
            data = fetch()
        except Exception as e:  # noqa: BLE001 - keep the last reading rather than fail the rounds
            print(f"::warning::LeetCode unavailable, keeping the last reading ({e})")
            return
    write(analyse(data))


if __name__ == "__main__":
    main()
