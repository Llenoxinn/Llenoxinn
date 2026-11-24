#!/usr/bin/env python3
"""LeetCode progress from the public GraphQL API. assets/leetcode-{dark,light}.svg and stills

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

from notebook import ASSETS, MANILA, THEMES, Typesetter, count_up, replace_block, scene, stamp, svg_doc
from rts import HALF, INK, bar, defs, plaque, text

PANEL_H = 236
COLOURS = {"Easy": "#3fb950", "Medium": "#ffb02e", "Hard": "#ff5c6c"}

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
    """LeetCode production panel: problems solved, then one slot per difficulty filling to its share."""
    ts = Typesetter("lc")
    total = v["solved"].get("All", 0)
    body = [defs(), plaque(0, 0, HALF, PANEL_H),
            text(ts, "LEETCODE", "head", 15, 16, 30, "url(#orange)", track=.1),
            text(ts, f"@{HANDLE}", "semi", 14, HALF - 16, 30, INK["muted"], anchor="end"),
            count_up(lambda n: text(ts, f"{n:,}", "num", 52, 16, 86, INK["text"]), total, 0.3 if animate else None),
            text(ts, "SOLVED", "bold", 12, 80, 68, INK["muted"], track=.14),
            text(ts, f"{v['active']} ACTIVE DAYS", "bold", 12, 80, 84, INK["gold"], track=.12)]
    for k, level in enumerate(DIFF):
        got = v["solved"].get(level, 0)
        body.append(bar(ts, 16, 118 + k * 32, HALF - 32, got / total if total else 0, COLOURS[level], level, str(got),
                        0.5 + k * .12 if animate else None))
    latest = (f"LATEST: {v['recent'][0][0].upper()}, {day(v['recent'][0][1]).upper()}" if v["recent"] else "")
    body.append(text(ts, latest[:58], "bold", 10.5, 16, PANEL_H - 14, INK["dim"], track=.08))
    split = ", ".join(f"{v['solved'].get(l, 0)} {l.lower()}" for l in DIFF)
    label_ = (f"LeetCode @{HANDLE}: {total} problems solved ({split}) over {v['active']} active days"
              + (f"; latest {v['recent'][0][0]}, {day(v['recent'][0][1])}." if v["recent"] else "."))
    return svg_doc(HALF, PANEL_H, ts.defs_svg() + "".join(body), label_), label_


def write(v):
    svgs = {theme: leetcard(v, theme) for theme in THEMES}
    for theme, (svg, _) in svgs.items():
        (ASSETS / f"leetcode-{theme}.svg").write_text(svg, encoding="utf-8")
        (ASSETS / f"leetcode-still-{theme}.svg").write_text(leetcard(v, theme, False)[0], encoding="utf-8")
    pic = scene("leetcode", svgs["light"][1], HALF, PANEL_H, query="v=" + stamp(svgs["light"][0]))
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
