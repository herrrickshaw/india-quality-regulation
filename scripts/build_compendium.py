#!/usr/bin/env python3
"""Build COMPENDIUM.md: every doc page (overview, all body/scheme entries,
coverage summary) flattened into one self-contained Markdown file.

Nesting: H1 = compendium title, H2 = Overview / each category / Coverage,
H3 = each entry's original title, H4 = that entry's Scope/Primary
source/Notes subsections (demoted from their original H2).

Relative doc-to-doc links (e.g. `[NABL](../apex-accreditation/nabl.md)`)
don't mean anything once everything lives in one file, so they're rewired
to in-file anchors (`#slug-of-the-target-titles-heading`) pointing at the
corresponding H3. Links to sources/ (backtick paths, not real hyperlinks)
and external http(s) links are left untouched — both still resolve
correctly from a file at the repository root.

Run `python3 scripts/verify_compendium.py --check all` after this to
confirm nothing was lost or broken in the process.
"""
import re
import sys
from datetime import date, datetime, timezone
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
DOCS = REPO_ROOT / "docs"
OUTPUT = REPO_ROOT / "COMPENDIUM.md"

CATEGORY_ORDER = [
    ("apex-accreditation", "Apex & Accreditation Infrastructure"),
    ("bis-core", "Cross-Sector Statutory — BIS Core"),
    ("food-agriculture", "Food & Agriculture"),
    ("health-pharma", "Health, Pharma & AYUSH"),
    ("energy-safety-environment", "Energy, Safety & Environment"),
    ("telecom-electronics", "Telecom & Electronics"),
    ("textiles", "Textiles & Handicrafts"),
    ("ip-trademarks", "Origin & Trademarks"),
    ("legal-metrology", "Legal Metrology"),
    ("private-voluntary", "Private / Industry Voluntary Marks"),
]

HEADING_RE = re.compile(r"^(#{1,6})(\s+.*)$", re.M)
LINK_RE = re.compile(r"\[([^\]]+)\]\(([^)\s]+)\)")


def slugify(title: str) -> str:
    """Approximation of GitHub's heading-anchor algorithm."""
    s = title.lower()
    s = re.sub(r"[^\w\- ]+", "", s)
    s = s.strip().replace(" ", "-")
    s = re.sub(r"-+", "-", s)
    return s


def demote(text: str, levels: int) -> str:
    def repl(m):
        return ("#" * (len(m.group(1)) + levels)) + m.group(2)
    return HEADING_RE.sub(repl, text)


def strip_h1(text: str) -> str:
    """Remove the first H1 line (and the blank line after it, if present)."""
    lines = text.split("\n")
    for i, line in enumerate(lines):
        if line.startswith("# "):
            rest = lines[i + 1 :]
            if rest and rest[0].strip() == "":
                rest = rest[1:]
            return "\n".join(rest)
    return text


def build_title_map():
    """docs-relative posix path -> the heading text that will actually
    anchor that content in the compendium.

    For the 36 entry pages this is just their own H1 (kept verbatim as an
    H3). For 00-overview.md and coverage.md it is NOT their own H1 — those
    two are re-headed as "Overview" / "Source Coverage" section titles in
    the compendium (see main()), so a link to them must resolve to THAT
    anchor, not to a heading that no longer exists in the output."""
    title_map = {}
    for md in DOCS.rglob("*.md"):
        text = md.read_text(encoding="utf-8")
        m = re.search(r"^# (.+)$", text, re.M)
        if m:
            title_map[md.relative_to(DOCS).as_posix()] = m.group(1)
    title_map["00-overview.md"] = "Overview"
    title_map["coverage.md"] = "Source Coverage"
    title_map["is-standards-referenced.md"] = "Referenced Technical Standards"
    return title_map


def resolve_docs_relative(doc_docs_relative_dir: str, target: str) -> str:
    """Resolve a link target (possibly with ../ segments, possibly ending
    in / for a bare directory reference) against the source doc's own
    docs/-relative directory, returning a normalized docs/-relative path
    with no trailing slash."""
    base = Path(doc_docs_relative_dir) if doc_docs_relative_dir else Path(".")
    resolved = (base / target).as_posix()
    resolved = re.sub(r"^\./", "", resolved)
    parts = []
    for part in resolved.split("/"):
        if part == "..":
            if parts:
                parts.pop()
        elif part and part != ".":
            parts.append(part)
    return "/".join(parts)


def rewrite_links(text: str, doc_docs_relative_dir: str, title_map: dict, category_map: dict) -> str:
    """Rewrite [text](relative/doc.md) links to [text](#slug), based on the
    resolved docs/-relative path of the target. A bare directory link (no
    filename, e.g. `../bis-core/`, used a couple of places to reference "the
    BIS category" loosely rather than one specific entry) is rewritten to
    that category's own section anchor via category_map. Leaves external
    links and non-.md/non-directory references (like the `sources/...`
    code spans, which aren't matched by LINK_RE's bracket syntax anyway)
    untouched."""

    def repl(m):
        label, target = m.group(1), m.group(2)
        if target.startswith(("http://", "https://", "mailto:", "#")):
            return m.group(0)

        # A target can carry a GitHub-style fragment, e.g.
        # `../sources/bis-core/bis-crs.md#L537` (line-anchor into that
        # file's blob view) — split it off before checking the extension,
        # since `target.endswith(".md")` would otherwise miss this target
        # entirely and leave a docs/-relative path uncorrected once this
        # link is flattened into a repo-root-relative COMPENDIUM.md.
        path_part, hash_sep, fragment = target.partition("#")

        if path_part.endswith(".md"):
            resolved = resolve_docs_relative(doc_docs_relative_dir, path_part)
            title = title_map.get(resolved)
            if title is not None and not fragment:
                return f"[{label}](#{slugify(title)})"
            # A link that climbs out of docs/ entirely (e.g.
            # `../../sources/bis-core/bis-isi-mark.md`, used to cite a
            # PDF's extracted-text transcription, or the #L537 case above)
            # resolves, once it clears docs/, to a path that's already
            # correct relative to the REPOSITORY ROOT — which is exactly
            # where COMPENDIUM.md lives. Point the link straight at that
            # file (plus its original fragment, if any) instead of an
            # in-file anchor.
            if resolved.startswith("sources/") and (REPO_ROOT / resolved).is_file():
                return f"[{label}]({resolved}{hash_sep}{fragment})"
            if title is not None:
                # docs/ target with a fragment lychee/GitHub wouldn't
                # resolve post-flatten anyway (it'd become an anchor); drop
                # the now-meaningless fragment and point at the section.
                return f"[{label}](#{slugify(title)})"
            print(f"WARNING: unresolved cross-link '{target}' in {doc_docs_relative_dir or '.'}",
                  file=sys.stderr)
            return m.group(0)

        if target.endswith("/"):
            resolved = resolve_docs_relative(doc_docs_relative_dir, target)
            cat_label = category_map.get(resolved)
            if cat_label is None:
                print(f"WARNING: unresolved directory link '{target}' in {doc_docs_relative_dir or '.'}",
                      file=sys.stderr)
                return m.group(0)
            return f"[{label}](#{slugify(cat_label)})"

        return m.group(0)

    return LINK_RE.sub(repl, text)


def main():
    title_map = build_title_map()
    category_map = {cat_key: cat_label for cat_key, cat_label in CATEGORY_ORDER}

    parts = []
    parts.append("# How India Regulates Quality — Compendium")
    parts.append("")
    parts.append(
        f"*Generated by `scripts/build_compendium.py` on "
        f"{datetime.now(timezone.utc).strftime('%Y-%m-%d')} from every page under `docs/` — "
        f"a single-file version of the same content for offline reading or pasting elsewhere. "
        f"The maintained source is `docs/`; re-run the generator after editing a doc page "
        f"instead of hand-editing this file.*"
    )
    parts.append("")
    parts.append(
        "This file is self-contained except for two things every entry still points back to "
        "the repository for: the mirrored primary-source files under `sources/...` (cited as "
        "code spans, e.g. `sources/bis-core/bis-isi-mark.pdf`), and each category's "
        "`sources/*/MANIFEST.md`. Open this file from the repository root for those paths to "
        "resolve; every other link in this document is an in-file anchor."
    )
    parts.append("")

    def embed_top_level_doc(filename: str, section_title: str):
        """Embed a docs/-root page (Overview, the IS-standards catalogue,
        Coverage) as its own H2 section, titled section_title rather than
        the page's own H1 — must match the title_map override above so
        cross-links resolve to the heading this actually produces."""
        text = (DOCS / filename).read_text(encoding="utf-8")
        body = strip_h1(text)
        body = rewrite_links(body, "", title_map, category_map)
        body = demote(body, 1)
        parts.append(f"## {section_title}")
        parts.append("")
        parts.append(body.strip())
        parts.append("")

    embed_top_level_doc("00-overview.md", "Overview")

    # --- Each category, each entry ---
    for cat_key, cat_label in CATEGORY_ORDER:
        cat_dir = DOCS / cat_key
        if not cat_dir.is_dir():
            continue
        entries = sorted(cat_dir.glob("*.md"))
        # A category whose one entry shares its exact name (Legal Metrology
        # today) would otherwise put two identically-worded headings in the
        # doc — the category H2 and the entry's own H3 — and GitHub's
        # anchor-disambiguation would silently shift whichever link targets
        # "Legal Metrology" onto the wrong one of the two. Skip the
        # redundant category header in that specific case; the entry's own
        # H3 already says everything the category header would.
        single_entry_same_name = (
            len(entries) == 1
            and re.search(r"^# (.+)$", entries[0].read_text(encoding="utf-8"), re.M).group(1)
            == cat_label
        )
        if not single_entry_same_name:
            parts.append(f"## {cat_label}")
            parts.append("")
        for md in entries:
            text = md.read_text(encoding="utf-8")
            title_match = re.search(r"^# (.+)$", text, re.M)
            title = title_match.group(1)
            body = strip_h1(text)
            body = rewrite_links(body, cat_key, title_map, category_map)
            body = demote(body, 2)
            parts.append(f"### {title}")
            parts.append("")
            parts.append(body.strip())
            parts.append("")

    embed_top_level_doc("is-standards-referenced.md", "Referenced Technical Standards")
    embed_top_level_doc("coverage.md", "Source Coverage")

    OUTPUT.write_text("\n".join(parts), encoding="utf-8")
    print(f"Wrote {OUTPUT.relative_to(REPO_ROOT)} "
          f"({len(OUTPUT.read_text(encoding='utf-8').splitlines())} lines).")


if __name__ == "__main__":
    sys.exit(main())
