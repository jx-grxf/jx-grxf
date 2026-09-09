#!/usr/bin/env python3
"""Refresh the public release data shown in README.md, standard library only."""

import argparse
from datetime import datetime
import json
import os
from pathlib import Path
import re
import urllib.error
import urllib.request

ROOT = Path(__file__).resolve().parents[1]
USER = "jx-grxf"

# Release allowlist. Only public repositories with published stable releases
# reach the profile; private work is filtered out at fetch time.
REPOS = (
    "BriskEdit", "agent-presence", "NotchTray", "MacPhone", "Caruso-Reborn",
    "BottleLite", "poise", "PatchPilot", "claude-swap-bar", "ip-multitool",
    "tools", "scooter-tuning-db",
)

MARKERS = ("releases", "counters", "now")

# Odometer geometry. The final number is the resting state, so a renderer
# without CSS animation shows the real figure instead of a row of zeros.
CELL_W, CELL_H, PAD = 34, 52, 24
REEL_STEPS = 14
INK, EDGE, DIGIT, LABEL = "#0d1117", "#30363d", "#f05138", "#8b949e"
MONO = '"SFMono-Regular", ui-monospace, Consolas, "Liberation Mono", monospace'


def api(path):
    headers = {"Accept": "application/vnd.github+json", "User-Agent": "jx-grxf-profile",
               "X-GitHub-Api-Version": "2022-11-28"}
    if token := os.environ.get("GITHUB_TOKEN"):
        headers["Authorization"] = f"Bearer {token}"
    request = urllib.request.Request(f"https://api.github.com/{path}", headers=headers)
    with urllib.request.urlopen(request, timeout=20) as response:
        return json.load(response)


def fetch():
    """Collect public releases and counters. Any API error aborts before writing."""
    latest, shipped, downloads = [], 0, 0
    for repo in REPOS:
        # Re-check visibility even when the local token can see more than the world.
        if api(f"repos/{USER}/{repo}")["private"]:
            continue
        try:
            releases = api(f"repos/{USER}/{repo}/releases?per_page=100")
        except urllib.error.HTTPError as error:
            error.close()
            if error.code == 404:
                continue
            raise
        stable = [r for r in releases if not r["draft"] and not r["prerelease"]]
        shipped += len(stable)
        downloads += sum(a["download_count"] for r in stable for a in r.get("assets", []))
        if stable:
            newest = max(stable, key=lambda r: r["published_at"])
            latest.append(dict(repo=repo, tag=newest["tag_name"],
                               published=newest["published_at"], url=newest["html_url"]))
    profile = api(f"users/{USER}")
    # Most recently pushed public repository. Forks are somebody else's work, and
    # this repository pushes itself every six hours, so both are excluded.
    owned = [r for r in api(f"users/{USER}/repos?sort=pushed&per_page=100")
             if not r["private"] and not r["fork"] and r["name"] != USER]
    now = max(owned, key=lambda r: r["pushed_at"])
    return validate(dict(public_repos=profile["public_repos"], releases_shipped=shipped,
                         downloads=downloads, releases=latest,
                         now=dict(repo=now["name"], pushed=now["pushed_at"],
                                  url=now["html_url"])))


def validate(data):
    """Reject anything that did not come from the expected public repositories."""
    releases = []
    for item in data["releases"]:
        repo, tag, date, url = (item[k] for k in ("repo", "tag", "published", "url"))
        if repo not in REPOS or not re.fullmatch(r"[A-Za-z0-9][A-Za-z0-9._+-]{0,27}", tag):
            raise ValueError("Unexpected repository or release tag")
        datetime.fromisoformat(date.replace("Z", "+00:00"))
        if not url.startswith(f"https://github.com/{USER}/{repo}/releases/tag/"):
            raise ValueError("Release URL must point to the expected public repository")
        if any(ch in url for ch in ('"', "<", ">", "(", ")", "\n", "\r", " ")):
            raise ValueError("Unsafe release URL")
        releases.append(dict(repo=repo, tag=tag, published=date, url=url))
    if not releases or len({r["repo"] for r in releases}) != len(releases):
        raise ValueError("Expected a nonempty snapshot with unique repositories")
    releases.sort(key=lambda r: (r["published"], r["repo"]), reverse=True)
    counts = {k: int(data[k]) for k in ("public_repos", "releases_shipped")}
    if not all(0 < v < 10000 for v in counts.values()):
        raise ValueError("Implausible profile counters")
    downloads = int(data["downloads"])
    if not 0 <= downloads < 10_000_000:
        raise ValueError("Implausible download total")

    now = data["now"]
    if not re.fullmatch(r"[A-Za-z0-9][A-Za-z0-9._-]{0,99}", now["repo"]):
        raise ValueError("Unexpected repository name")
    if now["url"] != f'https://github.com/{USER}/{now["repo"]}':
        raise ValueError("Repository URL must point at the expected public repository")
    datetime.fromisoformat(now["pushed"].replace("Z", "+00:00"))
    return dict(**counts, downloads=downloads, releases=releases[:5],
                now=dict(repo=now["repo"], pushed=now["pushed"], url=now["url"]))


def odometer(downloads, releases_shipped):
    """Digit reels that spin up to the download total.

    Each reel rests on its final digit and the animation runs *towards* that
    rest state, so a renderer that ignores CSS animation shows the real number
    instead of a row of zeros.
    """
    text = f"{downloads:,}"
    label = f"DOWNLOADS · ACROSS {releases_shipped} RELEASES"
    top, travel = 18, REEL_STEPS * CELL_H
    baseline = top + 40

    cells, x = [], PAD
    for ch in text:
        cells.append((ch, x))
        x += CELL_W if ch.isdigit() else 15
    width = PAD * 2 + max(x - PAD, round(len(label) * 7.4))
    height = top + CELL_H + 36

    clips, reels, reel = "", "", 0
    for ch, cx in cells:
        if not ch.isdigit():
            reels += (f'<text x="{cx + 7}" y="{baseline}" text-anchor="middle" font-size="44" '
                      f'font-weight="700" fill="{DIGIT}" opacity=".5">{ch}</text>')
            continue
        target = int(ch)
        strip = ""
        for j in range(REEL_STEPS + 1):
            value = (target - REEL_STEPS + j) % 10
            strip += (f'<text x="{cx + CELL_W // 2}" y="{baseline + (j - REEL_STEPS) * CELL_H}" '
                      f'text-anchor="middle" font-size="44" font-weight="700" '
                      f'fill="{DIGIT}">{value}</text>')
        clips += (f'<clipPath id="c{reel}"><rect x="{cx}" y="{top}" '
                  f'width="{CELL_W}" height="{CELL_H}"/></clipPath>')
        # Left digits settle first, the way a real odometer does.
        reels += (f'<g clip-path="url(#c{reel})"><g class="reel" '
                  f'style="animation-duration:{1.0 + reel * 0.25:.2f}s">{strip}</g></g>')
        reel += 1

    return f'''<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 {width} {height}" role="img" aria-label="{downloads:,} downloads across {releases_shipped} releases">
<title>{downloads:,} downloads across {releases_shipped} releases</title>
<defs>{clips}</defs>
<style>
text {{ font-family: {MONO}; }}
.reel {{ animation-name: spin; animation-timing-function: cubic-bezier(.16,.84,.24,1); animation-fill-mode: both; }}
@keyframes spin {{ from {{ transform: translateY({travel}px); }} to {{ transform: translateY(0); }} }}
@media (prefers-reduced-motion: reduce) {{ * {{ animation: none !important; }} }}
</style>
<rect x=".5" y=".5" width="{width - 1}" height="{height - 1}" rx="10" fill="{INK}" stroke="{EDGE}"/>
{reels}
<text x="{PAD}" y="{top + CELL_H + 22}" font-size="10" letter-spacing="1.4" fill="{LABEL}">{label}</text>
</svg>
'''


def replace_block(readme, name, body):
    """Swap the text between one pair of markers, leaving handwritten copy alone."""
    start, end = f"<!-- {name}:start -->", f"<!-- {name}:end -->"
    if readme.count(start) != 1 or readme.count(end) != 1 or readme.index(start) >= readme.index(end):
        raise ValueError(f"Expected one ordered pair of {name} markers in README.md")
    before, rest = readme.split(start)
    _, after = rest.split(end)
    return f"{before}{start}\n{body}\n{end}{after}"


def render(data):
    rows = "\n".join(
        f'| **[{r["repo"]}]({r["url"]})** | `{r["tag"]}` | '
        f'{datetime.fromisoformat(r["published"].replace("Z", "+00:00")).strftime("%d %b %Y")} |'
        for r in data["releases"])
    releases = "| Project | Version | Released |\n| :--- | :--- | :--- |\n" + rows
    newest = data["releases"][0]
    counters = (f'**{data["public_repos"]}** public repositories · '
                f'**{data["releases_shipped"]}** releases shipped · '
                f'latest **[{newest["repo"]} {newest["tag"]}]({newest["url"]})**')
    pushed = datetime.fromisoformat(data["now"]["pushed"].replace("Z", "+00:00"))
    now = (f'**On the workbench right now:** [{data["now"]["repo"]}]({data["now"]["url"]}), '
           f'last pushed {pushed.strftime("%d %b %Y")}.')
    return dict(releases=releases, counters=counters, now=now)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    mode = parser.add_mutually_exclusive_group()
    mode.add_argument("--refresh", action="store_true", help="Fetch public release data before writing")
    mode.add_argument("--check", action="store_true", help="Verify README without network access or writes")
    args = parser.parse_args()

    snapshot = ROOT / "assets/profile.json"
    data = fetch() if args.refresh else validate(json.loads(snapshot.read_text()))

    readme = ROOT / "README.md"
    updated = readme.read_text()
    for name, body in render(data).items():
        updated = replace_block(updated, name, body)
    outputs = {snapshot: json.dumps(data, indent=2) + "\n", readme: updated,
               ROOT / "assets/downloads.svg": odometer(data["downloads"], data["releases_shipped"])}

    stale = [path for path, content in outputs.items()
             if not path.exists() or path.read_text() != content]
    if args.check and stale:
        raise SystemExit("Stale generated content: "
                         + ", ".join(str(p.relative_to(ROOT)) for p in stale))
    if not args.check:
        # Finish every request and validation before touching the tree.
        for path in stale:
            path.write_text(outputs[path])
    print(f'{"Verified" if args.check else "Generated"} {len(outputs)} files; {len(stale)} changed.')


if __name__ == "__main__":
    main()
