#!/usr/bin/env python3
"""Offline unit/integration tests. Temporary Git repositories contain tiny fixtures."""
import importlib.util
import json
import os
from datetime import datetime
from pathlib import Path
import subprocess
import tempfile
import unittest
from unittest.mock import patch

spec = importlib.util.spec_from_file_location("catalog", Path(__file__).with_name("generate-manifest.py"))
assert spec is not None and spec.loader is not None
catalog = importlib.util.module_from_spec(spec)
spec.loader.exec_module(catalog)


class FilenameTests(unittest.TestCase):
    def test_longest_suffix(self):
        for fmt in ("tar", "tar.gz", "tar.xz", "tar.bz2", "tar.zst", "tgz", "zip"):
            self.assertEqual(catalog.classify("update." + fmt), ("archive", fmt))
        self.assertEqual(catalog.classify("firmware.fd.enc"), ("encrypted", "fd.enc"))
        self.assertEqual(catalog.classify("memtest.EFI"), ("tool", "efi"))
        self.assertEqual(catalog.classify("memtest.iso"), ("tool", "iso"))

    def test_precise_version_and_revision(self):
        a = catalog.parse_filename("EDK2602_xb612b0-v1.1-12_v5.0.0639-Stable202608_rel.fd")
        self.assertEqual(a["hardware_rev"], "v1.1-12")
        self.assertEqual(a["firmware_version"], "v5.0.0639")
        self.assertEqual(a["version"], "v5.0.0639-Stable202608")
        self.assertIsNone(a["build_date"])

    def test_udk2018_upstream_mapping(self):
        name = "UDK2018_3A5000-7A2000_Desktop_EVB_V4.0.05878.1-stable202411_dbg.fd"
        artifact = catalog.parse_filename(name)
        metadata = json.loads(Path(__file__).with_name("catalog-metadata.json").read_text())
        self.assertEqual(artifact["rc_baseline"], "stable202411")
        self.assertEqual(metadata["upstream_baselines"][artifact["baseline"]], "UDK2018")

    def test_stage_spelling_not_rewritten(self):
        a = catalog.parse_filename("UDK2018_board_V4.0.05421141-stable202302_dbg.fd")
        self.assertEqual(a["version"], "V4.0.05421141-stable202302")

    def test_rc_baseline_separate_from_upstream_identifier(self):
        a = catalog.parse_filename("EDK2602_board_V5.0.0639-Stable202608.fd")
        self.assertEqual(a["rc_baseline"], "stable202608")
        self.assertEqual(a["baseline"], "EDK2602")
        self.assertIsNone(catalog.parse_filename("QEMU_EFI.fd")["rc_baseline"])

    def test_build_date_calendar_and_boundaries(self):
        for token in ("20260230", "20261301", "stable202608", "x20260101", "20260101246000"):
            self.assertIsNone(catalog.parse_filename("board_" + token + ".fd")["build_date"])
        for token in ("20260228", "20260228123059"):
            self.assertEqual(catalog.parse_filename("board_" + token + ".fd")["build_date"], "2026-02-28")

    def ordered(self, names):
        artifacts = [dict(catalog.parse_filename(n), path=n) for n in names]
        return catalog.order_artifacts(artifacts)

    def test_variants_not_collapsed(self):
        names = ["EDK2602_board-v1.1-8_v5.0.0639_" + variant + "_rel.fd"
                 for variant in ("Gmem", "NoGmem", "mainline-dvfs", "special")]
        names.append("EDK2602_board-v1.1-12_v5.0.0639_Gmem_rel.fd")
        out = self.ordered(names)
        self.assertEqual({a["path"] for a in out}, set(names))
        self.assertTrue(all("is_latest" not in a for a in out))

    def test_unknown_versions_and_roles_retained(self):
        out = self.ordered(["QEMU_EFI.fd", "QEMU_VARS.fd", "mystery.fd", "mystery-new.fd"])
        self.assertEqual(len(out), 4)
        self.assertTrue(all("is_latest" not in a for a in out))
        self.assertEqual([a["path"] for a in out], sorted(a["path"] for a in out))

    def test_repository_time_over_version_and_build_date(self):
        newer_version = "EDK2602_board_v5.0.0639_rel_20261231.fd"
        older_version = "EDK2602_board_v5.0.0529_rel_20260101.fd"
        entries = [dict(catalog.parse_filename(n), path=n, updated_at=d) for n, d in [
            (newer_version, "2026-01-01T00:00:00+00:00"),
            (older_version, "2026-02-01T00:00:00+00:00")]]
        self.assertEqual(catalog.order_artifacts(entries)[0]["path"], older_version)

    def test_equal_versions_all_retained(self):
        out = self.ordered(["EDK2602_board_v5.0.0639_rel_20260101.fd",
                            "EDK2602_board_v5.0.0639_rel_20260201.fd"])
        self.assertEqual(len(out), 2)
        self.assertTrue(all("is_latest" not in a for a in out))

    def test_timezones_ties_and_missing_dates(self):
        entries = [
            {"path": "z.fd", "updated_at": "2026-01-01T08:00:00+08:00"},
            {"path": "a.fd", "updated_at": "2026-01-01T00:00:00+00:00"},
            {"path": "new.fd", "updated_at": "2026-01-01T00:01:00+00:00"},
            {"path": "missing.fd", "updated_at": None}]
        self.assertEqual([a["path"] for a in catalog.order_artifacts(entries)],
                         ["new.fd", "a.fd", "z.fd", "missing.fd"])

    def test_nested_grouping(self):
        self.assertEqual(catalog.group_for("5000Series/Laptop/LM-A2207/history/test.fd"), "5000Series/Laptop/LM-A2207")
        self.assertEqual(catalog.group_for("MultiArchUefiSupport/6000Series/PC/X/history/test.fd"), "MultiArchUefiSupport/6000Series/PC/X")
        self.assertEqual(catalog.group_for("tools/history/test.tar.gz"), "tools")


class ReleaseDiscoveryTests(unittest.TestCase):
    def discover(self, paths, metadata=None):
        warnings = []
        result = catalog.discover_release_notes(set(paths), metadata or {}, "https://example.invalid/commit/", warnings)
        return result, warnings

    def test_new_release_is_discovered_without_metadata(self):
        paths = ["docs/changelist_V6.0.0100-stable202701-" + lang + ".md" for lang in ("CN", "EN")]
        notes, warnings = self.discover(paths)
        self.assertFalse(warnings)
        self.assertEqual(len(notes), 1)
        self.assertEqual(notes[0]["baseline"], "stable202701")
        self.assertEqual(set(notes[0]["documents"]), {"zh", "en"})

    def test_language_is_not_guessed_for_legacy_names(self):
        path = "docs/changelist_V5.0.0343-stable2511.md"
        self.assertEqual(self.discover([path])[0], [])
        meta = {"release_notes": [{"baseline": "stable2511", "title": "V5.0.0343-stable2511", "documents": {"zh": path}}]}
        self.assertEqual(self.discover([path], meta)[0][0]["baseline"], "stable2511")

    def test_same_baseline_versions_are_not_collapsed(self):
        paths = ["docs/changelist_" + version + "-stable202608-CN.md" for version in ("V5.0.0639", "V5.0.0640")]
        notes, _ = self.discover(paths)
        self.assertEqual([n["version"] for n in notes], ["V5.0.0640", "V5.0.0639"])

    def test_duplicate_language_requires_explicit_resolution(self):
        a = "docs/changelist_V5.0.0639-stable202608-CN.md"
        b = "docs/changelist_v5.0.0639-stable202608-cn.md"
        notes, warnings = self.discover([a, b])
        self.assertEqual(notes, [])
        self.assertTrue(warnings)
        meta = {"release_notes": [{"baseline": "stable202608", "title": "V5.0.0639-stable202608", "default": True, "documents": {"zh": b}}]}
        notes, _ = self.discover([a, b], meta)
        self.assertEqual(len(notes), 1)
        self.assertTrue(notes[0]["documents"]["zh"].endswith(b))
        self.assertTrue(notes[0]["default"])


class RepositoryTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.run_git("init", "-q")
        self.run_git("config", "user.name", "Catalog Test")
        self.run_git("config", "user.email", "catalog@example.invalid")
        self.group = "6000Series/PC/Board"
        self.a = self.group + "/EDK2602_Board-V1.0_v5.0.0639-stable202608_rel.fd"
        self.b = self.group + "/history/EDK2602_Board-V1.0_v5.0.0529-stable202605_rel.fd"
        files = {self.a: "a", self.b: "b", self.group + "/unknown.fd.enc": "encrypted",
                 self.group + "/README.md": "![Board](../../../Image/board.png)\nhttps://example.com/support/helpdesk_bios/",
                 self.group + "/SHA256SUMS.txt": "a" * 64 + "  " + Path(self.a).name + "\n",
                 "Image/board.png": "not read as firmware", "Memtest86+/memtest.efi": "tool",
                 "LoongArchVirtMachine/QEMU_EFI.fd": "efi", "LoongArchVirtMachine/QEMU_VARS.fd": "vars"}
        for path, text in files.items():
            target = self.root / path
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_text(text)
        self.run_git("add", ".")
        env = dict(os.environ, GIT_AUTHOR_DATE="2024-01-01T00:00:00+00:00", GIT_COMMITTER_DATE="2025-02-03T04:05:06+00:00")
        self.run_git("commit", "-qm", "fixtures", env=env)

    def run_git(self, *args, **kwargs):
        return subprocess.run(["git", *args], cwd=self.root, check=True, capture_output=True, **kwargs)

    def machine(self, manifest):
        return next(m for m in manifest["machines"] if m["id"] == self.group)

    def test_missing_checksum_still_in_inventory(self):
        m = self.machine(catalog.generate(self.root))
        self.assertEqual(len(m["artifacts"]), 3)
        by_path = {a["path"]: a for a in m["artifacts"]}
        self.assertEqual(by_path[self.a]["sha256"], "a" * 64)
        self.assertIsNone(by_path[self.b]["sha256"])
        self.assertTrue(all(a["size_bytes"] is None for a in m["artifacts"]))

    def test_sparse_paths_and_metadata_git_fallback(self):
        expected = catalog.generate(self.root)
        for path in (self.a, self.b, self.group + "/README.md", self.group + "/SHA256SUMS.txt"):
            (self.root / path).unlink()
        self.assertEqual(catalog.generate(self.root), expected)

    def test_no_firmware_blob_read(self):
        real = catalog.git
        def guarded(root, *args):
            if args[0] == "show":
                self.assertFalse(catalog.classify(args[1]))
            return real(root, *args)
        with patch.object(catalog, "git", guarded):
            (self.root / self.a).unlink()
            catalog.generate(self.root)

    def test_no_mtime_and_determinism(self):
        first = catalog.generate(self.root)
        os.utime(self.root / self.a, (1, 1))
        os.utime(self.root / self.b, (2000000000, 2000000000))
        self.assertEqual(first, catalog.generate(self.root))
        m = self.machine(first)
        expected = datetime.fromisoformat("2025-02-03T04:05:06+00:00")
        for artifact in m["artifacts"]:
            self.assertEqual(datetime.fromisoformat(artifact["updated_at"]), expected)

    def test_git_utc_timestamp_spellings(self):
        real = catalog.git
        expected = datetime.fromisoformat("2025-02-03T04:05:06+00:00")
        for suffix in ("+00:00", "Z"):
            stamp = "2025-02-03T04:05:06" + suffix
            def utc_history(root, *args):
                result = real(root, *args)
                if args[0] == "log":
                    result = result.replace("2025-02-03T04:05:06+00:00", stamp)
                    result = result.replace("2025-02-03T04:05:06Z", stamp)
                return result
            with self.subTest(suffix=suffix), patch.object(catalog, "git", utc_history):
                m = self.machine(catalog.generate(self.root))
                for artifact in m["artifacts"]:
                    self.assertEqual(artifact["updated_at"], stamp)
                    self.assertEqual(datetime.fromisoformat(artifact["updated_at"]), expected)

    def test_shallow_dates_null(self):
        real = catalog.git
        def shallow(root, *args):
            return "true\n" if args == ("rev-parse", "--is-shallow-repository") else real(root, *args)
        with patch.object(catalog, "git", shallow):
            out = catalog.generate(self.root)
        self.assertTrue(out["warnings"])
        self.assertTrue(all(a["updated_at"] is None for m in out["machines"] for a in m["artifacts"]))

    def test_external_only_device_and_missing_docs(self):
        meta = {"machines": {"6000Series/PC/External": {"support_url": "https://example.com/support/helpdesk_bios/"}}}
        m = next(m for m in catalog.generate(self.root, meta)["machines"] if m["model"] == "External")
        self.assertTrue(m["external_only"])
        self.assertEqual(m["artifacts"], [])
        self.assertIsNone(m["readme_url"])

    def test_pinned_image_and_explicit_support(self):
        out = catalog.generate(self.root)
        m = self.machine(out)
        self.assertIn(out["source_commit"] + "/Image/board.png", m["image_url"])
        self.assertEqual(m["support_url"], "https://example.com/support/helpdesk_bios/")
        self.assertIsNone(catalog.readme_image("![x](https://other.example/Image/board.png)", self.group + "/README.md", {"Image/board.png"}))

    def test_diagnostic_image_can_be_suppressed(self):
        meta = {"machines": {self.group: {"hide_image": True}}}
        self.assertIsNone(self.machine(catalog.generate(self.root, meta))["image_url"])

    def test_release_notes_use_tracked_documents_and_explicit_baselines(self):
        document = "docs/release-CN.md"
        (self.root / "docs").mkdir()
        (self.root / document).write_text("# Release notes")
        self.run_git("add", document)
        self.run_git("commit", "-qm", "release documentation")
        meta = {"release_notes": [{"baseline": "stable2511", "title": "Release",
                                  "documents": {"zh": document, "en": "docs/missing.md"}}]}
        result = catalog.generate(self.root, meta)
        self.assertEqual(len(result["release_notes"]), 1)
        note = result["release_notes"][0]
        self.assertEqual(note["baseline"], "stable2511")
        self.assertEqual(list(note["documents"]), ["zh"])
        self.assertIn(result["source_commit"] + "/" + document, note["documents"]["zh"])
        self.assertTrue(any("docs/missing.md" in w for w in result["warnings"]))

    def test_release_notes_without_documents_are_omitted(self):
        meta = {"release_notes": [{"baseline": "stable202608", "title": "Absent",
                                  "documents": {"zh": "docs/absent.md"}}]}
        self.assertEqual(catalog.generate(self.root, meta)["release_notes"], [])

    def test_virtual_machine_category(self):
        meta = {"machines": {"LoongArchVirtMachine": {"category": "VirtualMachine"}}}
        result = catalog.generate(self.root, meta)
        vm = next(m for m in result["machines"] if m["id"] == "LoongArchVirtMachine")
        self.assertEqual(vm["category"], "VirtualMachine")
        self.assertIsNone(vm["series"])
        self.assertEqual(len(vm["artifacts"]), 2)

    def test_upstream_repository_is_separate_from_vendor_support(self):
        url = "https://github.com/memtest86plus/memtest86plus"
        meta = {"machines": {"Memtest86+": {"category": "tool", "upstream_url": url}}}
        result = catalog.generate(self.root, meta)
        tool = next(m for m in result["machines"] if m["id"] == "Memtest86+")
        self.assertEqual(tool["upstream_url"], url)
        self.assertEqual(tool["category"], "tool")
        self.assertIsNone(tool["support_url"])
        self.assertFalse(tool["external_only"])

    def test_documentation_only_tool_category(self):
        meta = {"machines": {"LoongsonBackupOS": {"category": "tool"}}}
        result = catalog.generate(self.root, meta)
        tool = next(m for m in result["machines"] if m["id"] == "LoongsonBackupOS")
        self.assertEqual(tool["category"], "tool")
        self.assertIsNone(tool["series"])
        self.assertEqual(tool["artifacts"], [])

    def test_upstream_baseline_requires_explicit_mapping(self):
        unknown = self.machine(catalog.generate(self.root))
        self.assertTrue(all(a["edk2_baseline"] is None for a in unknown["artifacts"]))
        meta = {"upstream_baselines": {"EDK2602": "stable202602"}}
        known = self.machine(catalog.generate(self.root, meta))
        artifact = next(a for a in known["artifacts"] if a["path"] == self.a)
        self.assertEqual(artifact["rc_baseline"], "stable202608")
        self.assertEqual(artifact["edk2_baseline"], "stable202602")

    def test_release_only_from_metadata(self):
        meta = {"artifacts": {self.a: {"release_date": "2026-08-01"}}}
        m = self.machine(catalog.generate(self.root, meta))
        self.assertEqual(next(a for a in m["artifacts"] if a["path"] == self.a)["release_date"], "2026-08-01")
        self.assertIsNone(next(a for a in m["artifacts"] if a["path"] == self.b)["release_date"])

    def test_json_javascript_outputs_and_escaping(self):
        output = self.root / "web/manifest.json"
        manifest = {"test": "</script>\u2028"}
        catalog.write_outputs(manifest, output)
        self.assertEqual(json.loads(output.read_text()), manifest)
        javascript = output.with_suffix(".js").read_text()
        self.assertTrue(javascript.startswith("window.FIRMWARE_CATALOG = "))
        self.assertNotIn("<", javascript)
        self.assertEqual(json.loads(javascript.removeprefix("window.FIRMWARE_CATALOG = ").rstrip(";\n")), manifest)


if __name__ == "__main__":
    unittest.main()
