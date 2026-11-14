#!/usr/bin/env python3
"""Check the issue forms in .github/ISSUE_TEMPLATE against GitHub's form syntax and labels.json."""
import json
import sys
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parent.parent
FIELD_TYPES = {"markdown", "input", "textarea", "dropdown", "checkboxes"}
CONFIG_KEYS = {"blank_issues_enabled", "contact_links"}


def known_labels(root):
    data = json.loads((root / "labels.json").read_text(encoding="utf-8"))
    return {label["name"] for group in data.values() for label in group}


def check_form(path, labels):
    problems = []
    form = yaml.safe_load(path.read_text(encoding="utf-8"))
    if not isinstance(form, dict):
        return [f"{path.name}: not a YAML mapping"]
    for key in ("name", "description", "body"):
        if not form.get(key):
            problems.append(f"{path.name}: missing {key}")
    for label in form.get("labels") or []:
        if label not in labels:
            problems.append(f"{path.name}: label {label!r} is not in labels.json")
    ids = set()
    for n, field in enumerate(form.get("body") or [], 1):
        kind = field.get("type") if isinstance(field, dict) else None
        if kind not in FIELD_TYPES:
            problems.append(f"{path.name}: field {n} has unknown type {kind!r}")
            continue
        if kind == "markdown":
            if not (field.get("attributes") or {}).get("value"):
                problems.append(f"{path.name}: markdown field {n} has no value")
            continue
        if not (field.get("attributes") or {}).get("label"):
            problems.append(f"{path.name}: field {n} has no label")
        fid = field.get("id")
        if fid in ids:
            problems.append(f"{path.name}: id {fid!r} is used twice")
        ids.add(fid)
        if kind == "dropdown" and not (field.get("attributes") or {}).get("options"):
            problems.append(f"{path.name}: dropdown {fid!r} has no options")
    return problems


def check_config(path):
    config = yaml.safe_load(path.read_text(encoding="utf-8"))
    if not isinstance(config, dict):
        return [f"{path.name}: not a YAML mapping"]
    problems = [f"{path.name}: unknown key {key!r}" for key in config if key not in CONFIG_KEYS]
    for n, link in enumerate(config.get("contact_links") or [], 1):
        for key in ("name", "url", "about"):
            if not link.get(key):
                problems.append(f"{path.name}: contact link {n} has no {key}")
        if not str(link.get("url", "")).startswith("https://"):
            problems.append(f"{path.name}: contact link {n} is not an https URL")
    return problems


def check(root):
    folder = root / ".github" / "ISSUE_TEMPLATE"
    labels = known_labels(root)
    problems = []
    forms = sorted(p for p in folder.glob("*.y*ml") if p.stem != "config")
    if not forms:
        problems.append("no issue forms found")
    for path in forms:
        try:
            problems += check_form(path, labels)
        except yaml.YAMLError as err:
            problems.append(f"{path.name}: YAML does not parse: {err}")
    config = folder / "config.yml"
    if config.exists():
        try:
            problems += check_config(config)
        except yaml.YAMLError as err:
            problems.append(f"config.yml: YAML does not parse: {err}")
    return problems


def main(argv=None):
    args = sys.argv[1:] if argv is None else argv
    root = Path(args[0]) if args else ROOT
    problems = check(root)
    for line in problems:
        print(line)
    print("forms OK" if not problems else f"{len(problems)} problem(s)")
    return 1 if problems else 0


if __name__ == "__main__":
    sys.exit(main())
