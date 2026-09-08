#!/usr/bin/env python3
"""Build profile SVGs using only Python's standard library."""

import argparse
from datetime import datetime
from html import escape
import json
import os
from pathlib import Path
import re
import urllib.error
import urllib.request

ROOT = Path(__file__).resolve().parents[1]
REPOS = (
    "BriskEdit", "agent-presence", "NotchTray", "MacPhone", "Caruso-Reborn",
    "BottleLite", "poise", "PatchPilot", "claude-swap-bar",
)
COLORS = {
    "dark": dict(bg="#0d1416", panel="#141f21", border="#2b3c3d",
                 text="#eef5f1", muted="#a2b5af", accent="#a5edb1", track="#38564a"),
    "light": dict(bg="#f6f8f4", panel="#eaf0e8", border="#c9d6cc",
                  text="#192c25", muted="#50675c", accent="#286c40", track="#a9c3b0"),
}
BADGES = {
    "swift": ("Swift", "#f58a55", 88),
    "swiftui": ("SwiftUI", "#68b5ff", 103),
    "typescript": ("TypeScript", "#68b5ff", 125),
    "rust": ("Rust", "#edb38e", 81),
    "astro": ("Astro", "#ccabff", 88),
    "supabase": ("Supabase", "#7bdfb0", 117),
    "cloudflare": ("Cloudflare", "#ffb66b", 125),
    "railway": ("Railway", "#c7b5ff", 105),
}


def badge(label, color, width):
    return f'''<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="30" viewBox="0 0 {width} 30" role="img" aria-label="{label}">
<title>{label}</title>
<rect x=".5" y=".5" width="{width-1}" height="29" rx="6" fill="#172226" stroke="#3c5148"/>
<circle cx="16" cy="15" r="4" fill="{color}"/>
<text x="28" y="19.5" fill="#eef5f1" font-family="-apple-system, BlinkMacSystemFont, Segoe UI, sans-serif" font-size="13" font-weight="550">{label}</text>
</svg>
'''


def svg(width, height, title, description, body, theme):
    c = COLORS[theme]
    return f'''<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 {width} {height}" role="img" aria-labelledby="title desc">
<title id="title">{escape(title)}</title>
<desc id="desc">{escape(description)}</desc>
<style>
text {{ font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif; fill: {c["text"]}; }}
.mono {{ font-family: "SFMono-Regular", Consolas, "Liberation Mono", monospace; }}
.muted {{ fill: {c["muted"]}; }}
.accent {{ fill: {c["accent"]}; }}
.enter {{ animation: enter .8s ease-out both; }}
.train {{ animation: journey 3.6s cubic-bezier(.25,.65,.25,1) both; }}
.cursor {{ animation: blink 1s step-end 3; }}
@keyframes enter {{ from {{ transform: translateY(5px); }} to {{ transform: translateY(0); }} }}
@keyframes journey {{ from {{ transform: translateX(0); }} to {{ transform: translateX({width - 130}px); }} }}
@keyframes blink {{ 50% {{ opacity: 0; }} }}
@media (prefers-reduced-motion: reduce) {{
  .enter, .train, .cursor {{ animation: none; }}
  .train {{ transform: translateX({width - 130}px); }}
}}
</style>
<rect x="1" y="1" width="{width - 2}" height="{height - 2}" rx="20" fill="{c["bg"]}" stroke="{c["border"]}"/>
{body}
</svg>
'''


def header(theme, mobile=False):
    c = COLORS[theme]
    w, h = (480, 338) if mobile else (960, 338)
    headline = 38 if mobile else 52
    body = f'''
<path d="M1 54H{w-1}" stroke="{c["border"]}"/>
<circle cx="26" cy="28" r="5" fill="#ef7970"/>
<circle cx="44" cy="28" r="5" fill="#e6bf63"/>
<circle cx="62" cy="28" r="5" fill="#78c990"/>
<text x="{w//2 + 18}" y="33" text-anchor="middle" class="mono muted" font-size="12">johannes — ~/workbench</text>
<g class="enter">
<text x="32" y="96" class="mono accent" font-size="13" letter-spacing="2">MADE IN AUSTRIA</text>
<text x="30" y="151" font-size="{headline}" font-weight="700" letter-spacing="-1.8">Native by nature.</text>
<text x="32" y="187" class="muted" font-size="18">Mac apps. Useful tools. Curious detours.</text>
<text x="32" y="222" class="mono accent" font-size="15">mac 4 life.<tspan class="cursor"> ▍</tspan></text>
</g>
'''
    if not mobile:
        body += f'''
<rect x="658" y="82" width="270" height="156" rx="14" fill="{c["panel"]}" stroke="{c["border"]}"/>
<text x="680" y="110" class="mono muted" font-size="12" letter-spacing="1">CURRENT FOCUS</text>
<text x="679" y="151" font-size="34" font-weight="650">ÖffiGo</text>
<text x="680" y="183" class="muted" font-size="15">Austria, one connection at a time.</text>
<circle cx="685" cy="212" r="4" fill="{c["accent"]}"/>
<text x="698" y="217" class="mono accent" font-size="12">iPHONE + APPLE WATCH</text>
'''
    body += f'''
<path d="M32 278H{w-32}" stroke="{c["track"]}" stroke-width="3"/>
<g fill="{c["bg"]}" stroke="{c["accent"]}" stroke-width="2">
<circle cx="40" cy="278" r="5"/><circle cx="{w//2}" cy="278" r="5"/><circle cx="{w-40}" cy="278" r="5"/>
</g>
<g class="train">
<rect x="35" y="261" width="54" height="20" rx="6" fill="{c["accent"]}"/>
<path d="M44 267h9m5 0h9m5 0h9" stroke="{c["bg"]}" stroke-width="4"/>
<circle cx="47" cy="283" r="3" fill="{c["text"]}"/><circle cx="78" cy="283" r="3" fill="{c["text"]}"/>
</g>
<text x="32" y="314" class="mono muted" font-size="{12 if mobile else 14}">01 / BUILD</text>
<text x="{w//2}" y="314" text-anchor="middle" class="mono muted" font-size="{12 if mobile else 14}">02 / LEARN</text>
<text x="{w-32}" y="314" text-anchor="end" class="mono muted" font-size="{12 if mobile else 14}">03 / REPEAT</text>
'''
    return svg(w, h, "Johannes Grof — native by nature",
               "Student developer in Austria. Native Mac apps, useful tools and curious detours. A small train arrives along the bottom of the window.",
               body, theme)


def validate_release(item):
    repo, tag, date, url = (item[k] for k in ("repo", "tag", "published", "url"))
    if repo not in REPOS or not re.fullmatch(r"[A-Za-z0-9][A-Za-z0-9._+-]{0,27}", tag):
        raise ValueError("Unexpected repository or release tag")
    datetime.fromisoformat(date.replace("Z", "+00:00"))
    if not url.startswith(f"https://github.com/jx-grxf/{repo}/releases/tag/"):
        raise ValueError("Release URL must point to the expected public repository")
    if any(ch in url for ch in ('"', "<", ">", "(", ")", "\n", "\r", " ")):
        raise ValueError("Unsafe release URL")
    return dict(repo=repo, tag=tag, published=date, url=url)


def validate_snapshot(items):
    result = [validate_release(item) for item in items]
    if not result or len({item["repo"] for item in result}) != len(result):
        raise ValueError("Expected a nonempty snapshot with unique repositories")
    return sorted(result, key=lambda item: (item["published"], item["repo"]), reverse=True)[:4]


def api(path):
    headers = {"Accept": "application/vnd.github+json", "User-Agent": "jx-grxf-profile",
               "X-GitHub-Api-Version": "2022-11-28"}
    if token := os.environ.get("GITHUB_TOKEN"):
        headers["Authorization"] = f"Bearer {token}"
    request = urllib.request.Request(f"https://api.github.com/repos/jx-grxf/{path}", headers=headers)
    with urllib.request.urlopen(request, timeout=20) as response:
        return json.load(response)


def fetch_releases():
    releases = []
    for repo in REPOS:
        # Check visibility even when the local token has broader access.
        metadata = api(repo)
        if metadata["private"]:
            continue
        try:
            release = api(f"{repo}/releases/latest")
        except urllib.error.HTTPError as error:
            error.close()
            if error.code == 404:
                continue
            raise
        if release["draft"] or release["prerelease"]:
            continue
        releases.append(dict(repo=repo, tag=release["tag_name"],
                             published=release["published_at"], url=release["html_url"]))
    return validate_snapshot(releases)


def board(items, theme, mobile=False):
    c = COLORS[theme]
    w, h = (480, 404) if mobile else (960, 404)
    body = f'''
<text x="28" y="43" font-size="23" font-weight="650" letter-spacing="-.5">Latest departures</text>
<text x="28" y="70" class="mono muted" font-size="12">FROM THE WORKBENCH / PUBLIC RELEASES</text>
<circle cx="{w-34}" cy="36" r="5" fill="{c["accent"]}"/>
<path d="M28 88H{w-28}" stroke="{c["border"]}"/>
'''
    for i, item in enumerate(items):
        y = 120 + 66 * i
        repo, tag = escape(item["repo"]), escape(item["tag"])
        date = datetime.fromisoformat(item["published"].replace("Z", "+00:00")).strftime("%d %b %Y")
        if mobile:
            body += f'''
<g class="enter" style="animation-delay:{i * .12}s">
<text x="28" y="{y}" font-size="21" font-weight="600">{repo}</text>
<text x="{w-28}" y="{y}" text-anchor="end" class="mono accent" font-size="18">{tag}</text>
<text x="28" y="{y+23}" class="mono muted" font-size="13">{date}</text>
</g>'''
        else:
            body += f'''
<g class="enter" style="animation-delay:{i * .12}s">
<text x="28" y="{y+7}" class="mono muted" font-size="14">0{i+1}</text>
<text x="79" y="{y+7}" font-size="24" font-weight="600">{repo}</text>
<text x="510" y="{y+7}" class="mono accent" font-size="22">{tag}</text>
<text x="{w-28}" y="{y+7}" text-anchor="end" class="mono muted" font-size="17">{date}</text>
</g>'''
        body += f'<path d="M28 {y+35}H{w-28}" stroke="{c["border"]}"/>'
    body += f'<text x="28" y="382" class="mono muted" font-size="12">NEXT STOP: WHATEVER NEEDS BUILDING.</text>'
    return svg(w, h, "Latest public releases",
               "; ".join(f'{r["repo"]} {r["tag"]}, {r["published"]}' for r in items), body, theme)


def update_readme(readme, items):
    start, end = "<!-- releases:start -->", "<!-- releases:end -->"
    if readme.count(start) != 1 or readme.count(end) != 1 or readme.index(start) >= readme.index(end):
        raise ValueError("Expected one ordered pair of release markers in README.md")
    links = "\n".join(f'- **[{r["repo"]} {r["tag"]}]({r["url"]})** · {r["published"][:10]}' for r in items)
    before, rest = readme.split(start)
    _, after = rest.split(end)
    return f"{before}{start}\n{links}\n{end}{after}"


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    mode = parser.add_mutually_exclusive_group()
    mode.add_argument("--refresh", action="store_true", help="Fetch public releases before rendering")
    mode.add_argument("--check", action="store_true", help="Verify assets without network or writes")
    args = parser.parse_args()
    snapshot = ROOT / "assets/releases.json"
    items = fetch_releases() if args.refresh else validate_snapshot(json.loads(snapshot.read_text()))
    outputs = {snapshot: json.dumps(items, indent=2) + "\n",
               ROOT / "README.md": update_readme((ROOT / "README.md").read_text(), items)}
    for name, (label, color, width) in BADGES.items():
        outputs[ROOT / f"assets/badge-{name}.svg"] = badge(label, color, width)
    for theme in COLORS:
        for mobile in (False, True):
            suffix = f'{"mobile-" if mobile else ""}{theme}.svg'
            outputs[ROOT / f"assets/header-{suffix}"] = header(theme, mobile)
            outputs[ROOT / f"assets/releases-{suffix}"] = board(items, theme, mobile)
    stale = [path for path, content in outputs.items()
             if not path.exists() or path.read_text() != content]
    if args.check and stale:
        raise SystemExit("Stale generated files: " + ", ".join(str(p.relative_to(ROOT)) for p in stale))
    if not args.check:
        # Finish every request, validation and rendering before changing files.
        for path in stale:
            path.write_text(outputs[path])
    print(f'{"Verified" if args.check else "Generated"} {len(outputs)} files; {len(stale)} changed.')


if __name__ == "__main__":
    main()
