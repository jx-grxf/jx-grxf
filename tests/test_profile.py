import importlib.util
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch
import urllib.error
import xml.etree.ElementTree as ET

spec = importlib.util.spec_from_file_location(
    "profile_data", Path(__file__).resolve().parents[1] / "scripts/profile.py")
profile = importlib.util.module_from_spec(spec)
spec.loader.exec_module(profile)


def release(repo="BriskEdit", tag="v1.0.0", date="2026-09-01"):
    return dict(repo=repo, tag=tag, published=date,
                url=f"https://github.com/jx-grxf/{repo}/releases/tag/{tag}")


def snapshot(releases=None, **counters):
    return dict(public_repos=33, releases_shipped=49, downloads=2357,
                releases=[release()] if releases is None else releases,
                now=dict(repo="BriskEdit", pushed="2026-09-09T11:50:52Z",
                         url="https://github.com/jx-grxf/BriskEdit")) | counters


def owned_repo(name="BriskEdit", **overrides):
    item = dict(name=name, private=False, fork=False, pushed_at="2026-09-09T11:50:52Z",
                html_url=f"https://github.com/jx-grxf/{name}")
    return item | overrides


def api_release(repo="BriskEdit", **overrides):
    item = dict(tag_name="v1.0.0", published_at="2026-09-01T12:00:00Z",
                html_url=f"https://github.com/jx-grxf/{repo}/releases/tag/v1.0.0",
                draft=False, prerelease=False)
    return item | overrides


class ValidationTests(unittest.TestCase):
    def test_selection_is_sorted_newest_first_and_bounded(self):
        items = [release(repo, date=f"2026-09-{i + 1:02}") for i, repo in enumerate(profile.REPOS)]
        result = profile.validate(snapshot(items))["releases"]
        self.assertEqual(len(result), 5)
        self.assertEqual([r["published"] for r in result],
                         sorted((r["published"] for r in items), reverse=True)[:5])

    def test_untrusted_values_cannot_become_markup_or_external_links(self):
        for changes in (dict(tag="<script>"), dict(url="https://example.com/"),
                        dict(repo="private-project"), dict(published="not-a-date"),
                        dict(url='https://github.com/jx-grxf/BriskEdit/releases/tag/x"><img>')):
            with self.subTest(changes=changes), self.assertRaises(ValueError):
                profile.validate(snapshot([release() | changes]))

    def test_same_day_releases_use_publication_time(self):
        items = [release("agent-presence", date="2026-09-05T19:41:45Z"),
                 release("BriskEdit", date="2026-09-05T22:05:47Z")]
        self.assertEqual(profile.validate(snapshot(items))["releases"][0]["repo"], "BriskEdit")

    def test_empty_and_duplicate_snapshots_are_rejected(self):
        for items in ([], [release(), release()]):
            with self.subTest(items=items), self.assertRaises(ValueError):
                profile.validate(snapshot(items))

    def test_implausible_counters_are_rejected(self):
        for counters in (dict(public_repos=0), dict(releases_shipped=99999),
                         dict(downloads=-1), dict(downloads=10_000_000)):
            with self.subTest(counters=counters), self.assertRaises(ValueError):
                profile.validate(snapshot(**counters))

    def test_the_workbench_repository_must_be_a_real_public_repository(self):
        for now in (dict(repo="../evil", url="https://github.com/jx-grxf/../evil"),
                    dict(repo="BriskEdit", url="https://example.com/BriskEdit"),
                    dict(repo="BriskEdit", url="https://github.com/someone/BriskEdit"),
                    dict(repo="BriskEdit", pushed="whenever",
                         url="https://github.com/jx-grxf/BriskEdit")):
            with self.subTest(now=now), self.assertRaises(ValueError):
                base = dict(repo="BriskEdit", pushed="2026-09-09T11:50:52Z",
                            url="https://github.com/jx-grxf/BriskEdit")
                profile.validate(snapshot() | dict(now=base | now))


class FetchTests(unittest.TestCase):
    def test_refresh_never_reads_private_release_data(self):
        def api(path):
            if path == "repos/jx-grxf/MacPhone":
                return {"private": True}
            if path == "repos/jx-grxf/BriskEdit":
                return {"private": False}
            if path.startswith("repos/jx-grxf/BriskEdit/releases"):
                return [api_release()]
            if path == "users/jx-grxf":
                return {"public_repos": 33}
            if path.startswith("users/jx-grxf/repos"):
                return [owned_repo()]
            self.fail(f"Unexpected API request: {path}")

        with patch.object(profile, "REPOS", ("MacPhone", "BriskEdit")), \
             patch.object(profile, "api", side_effect=api):
            self.assertEqual([r["repo"] for r in profile.fetch()["releases"]], ["BriskEdit"])

    def test_drafts_prereleases_and_missing_releases_are_skipped(self):
        def api(path):
            if path.startswith("users/jx-grxf/repos"):
                return [owned_repo()]
            if path == "users/jx-grxf":
                return {"public_repos": 33}
            if path.count("/") == 2:
                return {"private": False}
            if path.startswith("repos/jx-grxf/MacPhone/"):
                raise urllib.error.HTTPError("url", 404, "Not Found", None, None)
            if path.startswith("repos/jx-grxf/poise/"):
                return [api_release("poise", prerelease=True), api_release("poise", draft=True)]
            return [api_release("BriskEdit"), api_release("BriskEdit", draft=True)]

        with patch.object(profile, "REPOS", ("MacPhone", "poise", "BriskEdit")), \
             patch.object(profile, "api", side_effect=api):
            result = profile.fetch()
        self.assertEqual([r["repo"] for r in result["releases"]], ["BriskEdit"])
        self.assertEqual(result["releases_shipped"], 1)

    def test_api_failure_preserves_previous_files(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            (root / "assets").mkdir()
            saved = root / "assets/profile.json"
            saved.write_text("last good snapshot")
            with patch.object(profile, "ROOT", root), \
                 patch("sys.argv", ["profile.py", "--refresh"]), \
                 patch.object(profile, "api",
                              side_effect=urllib.error.HTTPError("url", 403, "Rate limited", None, None)), \
                 self.assertRaises(urllib.error.HTTPError):
                profile.main()
            self.assertEqual(saved.read_text(), "last good snapshot")
            self.assertEqual(list((root / "assets").iterdir()), [saved])


class ReadmeTests(unittest.TestCase):
    def readme(self):
        return ("intro\n<!-- counters:start -->\nold\n<!-- counters:end -->\nmiddle\n"
                "<!-- now:start -->\nold\n<!-- now:end -->\nmiddle\n"
                "<!-- releases:start -->\nold\n<!-- releases:end -->\nfooter\n")

    def test_every_marker_block_is_replaced_and_handwritten_copy_survives(self):
        text = self.readme()
        for name, body in profile.render(profile.validate(snapshot())).items():
            text = profile.replace_block(text, name, body)
        self.assertTrue(text.startswith("intro\n"))
        self.assertIn("\nmiddle\n", text)
        self.assertTrue(text.endswith("\nfooter\n"))
        self.assertNotIn("old", text)

    def test_replacement_is_idempotent(self):
        once = profile.replace_block(self.readme(), "counters", "body")
        self.assertEqual(profile.replace_block(once, "counters", "body"), once)

    def test_missing_or_reversed_markers_are_rejected(self):
        for invalid in ("no markers",
                        self.readme() + "<!-- counters:end -->",
                        "<!-- counters:end --><!-- counters:start -->"):
            with self.subTest(invalid=invalid), self.assertRaises(ValueError):
                profile.replace_block(invalid, "counters", "body")

    def test_rendered_blocks_carry_the_live_numbers_and_link_out(self):
        blocks = profile.render(profile.validate(snapshot()))
        self.assertIn("**33** public repositories", blocks["counters"])
        self.assertIn("**49** releases shipped", blocks["counters"])
        self.assertIn(release()["url"], blocks["counters"])
        self.assertIn(release()["url"], blocks["releases"])
        self.assertIn("| Project | Version | Released |", blocks["releases"])

    def test_the_workbench_line_names_the_repository_and_links_to_it(self):
        now = profile.render(profile.validate(snapshot()))["now"]
        self.assertIn("BriskEdit", now)
        self.assertIn("https://github.com/jx-grxf/BriskEdit", now)
        self.assertIn("09 Sep 2026", now)

    def test_the_real_readme_carries_every_marker_pair(self):
        text = (Path(profile.ROOT) / "README.md").read_text()
        for name in profile.MARKERS:
            with self.subTest(name=name):
                self.assertEqual(text.count(f"<!-- {name}:start -->"), 1)
                self.assertEqual(text.count(f"<!-- {name}:end -->"), 1)


if __name__ == "__main__":
    unittest.main()


class OdometerTests(unittest.TestCase):
    def svg(self, downloads=2357, releases=49):
        return profile.odometer(downloads, releases)

    def reels(self, svg):
        ns = "{http://www.w3.org/2000/svg}"
        root = ET.fromstring(svg)
        return [[t.text for t in g.iter(f"{ns}text")]
                for g in root.iter(f"{ns}g") if g.get("class") == "reel"]

    def test_every_reel_rests_on_its_final_digit(self):
        # The whole point: a renderer that ignores CSS animation must show the
        # real total, not a row of zeros.
        for total in (0, 7, 49, 2357, 9_999_999):
            with self.subTest(total=total):
                resting = "".join(r[-1] for r in self.reels(self.svg(total)))
                self.assertEqual(resting, f"{total:,}".replace(",", ""))

    def test_reels_count_upward_towards_the_target(self):
        for reel in self.reels(self.svg()):
            digits = [int(d) for d in reel]
            for before, after in zip(digits, digits[1:]):
                self.assertEqual(after, (before + 1) % 10)

    def test_animation_ends_at_the_rest_position(self):
        svg = self.svg()
        self.assertIn("to { transform: translateY(0); }", svg)
        self.assertIn("prefers-reduced-motion", svg)

    def test_document_is_well_formed_titled_and_script_free(self):
        ns = {"svg": "http://www.w3.org/2000/svg"}
        root = ET.fromstring(self.svg())
        self.assertEqual(root.find("svg:title", ns).text, "2,357 downloads across 49 releases")
        self.assertIn("2,357 downloads", root.attrib["aria-label"])
        self.assertFalse(root.findall(".//svg:script", ns))

    def test_each_reel_has_its_own_clip_so_neighbours_do_not_bleed(self):
        ns = "{http://www.w3.org/2000/svg}"
        root = ET.fromstring(self.svg())
        clips = {c.get("id") for c in root.iter(f"{ns}clipPath")}
        used = {g.get("clip-path") for g in root.iter(f"{ns}g") if g.get("clip-path")}
        self.assertEqual(len(clips), 4)
        self.assertEqual(used, {f"url(#{c})" for c in clips})
