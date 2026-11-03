#!/usr/bin/env python3
"""Verify every `sources/...` path mentioned in docs/**/*.md, COMPENDIUM.md,
and README.md resolves to a real file.

These are inline code spans (`sources/bis-core/bis-isi-mark.pdf`), not
markdown hyperlinks, so a hyperlink checker like lychee never looks at
them. That's exactly the class of bug this repo has already hit once
(agent-written doc pages citing a source filename that didn't match what
was actually saved) — this script exists to catch it in CI instead of by
hand.
"""
from __future__ import annotations

import re
import sys

from _common import REPO_ROOT

# Require a real file extension, and exclude `*` (glob wildcards never
# appear in a real path), so prose like `` `sources/...` `` or
# `` `sources/*/MANIFEST.md` `` (used to describe the pattern, e.g. in this
# file's own docstring, the README, or COMPENDIUM.md's intro) is never
# mistaken for an actual reference.
SOURCE_REF = re.compile(r"`(sources/[^`\s*]+\.[a-zA-Z0-9]+)`")


def find_markdown_files():
    yield REPO_ROOT / "README.md"
    yield REPO_ROOT / "COMPENDIUM.md"
    yield from (REPO_ROOT / "docs").rglob("*.md")


def main() -> int:
    """Return 1 if any `sources/...` reference is broken, else 0."""
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
