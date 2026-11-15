#!/usr/bin/env python3
"""Create or update the labels from labels.json in one repo, using the gh CLI."""
import argparse
import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent


def gh(*args):
    done = subprocess.run(["gh", *args], capture_output=True, text=True)
    if done.returncode != 0:
        sys.exit(f"gh {' '.join(args)} failed: {done.stderr.strip()}")
    return done.stdout


def wanted_labels(path):
    data = json.loads(Path(path).read_text(encoding="utf-8"))
    return [label for group in data.values() for label in group]


def plan(wanted, existing, prune):
    """Return a list of (action, label) with action create, update or delete."""
    have = {label["name"].lower(): label for label in existing}
    changes = []
    names = set()
    for label in wanted:
        names.add(label["name"].lower())
        current = have.get(label["name"].lower())
        if current is None:
            changes.append(("create", label))
        elif (current["color"].lower() != label["color"].lower()
              or (current.get("description") or "") != label["description"]
              or current["name"] != label["name"]):
            # Keep the spelling that exists on the repo, so gh can find it, and rename it with --name.
            changes.append(("update", dict(label, existing_name=current["name"])))
    if prune:
        for key, label in have.items():
            if key not in names:
                changes.append(("delete", label))
    return changes


def in_use(repo, name):
    for kind in ("issue", "pr"):
        out = gh(kind, "list", "-R", repo, "--label", name, "--state", "all",
                 "--limit", "1", "--json", "number")
        if json.loads(out):
            return True
    return False


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("repo", help="owner/repo")
    parser.add_argument("--dry-run", action="store_true", help="list the changes and make none")
    parser.add_argument("--prune", action="store_true",
                        help="delete labels that are not in labels.json and have no issues or pull requests")
    parser.add_argument("--labels", default=ROOT / "labels.json", help="path to the label file")
    args = parser.parse_args(argv)

    existing = json.loads(gh("label", "list", "-R", args.repo, "--limit", "1000",
                             "--json", "name,color,description"))
    changes = plan(wanted_labels(args.labels), existing, args.prune)
    done = 0
    for action, label in changes:
        name = label["name"]
        if action == "delete" and in_use(args.repo, name):
            print(f"keep    {name} (not in labels.json, but has issues or pull requests)")
            continue
        print(f"{'would ' if args.dry_run else ''}{action:<6}  {name}")
        done += 1
        if args.dry_run:
            continue
        if action == "delete":
            gh("label", "delete", name, "-R", args.repo, "--yes")
        else:
            if action == "create":
                gh("label", "create", name, "-R", args.repo,
                   "--color", label["color"], "--description", label["description"])
            else:
                gh("label", "edit", label["existing_name"], "-R", args.repo, "--name", name,
                   "--color", label["color"], "--description", label["description"])
    print(f"{done} change(s){' (dry run, nothing written)' if args.dry_run else ''}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
