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

MARKERS = ("releases", "counters")


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
    latest, shipped = [], 0
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
        if stable:
            newest = max(stable, key=lambda r: r["published_at"])
            latest.append(dict(repo=repo, tag=newest["tag_name"],
                               published=newest["published_at"], url=newest["html_url"]))
    profile = api(f"users/{USER}")
    return validate(dict(public_repos=profile["public_repos"], releases_shipped=shipped,
                         releases=latest))


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
    return dict(**counts, releases=releases[:5])


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
    return dict(releases=releases, counters=counters)


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
    outputs = {snapshot: json.dumps(data, indent=2) + "\n", readme: updated}

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
