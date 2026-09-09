# Profile assets

The profile is plain Markdown plus original SVG artwork that is generated from
`scripts/profile.py` and checked in. It needs no image service, package install,
badge CDN or deployed backend, so nothing on the page can break from the outside.

## Editing

- Edit the copy, project selection and links in `README.md`.
- Edit the header art, the stack panel and the contact pills in `scripts/profile.py`.
- Run `python3 scripts/profile.py` to rebuild from the saved snapshot.
- Run `python3 scripts/profile.py --refresh` to fetch public release data.
  An optional `GITHUB_TOKEN` raises the API rate limit; it is never written to disk.
- Run `python3 -m unittest discover -s tests -v` and
  `python3 scripts/profile.py --check` before committing.

The generator uses only the Python standard library (Python 3.10+).

## What is generated

| File | Contents |
| :--- | :--- |
| `assets/header-*.svg` | Hero art in light/dark and desktop/mobile, including the live counters. |
| `assets/stack-*.svg` | The stack panel, same four variants. |
| `assets/link-*.svg` | Contact pills. Ink on both GitHub themes, so they need no `<picture>`. |
| `assets/profile.json` | The snapshot: public repository count, releases shipped, newest releases. |
| `README.md` | Only the table between the `<!-- releases:start -->` markers. |

## Live data

`REPOS` in the script is the release allowlist. Only public repositories and
published stable releases are eligible; private repository names, drafts and
prereleases never leave the fetch step. Counters are range-checked and every
release URL must point at the expected public repository, so nothing fetched can
turn into markup or an off-site link.

GitHub API errors abort the refresh before any file is written, which preserves
the last good snapshot. The snapshot records release dates, never a generation
timestamp, so an unchanged profile produces no commit.

The counters appear in the header art as well as in the release table. The
refresh workflow therefore stages the whole `assets` directory — staging only the
release files would leave stale numbers in the header and fail the next `--check`.

## Workflow

`Profile assets` verifies every push and pull request. On the default branch it
also refreshes releases every six hours (00:23, 06:23, 12:23 and 18:23 UTC) or on
manual dispatch, and commits only when the data changed. GitHub may delay
scheduled runs and cache images: this is a snapshot, not a real-time feed.
Dispatching on a feature branch only verifies. The workflow uses the built-in
token and a pinned checkout action. If branch protection rejects the update
commit, the job fails visibly and the existing assets stay available.

## Rendering rules

Both illustrations ship separate light/dark and mobile/desktop variants, selected
by `<picture>`. GitHub strips ordinary page CSS and JavaScript, so all animation
lives inside the SVG.

Animation moves position only, never opacity. A renderer that ignores CSS
animation — a thumbnailer, a feed reader, an email client — still shows every
element instead of a blank card. `prefers-reduced-motion` disables it entirely.

The font stack contains double quotes and must stay inside a `<style>` block; in
an XML attribute it would terminate the attribute and break the file. Row labels
such as `BACKEND & WEB` have to be escaped for the same reason. Both rules are
covered by tests, because both were real breakages.

Release links are repeated as Markdown so they stay clickable and readable to a
screen reader; SVG text is not. After changing any `<picture>` markup, check the
real GitHub rendering in both themes and at a narrow viewport.
