import tempfile
import unittest
from pathlib import Path

import check_docs

ROOT = Path(__file__).resolve().parent.parent
BUTTON = check_docs.BUTTON.format("guide")

GOOD = f"""# Guide

Intro.

## Contents

- [One](#one)
- [Two's](#twos)

## One

Text.

## Two's

Text.

{BUTTON}
"""


class CheckDocsTest(unittest.TestCase):
    def run_check(self, text):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "GUIDE.md"
            path.write_text(text, encoding="utf-8")
            return check_docs.check_file(path)

    def test_repo_docs_pass(self):
        self.assertEqual(check_docs.check(ROOT), [])

    def test_slug(self):
        self.assertEqual(check_docs.slug("Contributor Covenant Code of Conduct"), "contributor-covenant-code-of-conduct")
        self.assertEqual(check_docs.slug(".github"), "github")
        self.assertEqual(check_docs.slug("Which version you're running"), "which-version-youre-running")
        self.assertEqual(check_docs.slug("1. Correction"), "1-correction")

    def test_good_doc_passes(self):
        self.assertEqual(self.run_check(GOOD), [])

    def test_missing_button_reports_last_line(self):
        problems = self.run_check(GOOD.replace(f"\n{BUTTON}\n", ""))
        self.assertEqual(len(problems), 1)
        self.assertTrue(problems[0].startswith("GUIDE.md:16:"))

    def test_button_after_each_section_fails(self):
        problems = self.run_check(GOOD.replace("Text.\n\n## Two", f"Text.\n\n{BUTTON}\n\n## Two"))
        self.assertEqual(len(problems), 1)
        self.assertIn("extra Back to top button", problems[0])

    def test_button_with_wrong_anchor_fails(self):
        problems = self.run_check(GOOD.replace("(#guide)", "(#other)", 1))
        self.assertEqual(len(problems), 1)

    def test_dead_contents_link_fails(self):
        problems = self.run_check(GOOD.replace("(#one)", "(#missing)"))
        self.assertTrue(any("#missing" in p for p in problems))

    def test_heading_missing_from_contents_fails(self):
        problems = self.run_check(GOOD.replace("- [One](#one)\n", ""))
        self.assertEqual(len(problems), 1)

    def test_button_in_contents_fails(self):
        problems = self.run_check(GOOD.replace("- [Two's](#twos)\n", f"- [Two's](#twos)\n\n{BUTTON}\n"))
        self.assertEqual(len(problems), 1)

    def test_single_section_needs_button_but_no_contents(self):
        self.assertEqual(self.run_check(f"# Guide\n\nText.\n\n{BUTTON}\n"), [])
        self.assertEqual(len(self.run_check("# Guide\n\nText.\n")), 1)

    def test_link_definitions_after_button_are_allowed(self):
        text = GOOD + "\n[ref]: https://example.com\n"
        self.assertEqual(self.run_check(text), [])

    def test_headings_in_code_fences_are_ignored(self):
        text = GOOD.replace("Text.\n\n## Two", "```\n## Fake\n```\n\n## Two", 1)
        self.assertEqual(self.run_check(text), [])


if __name__ == "__main__":
    unittest.main()
