#!/usr/bin/env python3
"""Check the navigation in the Markdown docs: a Contents list that links real headings, and one
Back to top button as the last line of the doc."""
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SKIP_DIRS = {".git", ".github", "node_modules"}
SKIP_FILES = {"RELEASE_NOTES_TEMPLATE.md"}
BUTTON = "[![Back to top](https://img.shields.io/badge/Back%20to%20top-222?style=plastic&logo=github)](#{})"
HEADING = re.compile(r"^(#{1,6})\s+(.+?)\s*#*\s*$")
LINK_DEF = re.compile(r"^\[[^\]]+\]:\s")
LINK = re.compile(r"\]\(#([^)]*)\)")


def slug(title):
    title = re.sub(r"`|\*|_(?=\S)|(?<=\S)_", "", title)
    title = re.sub(r"\[([^\]]*)\]\([^)]*\)", r"\1", title)
    kept = re.sub(r"[^\w\- ]", "", title.lower())
    return kept.replace(" ", "-")


def headings(lines):
    """Return (line number, level, title) for each heading outside code fences."""
    found = []
    fence = None
    for number, line in enumerate(lines, 1):
        marker = re.match(r"^\s*(`{3,}|~{3,})", line)
        if marker:
            if fence is None:
                fence = marker.group(1)[0]
            elif marker.group(1)[0] == fence:
                fence = None
            continue
        if fence is None:
            match = HEADING.match(line)
            if match:
                found.append((number, len(match.group(1)), match.group(2)))
    return found


def slugs_of(found):
    seen = {}
    result = set()
    for _, _, title in found:
        base = slug(title)
        count = seen.get(base, 0)
        seen[base] = count + 1
        result.add(base if count == 0 else f"{base}-{count}")
    return result


def check_file(path, name=None):
    name = name or path.name
    lines = path.read_text(encoding="utf-8").splitlines()
    found = headings(lines)
    titles = [h for h in found if h[1] == 1]
    if not titles:
        return [f"{name}:1: no # title"]
    title_slug = slug(titles[0][2])
    button = BUTTON.format(title_slug)
    known = slugs_of(found)
    sections = [h for h in found if h[1] == 2]
    problems = []

    def last_content(start, stop):
        for n in range(stop, start, -1):
            text = lines[n - 1].strip()
            if text and not LINK_DEF.match(text):
                return n
        return start

    contents = [h for h in sections if h[2] == "Contents"]
    others = [h for h in sections if h[2] != "Contents"]
    if len(others) >= 2 and not contents:
        problems.append(f"{name}:{titles[0][0]}: no ## Contents section")
    for number, _, _ in contents:
        later = [h[0] for h in found if h[1] <= 2 and h[0] > number]
        stop = (later[0] - 1) if later else len(lines)
        listed = set()
        for n in range(number + 1, stop + 1):
            for target in LINK.findall(lines[n - 1]):
                listed.add(target)
                if target not in known:
                    problems.append(f"{name}:{n}: Contents link #{target} matches no heading")
        for line_no, _, title in others:
            if slug(title) not in listed:
                problems.append(f"{name}:{line_no}: {title!r} is not in Contents")
    end = last_content(titles[0][0], len(lines))
    if lines[end - 1].strip() != button:
        problems.append(f"{name}:{end}: doc does not end with the Back to top button for #{title_slug}")
    for n, line in enumerate(lines, 1):
        if button in line and n != end:
            problems.append(f"{name}:{n}: extra Back to top button, only the last line has one")
    return problems


def docs(root):
    for path in sorted(root.rglob("*.md")):
        rel = path.relative_to(root)
        if SKIP_DIRS & set(rel.parts[:-1]) or rel.name in SKIP_FILES:
            continue
        yield path, rel.as_posix()


def check(root):
    problems = []
    for path, rel in docs(root):
        problems += check_file(path, rel)
    return problems


def main():
    root = Path(sys.argv[1]).resolve() if len(sys.argv) > 1 else ROOT
    problems = check(root)
    for problem in problems:
        print(problem)
    return 1 if problems else 0


if __name__ == "__main__":
    sys.exit(main())
