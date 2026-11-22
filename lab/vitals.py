#!/usr/bin/env python3
"""Draw the GitHub contributions card from the GitHub API and fill the CONTRIBUTIONS block.

Needs a token in GITHUB_TOKEN (the workflow's own token is enough; LAB_TOKEN adds
private contributions). Writes assets/contributions-{theme}.svg and its stills.

    GITHUB_TOKEN=... python lab/vitals.py
    python lab/vitals.py --from-json snapshot.json    # redraw from a saved API response
"""
import argparse
import datetime as dt
import json
import os
import sys
import urllib.request

from notebook import (ASSETS, PAPER, STAT_H, STAT_W, THEMES, USER, Typesetter, blink, box, foot, printed, reading,
                      replace_block, scene, sparkle, stamp, step_in, svg_doc)

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


# ------------------------------------------------------------------ contribution calendar

def calendar(v, theme, animate=True):
    """Contributions card: the year's total ticks up, then the last 26 weeks step in along diagonals
    inside a recessed radar screen, followed by a calm full-width stepped sweep synced to today's reticle."""
    s = PAPER[theme]
    ts = Typesetter("cal")
    body = reading(ts, theme, "contrib", "GITHUB", f"@{USER}", v["total"], "in 12 months", animate)
    body.append(box(11, 82, 226, 71, s["recess"], 2, s["line"]))
    dates = [dt.date.fromisoformat(d) for d in v["dates"]]
    if dates:
        first = dates[-1] - dt.timedelta(days=(dates[-1].weekday() + 1) % 7 + 25 * 7)   # Sunday, 26 weeks back
        pitch, size = 8.4, 7
        gx0, gy0 = 15.5, 89.0
        active = sorted(c for c in v["days"] if c)        # quartiles of active days, as GitHub shades them
        cuts = [active[len(active) * q // 4] for q in (1, 2, 3)] if active else []
        diag = {}
        for date, count in zip(dates, v["days"]):
            if date < first:
                continue
            col, row = (date - first).days // 7, (date.weekday() + 1) % 7
            level = 1 + sum(count > c for c in cuts) if count else 0
            x, y = gx0 + col * pitch, gy0 + row * pitch
            diag.setdefault(col + row, []).append(f'<rect x="{x:.1f}" y="{y:.1f}" width="{size}" height="{size}" '
                                                  f'fill="{s["heat"][level]}"/>')
        # cells land along diagonals, oldest corner first, right behind the moving print line
        cells = [f'<g>{step_in(0.36 + d * 0.018 if animate else None)}{"".join(r)}</g>' for d, r in sorted(diag.items())]
        if animate:
            # full-width stepped radar scan bar + soft trailing column sweeping all 26 weeks every 6s
            cols_n = 26
            travel = 0.36
            xs = [f"{gx0 + c * pitch:.1f}" for c in range(cols_n)]
            txs = [f"{gx0 + max(0, c - 1) * pitch:.1f}" for c in range(cols_n)]
            kt = [f"{travel * i / cols_n:.4f}" for i in range(cols_n)] + [f"{travel:.4f}", "1"]
            h_grid = 6 * pitch + size
            kt_s = ";".join(kt)
            op_lead = ";".join(["0.32"] * cols_n + ["0", "0"])
            op_trail = ";".join(["0.14"] * cols_n + ["0", "0"])
            cells.append(
                f'<rect x="{txs[0]}" y="{gy0:.1f}" width="{size}" height="{h_grid:.1f}" fill="{s["led"]}" opacity="0">'
                f'<animate attributeName="x" values="{";".join(txs)};{txs[-1]};{txs[0]}" keyTimes="{kt_s}" '
                f'calcMode="discrete" dur="6.0s" begin="1.4s" repeatCount="indefinite"/>'
                f'<animate attributeName="opacity" values="{op_trail}" keyTimes="{kt_s}" calcMode="discrete" '
                f'dur="6.0s" begin="1.4s" repeatCount="indefinite"/></rect>'
                f'<rect x="{xs[0]}" y="{gy0:.1f}" width="{size}" height="{h_grid:.1f}" fill="{s["text"]}" opacity="0">'
                f'<animate attributeName="x" values="{";".join(xs)};{xs[-1]};{xs[0]}" keyTimes="{kt_s}" '
                f'calcMode="discrete" dur="6.0s" begin="1.4s" repeatCount="indefinite"/>'
                f'<animate attributeName="opacity" values="{op_lead}" keyTimes="{kt_s}" calcMode="discrete" '
                f'dur="6.0s" begin="1.4s" repeatCount="indefinite"/></rect>'
            )
            # target lock flash + pixel sparkle when the radar scan hits today's cell
            cells.append(
                f'<rect x="{x - 1.5:.1f}" y="{y - 1.5:.1f}" width="{size + 3}" height="{size + 3}" '
                f'fill="none" stroke="{s["text"]}" stroke-width="1.5">'
                f'<animate attributeName="stroke" values="{s["muted"]};{s["text"]};{s["text"]};{s["muted"]}" '
                f'keyTimes="0;0.34;0.48;0.54" calcMode="discrete" dur="6.0s" begin="1.4s" repeatCount="indefinite"/></rect>'
                + sparkle(x + size - 1, y - 2, 2, s["text"], 6.0, 3.25)
            )
        else:
            cells.append(f'<rect x="{x - 1.5:.1f}" y="{y - 1.5:.1f}" width="{size + 3}" height="{size + 3}" '
                         f'fill="none" stroke="{s["text"]}" stroke-width="1.5"/>')
        body.append(f'<g shape-rendering="crispEdges">{"".join(cells)}</g>')
    days = "day" if v["current"] == 1 else "days"
    body.append(foot(ts, theme, f"{v['last7']} this week, a {v['current']}-day streak"))
    label = (f"GitHub contributions for @{USER}: {v['total']} in the last 12 months, {v['last7']} in the last 7 days, "
             f"current streak {v['current']} {days}, best {v['longest']}.")
    return svg_doc(STAT_W, STAT_H, ts.defs_svg() + printed("calp", STAT_W, STAT_H, body, animate), label), label


def write_contributions(v):
    """Draw the contributions card and fill the CONTRIBUTIONS block. True if the README changed."""
    svgs = {theme: calendar(v, theme) for theme in THEMES}
    for theme, (svg, _) in svgs.items():
        (ASSETS / f"contributions-{theme}.svg").write_text(svg, encoding="utf-8")
        (ASSETS / f"contributions-still-{theme}.svg").write_text(calendar(v, theme, False)[0], encoding="utf-8")
    pic = scene("contributions", svgs["light"][1], STAT_W, STAT_H, query="v=" + stamp(svgs["light"][0]))
    return replace_block("CONTRIBUTIONS", f'<a href="https://github.com/{USER}">{pic}</a>')


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
    changed = write_contributions(v)
    print(f"contributions: {v['total']} in 12 months, README {'updated' if changed else 'unchanged'}")


if __name__ == "__main__":
    main()
