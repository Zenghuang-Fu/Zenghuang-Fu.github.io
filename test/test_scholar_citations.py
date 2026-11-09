"""Regression checks for the site's scheduled citation data update."""

import importlib.util
import tempfile
import unittest
from datetime import datetime
from pathlib import Path
from unittest.mock import patch

import yaml

SCRIPT = Path(__file__).resolve().parents[1] / "bin/update_scholar_citations.py"
spec = importlib.util.spec_from_file_location("citation_updater", SCRIPT)
updater = importlib.util.module_from_spec(spec)
spec.loader.exec_module(updater)


class CitationUpdateTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.output = Path(self.temp.name) / "citations.yml"
        output_patch = patch.object(updater, "OUTPUT_FILE", str(self.output))
        output_patch.start()
        self.addCleanup(output_patch.stop)
        client_patch = patch.object(updater, "scholarly")
        self.client = client_patch.start()
        self.addCleanup(client_patch.stop)
        self.client.fill.return_value = {
            "publications": [{"author_pub_id": "author:paper", "bib": {"title": "Example paper", "pub_year": "2026"}, "num_citations": 7}]
        }

    def test_first_run_creates_citation_data(self):
        updater.get_scholar_citations("author")
        data = yaml.safe_load(self.output.read_text())
        self.assertEqual(data["papers"]["author:paper"]["citations"], 7)
        self.assertEqual(data["metadata"]["last_updated"], datetime.now().strftime("%Y-%m-%d"))

    def test_bad_existing_data_can_be_replaced_after_successful_fetch(self):
        for previous in ("", "[unexpected, list]", "metadata: [", "metadata: null"):
            with self.subTest(previous=previous):
                self.output.write_text(previous)
                updater.get_scholar_citations("author")
                self.assertIn("author:paper", yaml.safe_load(self.output.read_text())["papers"])

    def test_current_data_skips_network(self):
        updater.get_scholar_citations("author")
        self.client.reset_mock()
        updater.get_scholar_citations("author")
        self.client.search_author_id.assert_not_called()

    def test_unchanged_publications_do_not_rewrite_file(self):
        updater.get_scholar_citations("author")
        data = yaml.safe_load(self.output.read_text())
        data["metadata"]["last_updated"] = "2000-01-01"
        self.output.write_text(yaml.safe_dump(data))
        before = self.output.read_bytes()
        updater.get_scholar_citations("author")
        self.assertEqual(self.output.read_bytes(), before)

    def test_fetch_failure_preserves_existing_file(self):
        self.output.write_text("metadata: {last_updated: '2000-01-01'}\npapers: {}\n")
        before = self.output.read_bytes()
        self.client.search_author_id.side_effect = RuntimeError("Service unavailable")
        with self.assertRaises(SystemExit) as raised:
            updater.get_scholar_citations("author")
        self.assertEqual(raised.exception.code, 1)
        self.assertEqual(self.output.read_bytes(), before)

    def test_empty_result_preserves_existing_file(self):
        self.output.write_text("metadata: {last_updated: '2000-01-01'}\npapers: {}\n")
        before = self.output.read_bytes()
        self.client.fill.return_value = {"publications": []}
        with self.assertRaises(SystemExit):
            updater.get_scholar_citations("author")
        self.assertEqual(self.output.read_bytes(), before)

    def test_failed_write_preserves_existing_file(self):
        self.output.write_text("metadata: {last_updated: '2000-01-01'}\npapers: {}\n")
        before = self.output.read_bytes()
        with patch.object(updater.os, "replace", side_effect=OSError("Disk error")):
            with self.assertRaises(SystemExit):
                updater.get_scholar_citations("author")
        self.assertEqual(self.output.read_bytes(), before)
        self.assertEqual(list(self.output.parent.iterdir()), [self.output])


if __name__ == "__main__":
    unittest.main()
