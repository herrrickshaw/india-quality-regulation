#!/usr/bin/env python3
"""Verify COMPENDIUM.md against the docs/ pages it was built from.

Each --check prints a distinct success-only token and exits 0 only if
every assertion for that check passes; otherwise it prints the specific
failure(s) to stderr and exits 1. Used as the CHECK oracle for GATES.md.
"""
import argparse
import re
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
DOCS = REPO_ROOT / "docs"
COMPENDIUM = REPO_ROOT / "COMPENDIUM.md"

FIELD_NAMES = ["Authority", "Status", "Established", "Legal basis", "Marks issued", "Source tier"]


def slugify(title: str) -> str:
    s = title.lower()
    s = re.sub(r"[^\w\- ]+", "", s)
    s = s.strip().replace(" ", "-")
    s = re.sub(r"-+", "-", s)
    return s


def normalize(text: str) -> str:
    """Collapse whitespace so a hard-wrapped source paragraph still matches
    the same paragraph reflowed into the compendium."""
    return re.sub(r"\s+", " ", text).strip()


def entry_docs():
    for cat_dir in sorted(DOCS.iterdir()):
        if not cat_dir.is_dir():
            continue
        for md in sorted(cat_dir.glob("*.md")):
            yield md


def load_compendium() -> str:
    if not COMPENDIUM.is_file():
        print(f"FAIL: {COMPENDIUM} does not exist", file=sys.stderr)
        sys.exit(1)
    return COMPENDIUM.read_text(encoding="utf-8")


def main_entries_region(compendium: str) -> str:
    """The slice of the compendium holding only the 36 entry sections —
    excludes Overview's own H3 subsections (e.g. "The four-layer model")
    and the Referenced Technical Standards / Source Coverage sections,
    whose own subheadings are also demoted to H3/H4 and would otherwise
    look like duplicate/extra entries or spurious content."""
    start_marker = "\n## Apex & Accreditation Infrastructure\n"
    end_marker = "\n## Referenced Technical Standards\n"
    start = compendium.index(start_marker)
    end = compendium.index(end_marker)
    return compendium[start:end]


def entry_slice(region: str, title: str) -> str:
    """The text belonging to one entry's "### <title>" section within
    main_entries_region — up to (but not including) the next "### " or
    "## " heading. Scoping to this slice (instead of a whole-document
    substring search) is what makes check_fields/check_sections able to
    catch a corruption of one entry even when another entry legitimately
    shares the same field value or similar prose."""
    marker = f"### {title}\n"
    start = region.index(marker) + len(marker)
    m = re.search(r"\n#{2,3} ", region[start:])
    end = start + m.start() if m else len(region)
    return region[start:end]


def check_headings():
    compendium = load_compendium()
    h3_titles = re.findall(r"^### (.+)$", main_entries_region(compendium), re.M)
    expected = [re.search(r"^# (.+)$", md.read_text(encoding="utf-8"), re.M).group(1)
                for md in entry_docs()]

    failures = []
    if len(h3_titles) != len(expected):
        failures.append(f"expected {len(expected)} H3 entry headings, found {len(h3_titles)}")

    expected_set = set(expected)
    found_set = set(h3_titles)
    missing = expected_set - found_set
    extra = found_set - expected_set
    if missing:
        failures.append(f"missing headings for: {sorted(missing)}")
    if extra:
        failures.append(f"unexpected headings not in any source doc: {sorted(extra)}")

    from collections import Counter
    dupes = {t: c for t, c in Counter(h3_titles).items() if c > 1}
    if dupes:
        failures.append(f"duplicate H3 headings: {dupes}")

    if failures:
        for f in failures:
            print(f"FAIL: {f}", file=sys.stderr)
        sys.exit(1)
    print(f"COMPENDIUM_HEADINGS_OK ({len(expected)} entries, exact match)")


def check_fields():
    compendium = load_compendium()
    region = main_entries_region(compendium)
    failures = []
    for md in entry_docs():
        text = md.read_text(encoding="utf-8")
        title = re.search(r"^# (.+)$", text, re.M).group(1)
        # Scoped to THIS entry's own slice — not a whole-document substring
        # search — so corrupting one entry's field can't hide behind
        # another entry that happens to share the same field value (e.g.
        # many entries share "**Status:** Infrastructure" verbatim).
        try:
            slice_ = strip_links(entry_slice(region, title))
        except ValueError:
            failures.append(f"{title}: entry heading not found in compendium at all")
            continue
        for field in FIELD_NAMES:
            m = re.search(rf"\*\*{re.escape(field)}:\*\*\s*(.+)", text)
            if not m:
                failures.append(f"{md.relative_to(REPO_ROOT)}: source doc itself missing field '{field}'")
                continue
            value_line = strip_links(f"**{field}:** {m.group(1).strip()}")
            if value_line not in slice_:
                failures.append(f"{title}: field '{field}' not found verbatim (link-stripped) in its own compendium section")

    if failures:
        for f in failures:
            print(f"FAIL: {f}", file=sys.stderr)
        sys.exit(1)
    n = sum(1 for _ in entry_docs())
    print(f"COMPENDIUM_FIELDS_OK ({n} entries × {len(FIELD_NAMES)} fields, all present verbatim)")


def strip_links(text: str) -> str:
    """Reduce [label](anything) to just label. Applied to BOTH sides before
    comparing prose, since a link's target legitimately changes between the
    source doc (relative .md path) and the compendium (#anchor) — only the
    visible text is expected to survive unchanged."""
    return re.sub(r"\[([^\]]+)\]\([^)]+\)", r"\1", text)


def check_sections():
    compendium = load_compendium()
    region = main_entries_region(compendium)
    failures = []

    for md in entry_docs():
        text = md.read_text(encoding="utf-8")
        title = re.search(r"^# (.+)$", text, re.M).group(1)
        try:
            raw_slice = entry_slice(region, title)
        except ValueError:
            failures.append(f"{title}: entry heading not found in compendium at all")
            continue
        norm_slice = normalize(strip_links(raw_slice))
        for section in ("Scope", "Notes"):
            m = re.search(rf"^## {section}\n(.*?)(?:\n## |\Z)", text, re.M | re.S)
            if not m:
                continue  # Notes is optional on some pages
            body = m.group(1).strip()
            if not body:
                continue
            # Compare sentence-by-sentence (split on blank lines / bullets)
            # rather than the whole block, so an in-body link rewrite
            # (relative .md -> #anchor) doesn't make an otherwise-intact
            # paragraph look "missing" over one changed substring.
            chunks = [c.strip() for c in re.split(r"\n\s*\n", body) if c.strip()]
            for chunk in chunks:
                # Strip markdown link syntax down to just the visible label
                # before comparing, since link targets are exactly what
                # legitimately changes between source doc and compendium.
                label_only = strip_links(chunk)
                needle = normalize(label_only)
                if len(needle) < 15:
                    continue  # too short to be a meaningful containment check
                if needle not in norm_slice:
                    failures.append(
                        f"{title} / {section}: chunk not found in its own compendium section "
                        f"(first 80 chars): {needle[:80]!r}"
                    )

        # Primary source: every citation title + URL pair must appear,
        # scoped to this entry's own slice (a URL could in principle be
        # cited by two entries, e.g. a shared parent Act).
        m = re.search(r"## Primary source\n(.*?)\n## ", text, re.S)
        if m:
            for link_title, url in re.findall(r"\[([^\]]+)\]\((https?://[^)]+)\)", m.group(1)):
                if url not in raw_slice:
                    failures.append(f"{title} / Primary source: URL missing from its own section: {url}")
                if link_title not in raw_slice:
                    failures.append(f"{title} / Primary source: citation title missing from its own section: {link_title!r}")

    if failures:
        for f in failures:
            print(f"FAIL: {f}", file=sys.stderr)
        sys.exit(1)
    n = sum(1 for _ in entry_docs())
    print(f"COMPENDIUM_SECTIONS_OK ({n} entries, Scope/Notes/Primary-source content all present)")


def check_anchors():
    compendium = load_compendium()
    headings = re.findall(r"^(#{1,6})\s+(.+)$", compendium, re.M)
    heading_slugs = {slugify(text) for _, text in headings}

    internal_links = re.findall(r"\[([^\]]+)\]\(#([^)\s]+)\)", compendium)
    if not internal_links:
        print("FAIL: no internal anchor links found at all — rewrite step likely no-op'd", file=sys.stderr)
        sys.exit(1)

    failures = []
    for label, anchor in internal_links:
        if anchor not in heading_slugs:
            failures.append(f"dead anchor #{anchor} (link text: {label!r})")

    if failures:
        for f in failures:
            print(f"FAIL: {f}", file=sys.stderr)
        sys.exit(1)
    print(f"COMPENDIUM_ANCHORS_OK ({len(internal_links)} internal links, all resolve to a real heading)")


def check_coverage_counts():
    compendium = load_compendium()

    live_total = 0
    live_statutory = 0
    for md in entry_docs():
        text = md.read_text(encoding="utf-8")
        m = re.search(r"\*\*Source tier:\*\*\s*(.+)", text)
        if not m:
            print(f"FAIL: {md}: missing Source tier field", file=sys.stderr)
            sys.exit(1)
        live_total += 1
        if m.group(1).startswith("Statutory"):
            live_statutory += 1
    live_official = live_total - live_statutory

    m = re.search(
        r"\*\*(\d+) entries\.\s*(\d+) have the actual statutory or regulatory text.*?"
        r"(\d+) are administrative/scheme pages",
        compendium,
        re.S,
    )
    if not m:
        print("FAIL: coverage summary sentence not found in compendium", file=sys.stderr)
        sys.exit(1)
    embedded_total, embedded_statutory, embedded_official = (int(x) for x in m.groups())

    failures = []
    if embedded_total != live_total:
        failures.append(f"total: embedded={embedded_total} live={live_total}")
    if embedded_statutory != live_statutory:
        failures.append(f"statutory: embedded={embedded_statutory} live={live_statutory}")
    if embedded_official != live_official:
        failures.append(f"official: embedded={embedded_official} live={live_official}")

    if failures:
        for f in failures:
            print(f"FAIL: coverage count mismatch — {f}", file=sys.stderr)
        sys.exit(1)
    print(f"COMPENDIUM_COVERAGE_COUNTS_OK (total={live_total}, statutory={live_statutory}, official={live_official})")


CHECKS = {
    "headings": check_headings,
    "fields": check_fields,
    "sections": check_sections,
    "anchors": check_anchors,
    "coverage-counts": check_coverage_counts,
}


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--check", required=True, choices=list(CHECKS) + ["all"])
    args = parser.parse_args()

    if args.check == "all":
        for name, fn in CHECKS.items():
            fn()
    else:
        CHECKS[args.check]()


if __name__ == "__main__":
    sys.exit(main())
