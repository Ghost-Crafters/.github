import unittest
from pathlib import Path

import yaml

WORKFLOWS = Path(__file__).resolve().parent.parent / ".github" / "workflows"


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

    def test_no_answer_branch_removes_labels(self):
        head = self.script.split("gh issue edit \"$ISSUE_NUMBER\" --add-label")[0]
        start = head.index('if [ -z "$label" ]')
        self.assertIn("### Edition", head[start:head.index("No edition answer")])
        removing = head[head.index("No edition answer"):]
        self.assertIn("--remove-label", removing)
        self.assertIn("edition:bedrock", removing)
        self.assertIn("edition:java", removing)


class StaleWorkflow(unittest.TestCase):
    def test_pull_requests_are_ignored(self):
        step = load("stale-bug-reports.yml")["jobs"]["stale"]["steps"][0]["with"]
        self.assertIs(step["remove-pr-stale-when-updated"], False)
        self.assertEqual(step["days-before-pr-stale"], -1)
        self.assertEqual(step["days-before-pr-close"], -1)


if __name__ == "__main__":
    unittest.main()
