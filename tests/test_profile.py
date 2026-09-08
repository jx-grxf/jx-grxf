import importlib.util
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch
import urllib.error
import xml.etree.ElementTree as ET

spec = importlib.util.spec_from_file_location("profile_assets", Path(__file__).resolve().parents[1] / "scripts/profile.py")
profile = importlib.util.module_from_spec(spec)
spec.loader.exec_module(profile)


def release(repo="BriskEdit", tag="v1.0.0", date="2026-09-01"):
    return dict(repo=repo, tag=tag, published=date,
                url=f"https://github.com/jx-grxf/{repo}/releases/tag/{tag}")


def api_release(repo="BriskEdit", **overrides):
    item = dict(tag_name="v1.0.0", published_at="2026-09-01T12:00:00Z",
                html_url=f"https://github.com/jx-grxf/{repo}/releases/tag/v1.0.0",
                draft=False, prerelease=False)
    return item | overrides


class ProfileTests(unittest.TestCase):
    def test_release_selection_is_sorted_and_bounded(self):
        items = [release(repo, date=f"2026-09-{i+1:02}") for i, repo in enumerate(profile.REPOS)]
        result = profile.validate_snapshot(items)
        self.assertEqual(len(result), 4)
        self.assertEqual([r["published"] for r in result], sorted([r["published"] for r in items], reverse=True)[:4])

    def test_untrusted_values_cannot_become_markup_or_external_links(self):
        for changes in (dict(tag="<script>"), dict(url="https://example.com/"),
                        dict(repo="private-project"), dict(published="not-a-date"),
                        dict(url='https://github.com/jx-grxf/BriskEdit/releases/tag/x"><img>')):
            with self.subTest(changes=changes), self.assertRaises(ValueError):
                profile.validate_release(release() | changes)

    def test_same_day_releases_use_publication_time(self):
        items = [release("agent-presence", date="2026-09-05T19:41:45Z"),
                 release("BriskEdit", date="2026-09-05T22:05:47Z")]
        self.assertEqual(profile.validate_snapshot(items)[0]["repo"], "BriskEdit")

    def test_empty_and_duplicate_snapshots_are_rejected(self):
        for items in ([], [release(), release()]):
            with self.assertRaises(ValueError):
                profile.validate_snapshot(items)

    def test_refresh_never_reads_private_release_data(self):
        def api(path):
            if path == "MacPhone":
                return {"private": True}
            if path == "BriskEdit":
                return {"private": False}
            if path == "BriskEdit/releases/latest":
                return api_release()
            self.fail(f"Unexpected API request: {path}")
        with patch.object(profile, "REPOS", ("MacPhone", "BriskEdit")), patch.object(profile, "api", side_effect=api):
            self.assertEqual([r["repo"] for r in profile.fetch_releases()], ["BriskEdit"])

    def test_missing_release_and_prerelease_are_skipped(self):
        def api(path):
            if "/" not in path:
                return {"private": False}
            if path.startswith("MacPhone/"):
                raise urllib.error.HTTPError("url", 404, "Not Found", None, None)
            return api_release(path.split("/")[0], prerelease=path.startswith("poise/"))
        with patch.object(profile, "REPOS", ("MacPhone", "poise", "BriskEdit")), patch.object(profile, "api", side_effect=api):
            self.assertEqual([r["repo"] for r in profile.fetch_releases()], ["BriskEdit"])

    def test_api_failure_preserves_previous_files(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            (root / "assets").mkdir()
            snapshot = root / "assets/releases.json"
            snapshot.write_text("last good snapshot")
            with patch.object(profile, "ROOT", root), patch("sys.argv", ["profile.py", "--refresh"]), patch.object(
                profile, "api", side_effect=urllib.error.HTTPError("url", 403, "Rate limited", None, None)
            ), self.assertRaises(urllib.error.HTTPError):
                profile.main()
            self.assertEqual(snapshot.read_text(), "last good snapshot")
            self.assertEqual(list((root / "assets").iterdir()), [snapshot])

    def test_readme_update_preserves_handwritten_content_and_is_idempotent(self):
        original = "intro\n<!-- releases:start -->\nold\n<!-- releases:end -->\nfooter\n"
        updated = profile.update_readme(original, [release()])
        self.assertTrue(updated.startswith("intro\n"))
        self.assertTrue(updated.endswith("\nfooter\n"))
        self.assertIn(release()["url"], updated)
        self.assertEqual(profile.update_readme(updated, [release()]), updated)
        for invalid in ("no markers", original + "<!-- releases:end -->",
                        "<!-- releases:end --><!-- releases:start -->"):
            with self.assertRaises(ValueError):
                profile.update_readme(invalid, [release()])

    def test_every_svg_variant_parses_and_contains_no_script(self):
        ns = {"svg": "http://www.w3.org/2000/svg"}
        for theme in profile.COLORS:
            for mobile in (False, True):
                for content in (profile.header(theme, mobile), profile.board([release()], theme, mobile)):
                    root = ET.fromstring(content)
                    self.assertIsNotNone(root.find("svg:title", ns))
                    self.assertFalse(root.findall(".//svg:script", ns))
                    self.assertEqual(root.attrib["width"], "480" if mobile else "960")


if __name__ == "__main__":
    unittest.main()
