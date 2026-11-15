import json
import os
import stat
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

TOOLS = Path(__file__).resolve().parent
WRAPPER = TOOLS / "sync-labels.sh"

# A stand-in gh: serves the labels in $FAKE_STATE (a JSON list) and records every call.
# Writes update the state, so a second run sees the result of the first.
STUB = r'''#!/usr/bin/env python3
import json, os, sys
a = sys.argv[1:]
state = os.environ["FAKE_STATE"]
with open(os.environ["FAKE_LOG"], "a") as f:
    f.write(" ".join(a) + "\n")
labels = json.load(open(state))
def opt(name):
    return a[a.index(name) + 1]
if a[:2] == ["label", "list"]:
    print(json.dumps(labels))
elif a[0] in ("issue", "pr") and a[1] == "list":
    used = json.loads(os.environ.get("FAKE_USED", "[]"))
    print(json.dumps([{"number": 1}] if opt("--label") in used else []))
elif a[:2] in (["label", "create"], ["label", "edit"]):
    labels = [l for l in labels if l["name"].lower() != a[2].lower()]
    labels.append({"name": a[2], "color": opt("--color"), "description": opt("--description")})
    json.dump(labels, open(state, "w"))
elif a[:2] == ["label", "delete"]:
    labels = [l for l in labels if l["name"] != a[2]]
    json.dump(labels, open(state, "w"))
else:
    sys.exit("unexpected call: " + " ".join(a))
'''

WANTED = {
    "type": [{"name": "bug", "color": "d73a4a", "description": "Something is broken"}],
    "edition": [{"name": "edition:java", "color": "e99695", "description": "Java Edition"}],
}


class SyncLabels(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        d = Path(self.tmp.name)
        (d / "bin").mkdir()
        gh = d / "bin" / "gh"
        gh.write_text(STUB)
        gh.chmod(gh.stat().st_mode | stat.S_IEXEC)
        self.state = d / "state.json"
        self.log = d / "calls.log"
        self.log.write_text("")
        self.labels = d / "labels.json"
        self.labels.write_text(json.dumps(WANTED))
        self.env = dict(os.environ, PATH=f"{d / 'bin'}:{os.environ['PATH']}",
                        FAKE_STATE=str(self.state), FAKE_LOG=str(self.log), FAKE_USED="[]")

    def set_repo(self, labels):
        self.state.write_text(json.dumps(labels))

    def run_tool(self, *args):
        done = subprocess.run([str(WRAPPER), "org/repo", "--labels", str(self.labels), *args],
                              capture_output=True, text=True, env=self.env)
        self.assertEqual(done.returncode, 0, done.stderr)
        return done.stdout

    def writes(self):
        return [l for l in self.log.read_text().splitlines()
                if l.startswith(("label create", "label edit", "label delete"))]

    def test_creates_missing_and_second_run_changes_nothing(self):
        self.set_repo([])
        out = self.run_tool()
        self.assertIn("create  bug", out)
        self.assertIn("create  edition:java", out)
        self.assertEqual(len(self.writes()), 2)
        self.log.write_text("")
        out = self.run_tool()
        self.assertIn("0 change(s)", out)
        self.assertEqual(self.writes(), [])

    def test_updates_color_and_description(self):
        self.set_repo([{"name": "bug", "color": "000000", "description": "Old"},
                       {"name": "edition:java", "color": "E99695", "description": "Java Edition"}])
        out = self.run_tool()
        self.assertIn("update  bug", out)
        self.assertNotIn("edition:java", out)
        self.assertEqual(len(self.writes()), 1)

    def test_dry_run_lists_and_writes_nothing(self):
        self.set_repo([{"name": "old", "color": "ffffff", "description": ""}])
        out = self.run_tool("--dry-run", "--prune")
        self.assertIn("would create  bug", out)
        self.assertIn("would delete  old", out)
        self.assertEqual(self.writes(), [])
        self.assertEqual(json.loads(self.state.read_text())[0]["name"], "old")

    def test_extra_labels_stay_without_prune(self):
        self.set_repo([{"name": "area:x", "color": "ffffff", "description": ""}])
        self.run_tool()
        self.assertFalse([w for w in self.writes() if "delete" in w])
        self.assertIn("area:x", [l["name"] for l in json.loads(self.state.read_text())])

    def test_prune_deletes_unused_but_keeps_labels_with_issues(self):
        self.set_repo([{"name": "unused", "color": "ffffff", "description": ""},
                       {"name": "busy", "color": "ffffff", "description": ""}])
        self.env["FAKE_USED"] = json.dumps(["busy"])
        out = self.run_tool("--prune")
        self.assertIn("delete  unused", out)
        self.assertIn("keep    busy", out)
        names = [l["name"] for l in json.loads(self.state.read_text())]
        self.assertNotIn("unused", names)
        self.assertIn("busy", names)

    def test_labels_file_is_valid(self):
        sys.path.insert(0, str(TOOLS))
        import sync_labels
        labels = sync_labels.wanted_labels(TOOLS.parent / "labels.json")
        self.assertEqual(len({l["name"].lower() for l in labels}), len(labels))


if __name__ == "__main__":
    unittest.main()
