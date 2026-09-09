# Profile maintenance

The profile is plain Markdown. Two things are generated: the release table and
the counter line under the badges, both written by `scripts/profile.py` from a
saved snapshot in `assets/profile.json`. Everything else is handwritten.

## Editing

- Edit the copy, project selection, badges and links directly in `README.md`.
- Run `python3 scripts/profile.py` to rewrite the generated blocks from the snapshot.
- Run `python3 scripts/profile.py --refresh` to fetch fresh data from GitHub first.
  An optional `GITHUB_TOKEN` raises the API rate limit; it is never written to disk.
- Run `python3 -m unittest discover -s tests -v` and
  `python3 scripts/profile.py --check` before committing.

The script uses only the Python standard library (Python 3.10+). It touches
nothing outside the `<!-- releases:… -->` and `<!-- counters:… -->` marker pairs,
so handwritten copy between them is never at risk.

## Live data

`REPOS` in the script is the release allowlist. Only public repositories and
published stable releases are eligible; private repository names, drafts and
prereleases never leave the fetch step. Counters are range-checked and every
release URL must point at the expected public repository, so nothing fetched can
turn into markup or an off-site link.

GitHub API errors abort the refresh before any file is written, which preserves
the last good snapshot. The snapshot records release dates, never a generation
timestamp, so an unchanged profile produces no commit.

`Profile assets` verifies every push and pull request. On the default branch it
also refreshes every six hours (00:23, 06:23, 12:23 and 18:23 UTC) or on manual
dispatch, and commits only when the data changed. Dispatching on a feature branch
only verifies. GitHub may delay scheduled runs: this is a snapshot, not a live feed.

## Contribution snake

`Contribution snake` renders the contribution graph animation nightly at 02:17
UTC and force-pushes `snake.svg` and `snake-dark.svg` to the orphan `output`
branch. The README loads them from `raw.githubusercontent.com`, so the images
come from this repository rather than a third-party renderer.

The force-push is deliberate: it keeps `output` at a single commit instead of
adding a history entry every night. `workflow_dispatch` only works once the
workflow exists on the default branch, so the images 404 until the first run
after merge.

## Third-party images

The badges are external services and can fail independently of this repository:

| Service | Used for |
| :--- | :--- |
| `img.shields.io` | Contact badges and the individual technology badges. |
| `skillicons.dev` | The four icon rows in "What I work with". |
| `readme-typing-svg.demolab.com` | The animated line under the name. |

If one of them goes down, the page still reads correctly; only the images break.
Nothing here depends on them for meaning, and the alt text carries the content.
