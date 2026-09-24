#!/usr/bin/env python3
"""Verify every `sources/...` path mentioned in docs/**/*.md and README.md
resolves to a real file.

These are inline code spans (`sources/bis-core/bis-isi-mark.pdf`), not
markdown hyperlinks, so a hyperlink checker like lychee never looks at
them. That's exactly the class of bug this repo has already hit once
(agent-written doc pages citing a source filename that didn't match what
was actually saved) — this script exists to catch it in CI instead of by
hand.
"""
import re
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
SOURCE_REF = re.compile(r"`(sources/[^`\s]+)`")


def find_markdown_files():
    yield REPO_ROOT / "README.md"
    yield from (REPO_ROOT / "docs").rglob("*.md")


def main():
    broken = []
    checked = 0
    for md_file in find_markdown_files():
        if not md_file.is_file():
            continue
        text = md_file.read_text(encoding="utf-8", errors="replace")
        for match in SOURCE_REF.finditer(text):
            ref = match.group(1)
            checked += 1
            if not (REPO_ROOT / ref).is_file():
                line_no = text.count("\n", 0, match.start()) + 1
                broken.append((md_file.relative_to(REPO_ROOT), line_no, ref))

    if broken:
        print(f"Found {len(broken)} broken source reference(s):\n")
        for path, line_no, ref in broken:
            print(f"  {path}:{line_no}  ->  {ref}  (file does not exist)")
        print(f"\n{checked} references checked, {len(broken)} broken.")
        return 1

    print(f"{checked} source references checked, all resolve.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
