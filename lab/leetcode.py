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

from notebook import (ASSETS, MANILA, PAPER, SHADE, STAT_H, STAT_W, THEMES, Typesetter, blink, foot, printed, reading,
                      replace_block, scene, stamp, step_in, svg_doc)

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


def leetcard(v, theme, animate=True):
    """LeetCode card: problems solved ticks up, then one block meter per difficulty against the question bank."""
    s = PAPER[theme]
    ts = Typesetter("lc")
    total = v["solved"].get("All", 0)
    body = reading(ts, theme, "leet", "LEETCODE", f"@{HANDLE}", total, "solved", animate)
    right = STAT_W - SHADE - 14
    x0, x1, seg = 80, right - 30, 8
    for k, level in enumerate(DIFF):
        y = 100 + k * 21
        got, of = v["solved"].get(level, 0), v["bank"].get(level, 0)
        colour = s[level.lower()]
        body.append(ts.text(level, "body-bold", 12.5, 14, y, colour)[0])
        body.append(ts.text(str(got), "body-bold", 12.5, right, y, s["text"], anchor="end")[0])
        count = int((x1 - x0) // seg)
        lit = min(count, -(-got * count // of)) if got and of else 0
        blocks = []
        for i in range(count):
            on = i < lit
            motion = step_in(0.8 + k * 0.12 + i * 0.03) if animate and on else ""
            if animate and i == lit - 1:     # the newest block keeps blinking
                motion += blink(1.2, 2.5, low=0.35)
            blocks.append(f'<rect x="{x0 + i * seg}" y="{y - 10}" width="{seg - 2}" height="11" '
                          f'fill="{colour if on else s["well"]}">{motion}</rect>')
        body.append(f'<g shape-rendering="crispEdges">{"".join(blocks)}</g>')
    latest = f"latest: {v['recent'][0][0]}" if v["recent"] else f"{v['active']} active days"
    body.append(foot(ts, theme, latest))
    split = ", ".join(f"{v['solved'].get(l, 0)} {l.lower()}" for l in DIFF)
    label = (f"LeetCode @{HANDLE}: {total} problems solved ({split}) over {v['active']} active days"
             + (f"; latest {v['recent'][0][0]}, {day(v['recent'][0][1])}." if v["recent"] else "."))
    return svg_doc(STAT_W, STAT_H, ts.defs_svg() + printed("lcp", STAT_W, STAT_H, body, animate), label), label


def write(v):
    svgs = {theme: leetcard(v, theme) for theme in THEMES}
    for theme, (svg, _) in svgs.items():
        (ASSETS / f"leetcode-{theme}.svg").write_text(svg, encoding="utf-8")
        (ASSETS / f"leetcode-still-{theme}.svg").write_text(leetcard(v, theme, False)[0], encoding="utf-8")
    pic = scene("leetcode", svgs["light"][1], STAT_W, STAT_H, query="v=" + stamp(svgs["light"][0]))
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
