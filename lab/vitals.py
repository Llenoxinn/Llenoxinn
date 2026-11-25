#!/usr/bin/env python3
"""Read GitHub contributions from the GitHub API and redraw the scope on the lab console.

Needs a token in GITHUB_TOKEN (the workflow's own token is enough; LAB_TOKEN adds
private contributions). Saves the reading to lab/data/github.json, redraws
assets/live/github-*.svg and refills the CONTRIBUTIONS block.

    GITHUB_TOKEN=... python lab/vitals.py
    python lab/vitals.py --from-json snapshot.json    # redraw from a saved API response
"""
import argparse
import datetime as dt
import json
import os
import sys
import urllib.request

import console
from notebook import ROOT, USER

PROFILE_REPO = USER                 # the profile repo itself: lab code, not your work
QUERY = """
query($login: String!) {
  user(login: $login) {
    createdAt
    followers { totalCount }
    repositories(ownerAffiliations: OWNER, privacy: PUBLIC, isFork: false, first: 100,
                 orderBy: {field: PUSHED_AT, direction: DESC}) {
      totalCount
      nodes {
        name stargazerCount forkCount pushedAt
        primaryLanguage { name color }
        languages(first: 12, orderBy: {field: SIZE, direction: DESC}) { edges { size node { name color } } }
      }
    }
    contributionsCollection {
      totalCommitContributions totalPullRequestContributions totalIssueContributions
      restrictedContributionsCount
      contributionCalendar { totalContributions weeks { contributionDays { date contributionCount } } }
    }
  }
}"""
WEEKDAYS = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]


# ------------------------------------------------------------------ data

def fetch(token):
    body = json.dumps({"query": QUERY, "variables": {"login": USER}}).encode()
    req = urllib.request.Request("https://api.github.com/graphql", data=body, headers={
        "Authorization": f"bearer {token}", "Content-Type": "application/json", "User-Agent": "specimen-lab"})
    with urllib.request.urlopen(req, timeout=60) as r:
        data = json.load(r)
    if data.get("errors"):
        raise RuntimeError(data["errors"])
    return data["data"]["user"]


def analyse(user):
    cc = user["contributionsCollection"]
    days = [d for w in cc["contributionCalendar"]["weeks"] for d in w["contributionDays"]]
    weeks = [sum(d["contributionCount"] for d in w["contributionDays"]) for w in cc["contributionCalendar"]["weeks"]]
    counts = [d["contributionCount"] for d in days]
    longest = run = 0
    for c in counts:
        run = run + 1 if c else 0
        longest = max(longest, run)
    current = 0
    for c in reversed(counts[:-1] if counts and counts[-1] == 0 else counts):   # today may still be young
        if not c:
            break
        current += 1
    by_wd = [0] * 7
    for d in days:
        by_wd[dt.date.fromisoformat(d["date"]).weekday()] += d["contributionCount"]
    busiest = max(days, key=lambda d: d["contributionCount"]) if days else None
    repos = [r for r in user["repositories"]["nodes"] if r["name"] != PROFILE_REPO]
    return {
        "total": cc["contributionCalendar"]["totalContributions"],
        "commits": cc["totalCommitContributions"], "prs": cc["totalPullRequestContributions"],
        "issues": cc["totalIssueContributions"], "private": cc["restrictedContributionsCount"],
        "weeks": weeks, "days": counts, "dates": [d["date"] for d in days], "current": current, "longest": longest,
        "last7": sum(counts[-7:]),
        "busiest": busiest, "weekday": WEEKDAYS[by_wd.index(max(by_wd))] if any(by_wd) else None,
        "repos": repos, "repo_count": len(repos),
        "stars": sum(r["stargazerCount"] for r in repos), "followers": user["followers"]["totalCount"],
    }



def save(v):
    """The last 26 weeks as GitHub-style shade levels (quartiles of active days), Sunday first."""
    dates = [dt.date.fromisoformat(d) for d in v["dates"]]
    grid = {}
    if dates:
        first = dates[-1] - dt.timedelta(days=(dates[-1].weekday() + 1) % 7 + 25 * 7)
        active = sorted(c for c in v["days"] if c)
        cuts = [active[len(active) * q // 4] for q in (1, 2, 3)] if active else []
        for date, count in zip(dates, v["days"]):
            if date >= first:
                col, row = (date - first).days // 7, (date.weekday() + 1) % 7
                grid[f"{col},{row}"] = 1 + sum(count > c for c in cuts) if count else 0
    out = dict(_how="Written by lab/vitals.py every lab round. grid: 'week,day' -> GitHub shade level 0-4 (26 weeks, Sunday first).",
               user=USER, total=v["total"], last7=v["last7"], streak=v["current"], best=v["longest"], weeks=26, grid=grid)
    (ROOT / "lab" / "data" / "github.json").write_text(json.dumps(out, indent=1) + "\n", encoding="utf-8")


# ------------------------------------------------------------------ main

def main():
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--from-json", help="read a saved GraphQL `user` object instead of calling the API")
    args = ap.parse_args()
    if args.from_json:
        user = json.load(open(args.from_json))
    else:
        token = os.environ.get("GITHUB_TOKEN")
        if not token:
            sys.exit("set GITHUB_TOKEN (the Actions token works)")
        try:
            user = fetch(token)
        except Exception as e:  # noqa: BLE001 - keep yesterday's readings rather than fail the run
            print(f"::warning::GitHub API unavailable, keeping yesterday's reading ({e})")
            return
    v = analyse(user)
    save(v)
    changed = console.write_live("github")
    print(f"contributions: {v['total']} in 12 months, README {'updated' if changed else 'unchanged'}")


if __name__ == "__main__":
    main()
