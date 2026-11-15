import os
import subprocess
import sys
import unittest
from pathlib import Path

from edition_label import edition_label

SCRIPT = Path(__file__).resolve().parent / "edition_label.py"


def form(edition, what="It crashes."):
    return f"### Edition\n\n{edition}\n\n### Version\n\n0.1.0\n\n### What happened\n\n{what}"


class EditionLabel(unittest.TestCase):
    def test_java(self):
        self.assertEqual(edition_label(form("Java")), "edition:java")

    def test_bedrock(self):
        self.assertEqual(edition_label(form("Bedrock")), "edition:bedrock")

    def test_crlf_line_endings(self):
        self.assertEqual(edition_label(form("Java").replace("\n", "\r\n")), "edition:java")

    def test_no_response(self):
        self.assertIsNone(edition_label(form("_No response_")))

    def test_missing_section_and_empty_body(self):
        self.assertIsNone(edition_label("Just some text about Java."))
        self.assertIsNone(edition_label(""))
        self.assertIsNone(edition_label(None))

    def test_heading_with_no_answer(self):
        self.assertIsNone(edition_label("### Edition\n\n"))

    def test_unknown_answer(self):
        self.assertIsNone(edition_label(form("Universal")))

    def test_injected_text_in_another_field_is_ignored(self):
        body = form("Bedrock", what="### Edition\n\nJava\n\n$(touch /tmp/x) `id` ${{ secrets.X }}")
        self.assertEqual(edition_label(body), "edition:bedrock")

    def test_injected_answer_is_not_a_label(self):
        self.assertIsNone(edition_label(form("Java\" --add-label \"priority:high")))
        self.assertIsNone(edition_label(form("edition:java; rm -rf ~")))

    def test_cli_reads_body_from_env(self):
        env = dict(os.environ, ISSUE_BODY=form("Java"))
        out = subprocess.run([sys.executable, str(SCRIPT)], capture_output=True, text=True, env=env)
        self.assertEqual(out.stdout, "edition:java\n")

    def test_cli_prints_nothing_without_answer(self):
        env = dict(os.environ, ISSUE_BODY=form("_No response_"))
        out = subprocess.run([sys.executable, str(SCRIPT)], capture_output=True, text=True, env=env)
        self.assertEqual((out.returncode, out.stdout), (0, ""))


if __name__ == "__main__":
    unittest.main()
