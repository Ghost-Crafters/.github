#!/usr/bin/env python3
"""Print the edition label for a bug report body, or nothing if the form answer is missing.

The body comes in through the ISSUE_BODY environment variable (or a file path argument),
never through a command line, so its text is only ever read as data.
"""
import os
import sys

HEADING = "### Edition"
EDITIONS = {"bedrock": "edition:bedrock", "java": "edition:java"}


def edition_label(body):
    lines = (body or "").replace("\r\n", "\n").split("\n")
    for i, line in enumerate(lines):
        if line.strip() != HEADING:
            continue
        # The form puts the answer in the first non-empty line under the heading.
        for answer in lines[i + 1:]:
            if answer.strip():
                return EDITIONS.get(answer.strip().lower())
        return None
    return None


def main(argv):
    if argv:
        with open(argv[0], encoding="utf-8") as f:
            body = f.read()
    else:
        body = os.environ.get("ISSUE_BODY", "")
    label = edition_label(body)
    if label:
        print(label)
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
