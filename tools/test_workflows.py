import json
import os
import shutil
import subprocess
import tempfile
import unittest
from pathlib import Path

import yaml

TOOLS = Path(__file__).resolve().parent
WORKFLOWS = TOOLS.parent / ".github" / "workflows"


def load(name):
    return yaml.safe_load((WORKFLOWS / name).read_text(encoding="utf-8"))


class EditionLabelWorkflow(unittest.TestCase):
    def setUp(self):
        self.job = load("edition-label.yml")["jobs"]["label"]
        self.script = self.job["steps"][-1]["run"]

    def test_runs_for_one_issue_queue_up(self):
        group = self.job["concurrency"]
        self.assertIn("github.event.issue.number", group["group"])
        self.assertIn("github.repository", group["group"])
        self.assertIs(group["cancel-in-progress"], False)

    def test_reads_current_issue_not_event_payload(self):
        step = self.job["steps"][-1]
        self.assertIn("gh issue view", self.script)
        self.assertNotIn("github.event.issue.body", str(step))
        self.assertNotIn("ISSUE_BODY", str(step))

    def run_script(self, body, labels, fail_remove=False):
        """Run the step's script with a stand-in gh that serves the issue and logs every edit."""
        tmp = Path(tempfile.mkdtemp())
        self.addCleanup(shutil.rmtree, tmp)
        (tmp / "bin").mkdir()
        (tmp / "fixture.json").write_text(json.dumps({"body": body, "labels": [{"name": n} for n in labels]}))
        gh = tmp / "bin" / "gh"
        gh.write_text("#!/bin/sh\n"
                      'if [ "$2" = view ]; then cat "$FAKE_ISSUE"; exit 0; fi\n'
                      'echo "$*" >> "$FAKE_LOG"\n'
                      'case "$*" in *--remove-label*) [ -n "$FAKE_FAIL" ] && exit 1;; esac\n'
                      "exit 0\n")
        gh.chmod(0o755)
        env = dict(os.environ, PATH=f"{tmp / 'bin'}:{os.environ['PATH']}", RUNNER_TEMP=str(tmp), ISSUE_NUMBER="7",
                   FAKE_ISSUE=str(tmp / "fixture.json"), FAKE_LOG=str(tmp / "log"), FAKE_FAIL="1" if fail_remove else "")
        done = subprocess.run(["bash", "-e", "-c", self.script], cwd=TOOLS.parent, env=env, capture_output=True,
                              text=True)
        log = (tmp / "log").read_text().splitlines() if (tmp / "log").exists() else []
        return done.returncode, log

    def test_answer_swaps_the_edition_label(self):
        code, log = self.run_script("### Edition\n\nJava\n", ["edition:bedrock", "bug"])
        self.assertEqual(code, 0)
        self.assertEqual(log, ["issue edit 7 --remove-label edition:bedrock", "issue edit 7 --add-label edition:java"])

    def test_removed_answer_removes_only_attached_edition_labels(self):
        code, log = self.run_script("### Edition\n\n_No response_\n", ["edition:java"])
        self.assertEqual(code, 0)
        self.assertEqual(log, ["issue edit 7 --remove-label edition:java"])

    def test_issue_without_the_form_is_left_alone(self):
        code, log = self.run_script("Just a question about Java.", ["edition:java"])
        self.assertEqual(code, 0)
        self.assertEqual(log, [])

    def test_failed_removal_fails_the_job_before_adding(self):
        code, log = self.run_script("### Edition\n\nBedrock\n", ["edition:java"], fail_remove=True)
        self.assertNotEqual(code, 0)
        self.assertNotIn("issue edit 7 --add-label edition:bedrock", log)

    def test_removal_failures_stop_the_job(self):
        # Only labels the issue has are removed, so a failing removal is a real error and isn't hidden.
        self.assertNotIn("|| true", self.script)
        self.assertIn("--json body,labels", self.script)


class StaleWorkflow(unittest.TestCase):
    def test_can_save_its_state(self):
        # actions/stale keeps its place between runs in the Actions cache, which needs actions: write.
        self.assertEqual(load("stale-bug-reports.yml")["permissions"].get("actions"), "write")

    def test_pull_requests_are_ignored(self):
        step = load("stale-bug-reports.yml")["jobs"]["stale"]["steps"][0]["with"]
        self.assertIs(step["remove-pr-stale-when-updated"], False)
        self.assertEqual(step["days-before-pr-stale"], -1)
        self.assertEqual(step["days-before-pr-close"], -1)


if __name__ == "__main__":
    unittest.main()
