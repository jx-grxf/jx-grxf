# Profile assets

The profile uses original SVG illustrations, checked-in product screenshots and
plain Markdown. It needs no image service, package install or deployed backend.
The activity card is served by GitHub Stats Extended; the main illustrations and
stack badges do not depend on that service.

## Editing

- Edit personal copy, project selection and the stack in `README.md`.
- Edit the header and departure-board design in `scripts/profile.py`.
- Run `python3 scripts/profile.py` to rebuild from the saved release snapshot.
- Run `python3 scripts/profile.py --refresh` to retrieve public stable releases.
  An optional `GITHUB_TOKEN` raises the API rate limit; it is never written to disk.
- Run `python3 -m unittest discover -s tests -v` and
  `python3 scripts/profile.py --check` before committing.

The generator uses only the Python standard library (Python 3.10+). The release
allowlist is `REPOS` in the script. Only explicitly public repositories and
published stable releases are eligible; the four newest release dates are shown.
Private repository names, drafts and prereleases are not exported. GitHub API
errors abort the refresh before writing files, preserving the last good snapshot.
The snapshot records release dates, not a constantly changing generation time.

The `Profile assets` workflow verifies changes on pushes and pull requests. Once
merged into the default branch, it also refreshes releases every six hours
(00:23, 06:23, 12:23 and 18:23 UTC), or on manual dispatch from the default branch. GitHub may delay scheduled runs and cache images; this is a release snapshot, not a real-time feed. It commits only when
release data changes. Dispatching on a feature branch only verifies; it does not
write to the default branch. The workflow uses the built-in GitHub token and a
pinned checkout action. If branch protection rejects the update commit, the job
fails visibly and the existing assets remain available.

Both graphics have separate light/dark and mobile/desktop versions. Animation
plays once, then rests; `prefers-reduced-motion` displays the final static state.
GitHub strips ordinary page CSS and JavaScript, so all animation is inside the
SVG image. The release links are repeated as Markdown for accessibility and
clickable navigation. Check the actual GitHub rendering in both themes and at a
narrow viewport after changing the picture markup.

The eight stack badges are also generated locally and checked in. Their small
SVGs use text and color dots, so no icon CDN or badge service is required.

## Product screenshots

- `assets/oeffigo.webp`: the existing public ÖffiGo website image,
  `public/shots/variants/app-board-480.webp` in `jx-grxf/oeffigo-website`, also
  served at <https://oeffigo.app/shots/variants/app-board-480.webp>.
  It illustrates the beta interface; its displayed times are not live data.
- `assets/briskedit.png`: `.github/assets/showcase.png` from `jx-grxf/BriskEdit`.
  Public source: <https://github.com/jx-grxf/BriskEdit/blob/main/.github/assets/showcase.png>.

Keep screenshots as product evidence. Do not synthesize UI or describe a still
image as a recorded demo. BriskEdit's demo link points to its existing showcase.
The header and departure-board illustrations are original repository assets.
