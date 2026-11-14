import shutil
import tempfile
import unittest
from pathlib import Path

import check_forms

ROOT = Path(__file__).resolve().parent.parent


class CheckFormsTest(unittest.TestCase):
    def setUp(self):
        self.tmp = Path(tempfile.mkdtemp())
        shutil.copytree(ROOT / ".github", self.tmp / ".github")
        shutil.copy(ROOT / "labels.json", self.tmp / "labels.json")
        self.forms = self.tmp / ".github" / "ISSUE_TEMPLATE"

    def tearDown(self):
        shutil.rmtree(self.tmp)

    def edit(self, name, old, new):
        path = self.forms / name
        text = path.read_text(encoding="utf-8")
        self.assertIn(old, text)
        path.write_text(text.replace(old, new, 1), encoding="utf-8")

    def test_current_forms_pass(self):
        self.assertEqual(check_forms.check(ROOT), [])

    def test_missing_body_fails(self):
        path = self.forms / "feature_request.yml"
        text = path.read_text(encoding="utf-8")
        path.write_text(text.split("body:")[0], encoding="utf-8")
        self.assertIn("feature_request.yml: missing body", check_forms.check(self.tmp))

    def test_unknown_label_fails(self):
        self.edit("bug_report.yml", 'labels: ["bug"]', 'labels: ["crash"]')
        self.assertIn("bug_report.yml: label 'crash' is not in labels.json", check_forms.check(self.tmp))

    def test_duplicate_id_fails(self):
        self.edit("bug_report.yml", "id: expected", "id: what")
        self.assertIn("bug_report.yml: id 'what' is used twice", check_forms.check(self.tmp))

    def test_unknown_field_type_fails(self):
        self.edit("feature_request.yml", "type: textarea", "type: textbox")
        self.assertIn("feature_request.yml: field 2 has unknown type 'textbox'", check_forms.check(self.tmp))

    def test_dropdown_without_options_fails(self):
        path = self.forms / "feature_request.yml"
        text = path.read_text(encoding="utf-8")
        start = text.index("      options:")
        end = text.index("    validations:", start)
        path.write_text(text[:start] + text[end:], encoding="utf-8")
        self.assertIn("feature_request.yml: dropdown 'edition' has no options", check_forms.check(self.tmp))

    def test_broken_yaml_fails(self):
        (self.forms / "broken.yml").write_text("name: [unclosed\n", encoding="utf-8")
        problems = check_forms.check(self.tmp)
        self.assertTrue(any(p.startswith("broken.yml: YAML does not parse") for p in problems))

    def test_config_unknown_key_fails(self):
        self.edit("config.yml", "blank_issues_enabled", "blank_issues")
        self.assertIn("config.yml: unknown key 'blank_issues'", check_forms.check(self.tmp))

    def test_config_link_without_https_fails(self):
        self.edit("config.yml", "url: https://github.com/Ghost-Crafters\n", "url: http://github.com/Ghost-Crafters\n")
        self.assertIn("config.yml: contact link 2 is not an https URL", check_forms.check(self.tmp))

    def test_no_forms_fails(self):
        for path in self.forms.glob("*.yml"):
            if path.stem != "config":
                path.unlink()
        self.assertIn("no issue forms found", check_forms.check(self.tmp))

    def test_main_exit_codes(self):
        self.assertEqual(check_forms.main([]), 0)
        (self.forms / "bug_report.yml").write_text("name: x\n", encoding="utf-8")
        self.assertEqual(check_forms.main([str(self.tmp)]), 1)


if __name__ == "__main__":
    unittest.main()
