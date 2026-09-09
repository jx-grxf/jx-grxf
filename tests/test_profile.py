import importlib.util
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch
import urllib.error
import xml.etree.ElementTree as ET

spec = importlib.util.spec_from_file_location(
    "profile_assets", Path(__file__).resolve().parents[1] / "scripts/profile.py")
profile = importlib.util.module_from_spec(spec)
spec.loader.exec_module(profile)

NS = {"svg": "http://www.w3.org/2000/svg"}


def release(repo="BriskEdit", tag="v1.0.0", date="2026-09-01"):
    return dict(repo=repo, tag=tag, published=date,
                url=f"https://github.com/jx-grxf/{repo}/releases/tag/{tag}")


def snapshot(releases=None, **counters):
    return dict(public_repos=33, releases_shipped=49,
                releases=[release()] if releases is None else releases) | counters


def api_release(repo="BriskEdit", **overrides):
    item = dict(tag_name="v1.0.0", published_at="2026-09-01T12:00:00Z",
                html_url=f"https://github.com/jx-grxf/{repo}/releases/tag/v1.0.0",
                draft=False, prerelease=False)
    return item | overrides


def stats():
    return dict(public_repos=33, releases_shipped=49, latest=release())


class ReleaseDataTests(unittest.TestCase):
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
        for counters in (dict(public_repos=0), dict(releases_shipped=99999)):
            with self.subTest(counters=counters), self.assertRaises(ValueError):
                profile.validate(snapshot(**counters))


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
            self.fail(f"Unexpected API request: {path}")

        with patch.object(profile, "REPOS", ("MacPhone", "BriskEdit")), \
             patch.object(profile, "api", side_effect=api):
            self.assertEqual([r["repo"] for r in profile.fetch()["releases"]], ["BriskEdit"])

    def test_drafts_prereleases_and_missing_releases_are_skipped(self):
        def api(path):
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
    def test_update_preserves_handwritten_content_and_is_idempotent(self):
        original = "intro\n<!-- releases:start -->\nold\n<!-- releases:end -->\nfooter\n"
        updated = profile.readme_releases(original, [release()])
        self.assertTrue(updated.startswith("intro\n"))
        self.assertTrue(updated.endswith("\nfooter\n"))
        self.assertIn(release()["url"], updated)
        self.assertEqual(profile.readme_releases(updated, [release()]), updated)

    def test_missing_or_reversed_markers_are_rejected(self):
        original = "intro\n<!-- releases:start -->\nold\n<!-- releases:end -->\nfooter\n"
        for invalid in ("no markers", original + "<!-- releases:end -->",
                        "<!-- releases:end --><!-- releases:start -->"):
            with self.subTest(invalid=invalid), self.assertRaises(ValueError):
                profile.readme_releases(invalid, [release()])


class ArtworkTests(unittest.TestCase):
    def every_document(self):
        for theme in profile.PALETTE:
            for mobile in (False, True):
                yield f"header-{theme}-{mobile}", profile.header(stats(), theme, mobile), mobile
                yield f"stack-{theme}-{mobile}", profile.stack(theme, mobile), mobile

    def test_every_variant_is_well_formed_titled_and_script_free(self):
        for name, content, mobile in self.every_document():
            with self.subTest(name=name):
                root = ET.fromstring(content)  # an unescaped "&" would raise here
                self.assertIsNotNone(root.find("svg:title", NS))
                self.assertIsNotNone(root.find("svg:desc", NS))
                self.assertFalse(root.findall(".//svg:script", NS))
                self.assertEqual(root.attrib["width"], "480" if mobile else "960")

    def test_link_badges_are_well_formed_and_labelled(self):
        for _, label, kind in profile.LINKS:
            with self.subTest(kind=kind):
                root = ET.fromstring(profile.link_badge(label, kind))
                self.assertEqual(root.attrib["aria-label"], label)
                self.assertFalse(root.findall(".//svg:script", NS))

    def test_no_attribute_carries_the_quoted_font_stack(self):
        # The font stack contains double quotes and must stay inside <style>.
        for name, content, _ in self.every_document():
            with self.subTest(name=name):
                self.assertNotIn('font-family="', content)
        for _, label, kind in profile.LINKS:
            self.assertNotIn('font-family="', profile.link_badge(label, kind))

    def test_ampersands_in_stack_labels_survive_rendering(self):
        self.assertIn("BACKEND &amp; WEB", profile.stack("light"))

    def test_animation_never_starts_from_a_hidden_state(self):
        # A renderer that ignores CSS animation must still show every element.
        for name, content, _ in self.every_document():
            with self.subTest(name=name):
                self.assertNotIn("opacity: 0", content)

    def test_live_counters_reach_the_header(self):
        content = profile.header(stats(), "light")
        self.assertIn(">33<", content)
        self.assertIn(">49<", content)
        self.assertIn(">BriskEdit<", content)


if __name__ == "__main__":
    unittest.main()
