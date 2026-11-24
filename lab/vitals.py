#!/usr/bin/env python3
"""Draw the GitHub panel from the GitHub API and fill the CONTRIBUTIONS block.

The panel is the readings section's main instrument: the year's contributions over a
53-week phosphor heatmap, then four readouts (pull requests merged, issues closed,
commits, streak), and underneath, the languages across public repositories and the
week's rhythm. It comes wide and narrow (phones), each animated and still.

Needs a token in GITHUB_TOKEN (the workflow's own token is enough; LAB_TOKEN adds
private contributions).

    GITHUB_TOKEN=... python lab/vitals.py
    python lab/vitals.py --from-json snapshot.json    # redraw from a saved API response
"""
import argparse
import datetime as dt
import json
import os
import sys
import urllib.request

from notebook import ASSETS, USER, Typesetter, count_up, mark, replace_block, stamp, step_in, svg_doc, wide_scene, write_pair
from rts import INK, W, bar, defs, plaque, text, well

PROFILE_REPO = USER                 # the profile repo itself: lab code, not your work
QUERY = """
query($login: String!) {
  user(login: $login) {
    createdAt
    followers { totalCount }
    pullRequests { totalCount }
    mergedPullRequests: pullRequests(states: MERGED) { totalCount }
    issues { totalCount }
    closedIssues: issues(states: CLOSED) { totalCount }
    repositories(ownerAffiliations: OWNER, privacy: PUBLIC, isFork: false, first: 100,
                 orderBy: {field: PUSHED_AT, direction: DESC}) {
      totalCount
      nodes {
        name stargazerCount forkCount pushedAt
        languages(first: 12, orderBy: {field: SIZE, direction: DESC}) { edges { size node { name } } }
      }
    }
    contributionsCollection {
      totalCommitContributions totalPullRequestContributions totalIssueContributions
      totalPullRequestReviewContributions restrictedContributionsCount
      contributionCalendar { totalContributions weeks { contributionDays { date contributionCount } } }
    }
  }
}"""
WEEKDAYS = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]


# ------------------------------------------------------------------ data

def fetch(token):
    body = json.dumps({"query": QUERY, "variables": {"login": USER}}).encode()
    req = urllib.request.Request("https://api.github.com/graphql", data=body, headers={
        "Authorization": f"bearer {token}", "Content-Type": "application/json", "User-Agent": "dexterslab-lab"})
    with urllib.request.urlopen(req, timeout=60) as r:
        data = json.load(r)
    if data.get("errors"):
        raise RuntimeError(data["errors"])
    return data["data"]["user"]


def analyse(user):
    cc = user["contributionsCollection"]
    days = [d for w in cc["contributionCalendar"]["weeks"] for d in w["contributionDays"]]
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
    repos = [r for r in user["repositories"]["nodes"] if r["name"] != PROFILE_REPO]
    langs = {}
    for r in repos:
        for e in r["languages"]["edges"]:
            langs[e["node"]["name"]] = langs.get(e["node"]["name"], 0) + e["size"]
    size = sum(langs.values()) or 1
    top = sorted(langs.items(), key=lambda kv: -kv[1])[:5]
    return {
        "total": cc["contributionCalendar"]["totalContributions"],
        "commits": cc["totalCommitContributions"], "reviews": cc["totalPullRequestReviewContributions"],
        "prs": user["pullRequests"]["totalCount"], "merged": user["mergedPullRequests"]["totalCount"],
        "issues": user["issues"]["totalCount"], "closed": user["closedIssues"]["totalCount"],
        "days": counts, "dates": [d["date"] for d in days], "current": current, "longest": longest,
        "last7": sum(counts[-7:]), "weekdays": by_wd,
        "busiest": WEEKDAYS[by_wd.index(max(by_wd))] if any(by_wd) else None,
        "langs": [(name, b / size) for name, b in top], "repo_count": len(repos),
        "followers": user["followers"]["totalCount"],
    }


# ------------------------------------------------------------------ the panel

def minimap(v, x, y, weeks, pitch, cell, animate):
    """The last `weeks` weeks as a minimap: dark water for quiet days, brighter for busy ones.
    Animated, the columns are revealed left to right like fog of war lifting."""
    dates = [dt.date.fromisoformat(d) for d in v["dates"]]
    if not dates:
        return "", []
    last = dates[-1]
    first = last - dt.timedelta(days=(last.weekday() + 1) % 7 + (weeks - 1) * 7)   # a Sunday
    active = sorted(c for c in v["days"] if c)
    cuts = [active[len(active) * q // 4] for q in (1, 2, 3)] if active else []
    ramp = ["#24262b", "#5a3a10", "#a8650f", "#e8891f", "#ffe08a"]   # iron to molten gold
    cols, months, tx, ty = {}, [], x, y
    for date, count in zip(dates, v["days"]):
        if date < first:
            continue
        col, row = (date - first).days // 7, (date.weekday() + 1) % 7
        level = 1 + sum(count > c for c in cuts) if count else 0
        cx, cy = x + col * pitch, y + row * pitch
        cols.setdefault(col, []).append(f'<rect x="{cx:.1f}" y="{cy:.1f}" width="{cell}" height="{cell}" rx="1" fill="{ramp[level]}"/>')
        if date.day == 1 or (date == first and date.day < 8):
            months.append((cx, date.strftime("%b").upper()))
        tx, ty = cx, cy
    out = [f'<g>{step_in(0.4 + c * 0.012) if animate else ""}{"".join(r)}</g>' for c, r in sorted(cols.items())]
    out.append(f'<rect x="{tx - 1.5:.1f}" y="{ty - 1.5:.1f}" width="{cell + 3}" height="{cell + 3}" fill="none" stroke="#ffcf6a" stroke-width="1.4"/>')
    labels, prev = [], -99
    for mx, name in months:
        if mx - prev >= 34:
            labels.append((mx, name))
            prev = mx
    return "".join(out), labels


def github_panel(v, theme, layout="wide", animate=True):
    ts = Typesetter("gh")
    wide = layout == "wide"
    w = W if wide else 400
    total, best = v["total"], max(v["longest"], v["current"])
    share = v["commits"] / total if total else 0
    rows = [("Pull requests merged", f"{v['merged']}\\{v['prs']}", v["merged"] / v["prs"] if v["prs"] else 0, INK["blue"]),
            ("Issues closed", f"{v['closed']}\\{v['issues']}", v["closed"] / v["issues"] if v["issues"] else 0, INK["green"]),
            (f"Commits, {share * 100:.0f}% of activity", f"{v['commits']:,}", share, INK["gold"]),
            (f"Streak, best {best}", f"{v['current']} DAYS", v["current"] / best if best else 0, INK["violet"])]
    if wide:
        h = 300
        body = [defs(), plaque(0, 0, w, h, pattern=True), mark("github", 18, 16, 18, "#e8e2d4"),
                text(ts, "GITHUB", "head", 15, 44, 31, "url(#orange)", track=.1),
                text(ts, f"@{USER}", "semi", 14, w - 18, 30, INK["muted"], anchor="end"),
                count_up(lambda n: text(ts, f"{n:,}", "num", 56, 18, 92, INK["text"]), total, 0.3 if animate else None),
                text(ts, "CONTRIBUTIONS IN THE LAST YEAR", "bold", 12, 140, 70, INK["muted"], track=.12),
                text(ts, f"{v['last7']:,} THIS WEEK", "bold", 12, 140, 88, INK["gold"], track=.12)]
        for i, (label, val, frac, col) in enumerate(rows):
            body.append(bar(ts, 18, 128 + i * 42, 250, frac, col, label, val, 0.5 + i * .12 if animate else None))
        mx, my, mw, mh = 286, 112, 330, 170
        weeks = 26
        body.append(f'<rect x="{mx}" y="{my}" width="{mw}" height="{mh}" rx="3" fill="url(#well)" stroke="url(#gold)" stroke-width="2"/>'
                    + text(ts, f"MINIMAP: LAST {weeks} WEEKS", "bold", 11, mx + 12, my + 20, INK["gold"], track=.14))
        cells, months = minimap(v, mx + 15, my + 34, weeks, 11.6, 9.5, animate)
        body.append(cells)
        for x_, name in months:
            body.append(text(ts, name, "bold", 10, x_, my + 132, INK["dim"], track=.1))
        if v["busiest"]:
            body.append(text(ts, f"BUSIEST ON {v['busiest'].upper()}S", "bold", 11, mx + 12, my + 156, INK["gold"], track=.12))
        lx = 636
        body.append(text(ts, "LANGUAGES BY BYTES", "bold", 11, lx, my + 6, INK["gold"], track=.14))
        top = v["langs"][0][1] if v["langs"] else 1
        for i, (name, frac) in enumerate(v["langs"]):
            y = my + 30 + i * 28
            fw = 100 * frac / top
            body.append(text(ts, name, "semi", 14, lx, y + 10, INK["text"])
                        + well(lx + 76, y, 104, 12) + f'<rect x="{lx + 78}" y="{y + 2}" width="{fw:.1f}" height="8" fill="url(#goldh)"/>'
                        + text(ts, f"{frac * 100:.0f}%", "num", 17, w - 18, y + 12, INK["text"], anchor="end"))
    else:
        h = 560
        body = [defs(), plaque(0, 0, w, h, pattern=True), mark("github", 16, 16, 18, "#e8e2d4"),
                text(ts, "GITHUB", "head", 15, 42, 31, "url(#orange)", track=.1),
                text(ts, f"@{USER}", "semi", 14, w - 16, 30, INK["muted"], anchor="end"),
                count_up(lambda n: text(ts, f"{n:,}", "num", 52, 16, 92, INK["text"]), total, 0.3 if animate else None),
                text(ts, "CONTRIBUTIONS, LAST YEAR", "bold", 11.5, 130, 70, INK["muted"], track=.1),
                text(ts, f"{v['last7']:,} THIS WEEK", "bold", 11.5, 130, 88, INK["gold"], track=.1)]
        for i, (label, val, frac, col) in enumerate(rows):
            body.append(bar(ts, 16, 128 + i * 42, 368, frac, col, label, val, 0.5 + i * .12 if animate else None))
        my = 296
        body.append(f'<rect x="16" y="{my}" width="368" height="140" rx="3" fill="url(#well)" stroke="url(#gold)" stroke-width="2"/>'
                    + text(ts, "MINIMAP: LAST 26 WEEKS", "bold", 11, 28, my + 20, INK["gold"], track=.14))
        cells, months = minimap(v, 28, my + 32, 26, 13.2, 11, animate)
        body.append(cells)
        if v["busiest"]:
            body.append(text(ts, f"BUSIEST ON {v['busiest'].upper()}S", "bold", 11, 28, my + 130, INK["gold"], track=.12))
        top = v["langs"][0][1] if v["langs"] else 1
        body.append(text(ts, "LANGUAGES BY BYTES", "bold", 11, 16, 462, INK["gold"], track=.14))
        for i, (name, frac) in enumerate(v["langs"][:4]):
            x0, y0 = 16 + (i % 2) * 188, 474 + (i // 2) * 34
            fw = 80 * frac / top
            body.append(text(ts, name, "semi", 13.5, x0, y0 + 10, INK["text"])
                        + well(x0 + 74, y0, 84, 12) + f'<rect x="{x0 + 76}" y="{y0 + 2}" width="{fw:.1f}" height="8" fill="url(#goldh)"/>'
                        + text(ts, f"{frac * 100:.0f}%", "num", 16, x0 + 180, y0 + 12, INK["text"], anchor="end"))
    return svg_doc(w, h, ts.defs_svg() + "".join(body), alt(v)), alt(v)


def alt(v):
    langs = ", ".join(f"{name} {share * 100:.0f}%" for name, share in v["langs"])
    return (f"GitHub activity for @{USER}: {v['total']:,} contributions in the last 12 months, "
            f"{v['last7']} in the last 7 days. {v['merged']} of {v['prs']} pull requests merged, "
            f"{v['closed']} of {v['issues']} issues closed, {v['commits']:,} commits in a year. "
            f"Current streak {v['current']} days, best {max(v['longest'], v['current'])}. "
            f"Top languages: {langs}." + (f" Busiest on {v['busiest']}s." if v["busiest"] else ""))


def write_contributions(v):
    """Draw the GitHub panel and fill the CONTRIBUTIONS block. True if the README changed."""
    write_pair(ASSETS, "contributions", lambda t, a: github_panel(v, t, "wide", a)[0])
    write_pair(ASSETS, "contributions-narrow", lambda t, a: github_panel(v, t, "narrow", a)[0])
    svg, label = github_panel(v, "light", "wide")
    pic = wide_scene("contributions", "contributions-narrow", label, width=W, query="v=" + stamp(svg))
    return replace_block("CONTRIBUTIONS", f'<a href="https://github.com/{USER}">{pic}</a>')


# ------------------------------------------------------------------ main

def main():
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--from-json", help="read a saved GraphQL `user` object instead of calling the API")
    args = ap.parse_args()
    if args.from_json:
        user = json.load(open(args.from_json, encoding="utf-8"))
    else:
        token = os.environ.get("GITHUB_TOKEN")
        if not token:
            sys.exit("set GITHUB_TOKEN (the Actions token works)")
        try:
            user = fetch(token)
        except Exception as e:  # noqa: BLE001 - keep the last reading rather than fail the run
            print(f"::warning::GitHub API unavailable, keeping the last reading ({e})")
            return
    v = analyse(user)
    changed = write_contributions(v)
    print(f"github: {v['total']} contributions, {v['merged']}/{v['prs']} PRs merged, "
          f"{v['closed']}/{v['issues']} issues closed, README {'updated' if changed else 'unchanged'}")


if __name__ == "__main__":
    main()
