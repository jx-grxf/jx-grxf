#!/usr/bin/env python3
"""Build the profile artwork and release snapshot using only Python's standard library."""

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
USER = "jx-grxf"

# Release board allowlist. Only public repositories with published stable
# releases reach the profile; private work is filtered out at fetch time.
REPOS = (
    "BriskEdit", "agent-presence", "NotchTray", "MacPhone", "Caruso-Reborn",
    "BottleLite", "poise", "PatchPilot", "claude-swap-bar", "ip-multitool",
    "tools", "scooter-tuning-db",
)

# Warm paper and terracotta, matching johannesgrof.me so the profile, the site
# and the apps read as one hand. `accent` is the text-safe tone, `vivid` the
# graphic one.
PALETTE = {
    "light": dict(bg="#faf8f4", panel="#f1ece2", tile="#ffffff", border="#e2dace",
                  hair="#ece5d9", text="#14130f", muted="#6e6a5f",
                  accent="#b8431f", vivid="#df5638"),
    "dark": dict(bg="#14130f", panel="#1e1b15", tile="#242118", border="#332f27",
                 hair="#2a2720", text="#f1eee5", muted="#a49c8b",
                 accent="#ff997c", vivid="#ff997c"),
}

SANS = '-apple-system, BlinkMacSystemFont, "Segoe UI", Helvetica, Arial, sans-serif'
MONO = '"SFMono-Regular", ui-monospace, Consolas, "Liberation Mono", monospace'

# Stack panel: (row label, [(technology, brand dot)]).
STACK = (
    ("NATIVE", (("Swift", "#f05138"), ("SwiftUI", "#0a84ff"), ("AppKit", "#8e8e93"),
                ("WidgetKit", "#5e5ce6"), ("ActivityKit", "#32ade6"))),
    ("BACKEND & WEB", (("TypeScript", "#3178c6"), ("Node.js", "#5fa04e"),
                       ("Rust", "#dea584"), ("Python", "#ffd343"), ("Astro", "#bc52ee"))),
    ("DATA & SHIPPING", (("PostgreSQL", "#4169e1"), ("Supabase", "#3ecf8e"),
                         ("Cloudflare", "#f6821f"), ("Railway", "#a394f0"),
                         ("Sparkle", "#5e5ce6"))),
)

# Contact pills. Ink on both GitHub themes, so they need no <picture> switch.
LINKS = (
    ("website", "johannesgrof.me", "globe"),
    ("x", "@johannesgrofdev", "x"),
    ("linkedin", "Johannes Grof", "in"),
    ("email", "contact@johannesgrof.me", "mail"),
)

PILL_PAD = 49          # dot, gutters and generous right padding
PILL_CHAR = 7.4        # conservative average advance at 13px


def pill_width(label):
    return PILL_PAD + round(len(label) * PILL_CHAR)


def document(width, height, title, description, body, theme, extra_css=""):
    c = PALETTE[theme]
    return f'''<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 {width} {height}" role="img" aria-labelledby="t d">
<title id="t">{escape(title)}</title>
<desc id="d">{escape(description)}</desc>
<style>
text {{ font-family: {SANS}; fill: {c["text"]}; }}
.mono {{ font-family: {MONO}; }}
.muted {{ fill: {c["muted"]}; }}
.accent {{ fill: {c["accent"]}; }}
.rise {{ animation: rise .7s cubic-bezier(.2,.7,.3,1) both; }}
/* Position only: a renderer that ignores CSS animation still shows every element. */
@keyframes rise {{ from {{ transform: translateY(10px); }} to {{ transform: translateY(0); }} }}
{extra_css}@media (prefers-reduced-motion: reduce) {{
  * {{ animation: none !important; }}
}}
</style>
<rect x=".5" y=".5" width="{width - 1}" height="{height - 1}" rx="18" fill="{c["bg"]}" stroke="{c["border"]}"/>
{body}</svg>
'''


# --------------------------------------------------------------------------- header

TILE_GLYPHS = ("caret", "route", "prompt", "wave", "notch", "signal")


def glyph(name, x, y, size, color):
    """A simple geometric mark centred in a tile, one per kind of thing I build."""
    cx, cy = x + size / 2, y + size / 2
    s = f'stroke="{color}" stroke-width="2.4" stroke-linecap="round" fill="none"'
    if name == "caret":        # text editor
        return (f'<path d="M{cx - 9} {cy - 9}h5m-2.5 0v18m-2.5 0h5" {s}/>'
                f'<rect x="{cx + 2}" y="{cy - 3}" width="8" height="6" rx="1.5" fill="{color}"/>')
    if name == "route":        # transit
        return (f'<path d="M{cx - 10} {cy + 6}h6a5 5 0 0 0 5-5v-4a5 5 0 0 1 5-5h4" {s}/>'
                f'<circle cx="{cx - 11}" cy="{cy + 6}" r="3" fill="{color}"/>'
                f'<circle cx="{cx + 11}" cy="{cy - 8}" r="3" fill="{color}"/>')
    if name == "prompt":       # command line
        return (f'<path d="M{cx - 10} {cy - 7}l6 6-6 6" {s}/>'
                f'<path d="M{cx + 1} {cy + 7}h9" {s}/>')
    if name == "wave":         # audio
        bars = ""
        for i, height in enumerate((8, 16, 22, 14, 9)):
            bars += (f'<path d="M{cx - 16 + i * 8} {cy - height / 2}v{height}" '
                     f'stroke="{color}" stroke-width="2.6" stroke-linecap="round"/>')
        return bars
    if name == "notch":        # menu bar utilities on a notched display
        l, r_, t, b = cx - 16, cx + 16, cy - 11, cy + 11
        return (f'<path d="M{l + 3} {t}H{cx - 9}a1 1 0 0 1 1 1v4a1 1 0 0 0 1 1h14'
                f'a1 1 0 0 0 1-1v-4a1 1 0 0 1 1-1H{r_ - 3}a3 3 0 0 1 3 3V{b - 3}'
                f'a3 3 0 0 1-3 3H{l + 3}a3 3 0 0 1-3-3V{t + 3}a3 3 0 0 1 3-3z" {s}/>')
    return (f'<path d="M{cx - 3} {cy + 9}a4 4 0 0 1 6 0" {s}/>'   # signal / wireless
            f'<path d="M{cx - 9} {cy + 2}a12 12 0 0 1 18 0" {s}/>'
            f'<path d="M{cx - 15} {cy - 5}a20 20 0 0 1 30 0" {s}/>')


def header(stats, theme, mobile=False):
    c = PALETTE[theme]
    # Two explicit layouts beat one generic engine: every baseline is readable here.
    if mobile:
        w, h, pad = 480, 396, 28
        eyebrow, heads, subs = 62, (106, 144), (180, 202)
        size, sub_size = 32, 15
        tile, gap, cols, gx, gy = 58, 12, 6, 28, 232
        strip_y = 326
    else:
        w, h, pad = 960, 352, 48
        eyebrow, heads, subs = 68, (122, 174), (214, 236)
        size, sub_size = 46, 17
        tile, gap, cols = 76, 24, 3
        gx, gy = w - pad - (cols * tile + (cols - 1) * gap), 56
        strip_y = 281

    body = (f'<g class="rise"><text x="{pad}" y="{eyebrow}" class="mono accent" font-size="12" '
            f'letter-spacing="2.2">MADE IN AUSTRIA · HTL KAINDORF</text></g>')
    for i, line in enumerate(("Software that does", "one thing, properly.")):
        body += (f'<g class="rise" style="animation-delay:{.06 + i * .07:.2f}s">'
                 f'<text x="{pad - 2}" y="{heads[i]}" font-size="{size}" font-weight="700" '
                 f'letter-spacing="-1.5">{line}</text></g>')
    # Two short lines keep the copy clear of the tile grid at every width.
    body += '<g class="rise" style="animation-delay:.2s">'
    for y, line in zip(subs, ("Native Mac and iPhone apps, developer tools,",
                              "and the backends that keep them running.")):
        body += f'<text x="{pad}" y="{y}" class="muted" font-size="{sub_size}">{line}</text>'
    body += "</g>"

    # One mark per kind of thing I build; the transit tile is the accent one.
    for i, name in enumerate(TILE_GLYPHS):
        x, y = gx + (i % cols) * (tile + gap), gy + (i // cols) * (tile + gap)
        featured = name == "route"
        body += (f'<g class="rise" style="animation-delay:{.24 + i * .06:.2f}s">'
                 f'<rect x="{x}" y="{y}" width="{tile}" height="{tile}" rx="{round(tile * .28)}" '
                 f'fill="{c["vivid"] if featured else c["tile"]}" '
                 f'stroke="{c["vivid"] if featured else c["border"]}"/>'
                 f'{glyph(name, x, y, tile, c["bg"] if featured else c["muted"])}</g>')

    # Live strip: the numbers come from the public GitHub API at --refresh time.
    body += f'<path d="M{pad} {strip_y}H{w - pad}" stroke="{c["hair"]}"/>'
    cells = ((str(stats["public_repos"]), "PUBLIC REPOS"),
             (str(stats["releases_shipped"]), "RELEASES SHIPPED"),
             (stats["latest"]["repo"], f'LATEST · {stats["latest"]["tag"]}'))
    step = (w - 2 * pad) / len(cells)
    for i, (value, label) in enumerate(cells):
        x = round(pad + i * step)
        body += (f'<g class="rise" style="animation-delay:{.44 + i * .06:.2f}s">'
                 f'<text x="{x}" y="{strip_y + 26}" font-size="{17 if mobile else 19}" '
                 f'font-weight="650">{escape(value)}</text>'
                 f'<text x="{x}" y="{strip_y + 43}" class="mono muted" font-size="10" '
                 f'letter-spacing="1.4">{escape(label)}</text></g>')

    described = (f"Johannes Grof, developer in Austria. Software that does one thing, properly. "
                 f"Native Mac and iPhone apps, developer tools and the backends that keep them "
                 f"running. Six marks for the kinds of things he builds, and a live strip: "
                 f'{stats["public_repos"]} public repositories, {stats["releases_shipped"]} '
                 f'releases shipped, latest {stats["latest"]["repo"]} {stats["latest"]["tag"]}.')
    return document(w, h, "Johannes Grof — software that does one thing, properly",
                    described, body, theme)


# ---------------------------------------------------------------------------- stack

def stack(theme, mobile=False):
    c = PALETTE[theme]
    w = 480 if mobile else 960
    pad = 24 if mobile else 32
    body, y, index = "", 0, 0

    if mobile:
        y = pad + 6
        for label, items in STACK:
            body += (f'<text x="{pad}" y="{y + 10}" class="mono muted" font-size="10" '
                     f'letter-spacing="1.6">{escape(label)}</text>')
            y += 26
            x = pad
            for name, dot in items:
                width = pill_width(name)
                if x + width > w - pad:
                    x, y = pad, y + 38
                body += pill(x, y, width, name, dot, c, index)
                x += width + 8
                index += 1
            y += 52
        y -= 20
    else:
        y = pad + 4
        for label, items in STACK:
            body += (f'<text x="{pad}" y="{y + 21}" class="mono muted" font-size="10" '
                     f'letter-spacing="1.6">{escape(label)}</text>')
            x = pad + 132
            for name, dot in items:
                width = pill_width(name)
                body += pill(x, y, width, name, dot, c, index)
                x += width + 10
                index += 1
            y += 54
        y -= 22

    described = "; ".join(f'{label}: ' + ", ".join(n for n, _ in items) for label, items in STACK)
    return document(w, y + pad - 8, "What Johannes Grof works with", described, body, theme)


def pill(x, y, width, label, dot, c, index):
    return (f'<g class="rise" style="animation-delay:{min(index, 14) * .035:.3f}s">'
            f'<rect x="{x}" y="{y}" width="{width}" height="32" rx="9" '
            f'fill="{c["panel"]}" stroke="{c["border"]}"/>'
            f'<circle cx="{x + 16}" cy="{y + 16}" r="4" fill="{dot}"/>'
            f'<text x="{x + 29}" y="{y + 21}" font-size="13" font-weight="550">'
            f'{escape(label)}</text></g>')


# ---------------------------------------------------------------------------- links

def link_badge(label, kind):
    ink, paper, accent = "#191610", "#f4f1e8", "#ff997c"
    width, height = pill_width(label) + 8, 34
    marks = {
        "globe": (f'<circle cx="19" cy="17" r="7.5" fill="none" stroke="{accent}" stroke-width="1.7"/>'
                  f'<path d="M11.5 17h15M19 9.5c4 4.5 4 10.5 0 15c-4-4.5-4-10.5 0-15z" '
                  f'fill="none" stroke="{accent}" stroke-width="1.7"/>'),
        "x": (f'<path d="M13 10l12 14m0-14L13 24" stroke="{accent}" stroke-width="2.1" '
              f'stroke-linecap="round"/>'),
        "in": (f'<text x="12" y="22" font-size="13" font-weight="700" '
               f'fill="{accent}">in</text>'),
        "mail": (f'<rect x="11" y="11" width="16" height="12" rx="2.5" fill="none" '
                 f'stroke="{accent}" stroke-width="1.7"/>'
                 f'<path d="M11.8 12.5L19 18l7.2-5.5" fill="none" stroke="{accent}" '
                 f'stroke-width="1.7" stroke-linejoin="round"/>'),
    }[kind]
    return f'''<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 {width} {height}" role="img" aria-label="{escape(label)}">
<title>{escape(label)}</title>
<style>text {{ font-family: {SANS}; }}</style>
<rect x=".5" y=".5" width="{width - 1}" height="{height - 1}" rx="9" fill="{ink}" stroke="#3a3428"/>
{marks}
<text x="34" y="22" font-size="13" font-weight="600" fill="{paper}">{escape(label)}</text>
</svg>
'''


# ------------------------------------------------------------------------ github api

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


def readme_releases(readme, releases):
    start, end = "<!-- releases:start -->", "<!-- releases:end -->"
    if readme.count(start) != 1 or readme.count(end) != 1 or readme.index(start) >= readme.index(end):
        raise ValueError("Expected one ordered pair of release markers in README.md")
    rows = "\n".join(
        f'| **[{r["repo"]}]({r["url"]})** | `{r["tag"]}` | '
        f'{datetime.fromisoformat(r["published"].replace("Z", "+00:00")).strftime("%d %b %Y")} |'
        for r in releases)
    table = "| Project | Version | Released |\n| :--- | :--- | :--- |\n" + rows
    before, rest = readme.split(start)
    _, after = rest.split(end)
    return f"{before}{start}\n{table}\n{end}{after}"


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    mode = parser.add_mutually_exclusive_group()
    mode.add_argument("--refresh", action="store_true", help="Fetch public release data before rendering")
    mode.add_argument("--check", action="store_true", help="Verify assets without network access or writes")
    args = parser.parse_args()

    snapshot = ROOT / "assets/profile.json"
    data = fetch() if args.refresh else validate(json.loads(snapshot.read_text()))
    stats = dict(public_repos=data["public_repos"], releases_shipped=data["releases_shipped"],
                 latest=data["releases"][0])

    outputs = {snapshot: json.dumps(data, indent=2) + "\n",
               ROOT / "README.md": readme_releases((ROOT / "README.md").read_text(), data["releases"])}
    for key, label, kind in LINKS:
        outputs[ROOT / f"assets/link-{key}.svg"] = link_badge(label, kind)
    for theme in PALETTE:
        for mobile in (False, True):
            suffix = f'{"mobile-" if mobile else ""}{theme}.svg'
            outputs[ROOT / f"assets/header-{suffix}"] = header(stats, theme, mobile)
            outputs[ROOT / f"assets/stack-{suffix}"] = stack(theme, mobile)

    stale = [path for path, content in outputs.items()
             if not path.exists() or path.read_text() != content]
    if args.check and stale:
        raise SystemExit("Stale generated files: " + ", ".join(str(p.relative_to(ROOT)) for p in stale))
    if not args.check:
        # Finish every request, validation and render before touching the tree.
        for path in stale:
            path.write_text(outputs[path])
    print(f'{"Verified" if args.check else "Generated"} {len(outputs)} files; {len(stale)} changed.')


if __name__ == "__main__":
    main()
