#!/usr/bin/env python3
"""LeetCode progress from the public GraphQL API, shown on the lab console's Nixie counter.

Reads solved counts by difficulty and active days, saves them to lab/data/leetcode.json,
redraws assets/live/leetcode-*.svg and refills the LEETCODE block. No token is needed.
If LeetCode is unreachable, the last reading stays up.

    python lab/leetcode.py
    python lab/leetcode.py --from-json snapshot.json    # redraw from a saved response
"""
import argparse
import datetime as dt
import json
import urllib.request

import console
from notebook import MANILA, ROOT

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


def write(v):
    out = dict(_how="Written by lab/leetcode.py every lab round.", handle=HANDLE,
               solved={k: v["solved"].get(k, 0) for k in DIFF}, active=v["active"])
    (ROOT / "lab" / "data" / "leetcode.json").write_text(json.dumps(out, indent=1) + "\n", encoding="utf-8")
    changed = console.write_live("leetcode")
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
