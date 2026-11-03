"""Unit and smoke tests for the offline generator/verifier scripts.

No network and no PDF tooling needed: PDF extraction is covered by CI's
``verify_pdf_extraction.py`` job, which needs poppler/tesseract.
"""
from __future__ import annotations

import subprocess
import sys

import build_compendium
import check_source_refs
import generate_coverage
from _common import CATEGORY_ORDER, DOCS, REPO_ROOT, slugify

SCRIPTS = REPO_ROOT / "scripts"


def test_slugify_matches_github_anchor_style():
    assert slugify("Apex & Accreditation Infrastructure") == "apex-accreditation-infrastructure"
    assert slugify("Cross-Sector Statutory — BIS Core") == "cross-sector-statutory-bis-core"
    assert slugify("  Legal Metrology ") == "legal-metrology"


def test_category_order_dirs_exist_and_cover_all_docs():
    keys = [k for k, _ in CATEGORY_ORDER]
    assert len(keys) == len(set(keys))
    on_disk = {p.name for p in DOCS.iterdir() if p.is_dir()}
    assert on_disk == set(keys)


def test_demote_and_strip_h1():
    assert build_compendium.demote("# A\ntext\n## B", 2) == "### A\ntext\n#### B"
    assert build_compendium.strip_h1("# Title\n\nbody\n") == "body\n"
    assert build_compendium.strip_h1("no heading") == "no heading"


def test_resolve_docs_relative_normalises_dotdot():
    f = build_compendium.resolve_docs_relative
    assert f("bis-core", "../apex-accreditation/nabl.md") == "apex-accreditation/nabl.md"
    assert f("", "00-overview.md") == "00-overview.md"
    assert f("bis-core", "../apex-accreditation/") == "apex-accreditation"


def test_parse_doc_reads_tier_and_sources(tmp_path, monkeypatch):
    doc = tmp_path / "cat" / "x.md"
    doc.parent.mkdir()
    doc.write_text(
        "# Thing\n\n**Source tier:** Statutory / regulatory text (Act)\n\n"
        "## Primary source\n- [The Act, 2000](https://x.example) mirrored at `sources/cat/a.pdf`"
        " and `sources/cat/a.md`\n\n## Notes\n",
        encoding="utf-8",
    )
    monkeypatch.setattr(generate_coverage, "DOCS", tmp_path)
    got = generate_coverage.parse_doc(doc)
    assert got == {
        "title": "Thing",
        "tier": generate_coverage.STATUTORY_LABEL,
        "citation": "The Act, 2000",
        "n_sources": 2,
        "doc_link": "cat/x.md",
    }


def test_source_ref_regex_ignores_globs_and_prose():
    rx = check_source_refs.SOURCE_REF
    assert rx.findall("`sources/bis-core/bis-crs.pdf`") == ["sources/bis-core/bis-crs.pdf"]
    assert rx.findall("`sources/*/MANIFEST.md` and `sources/...`") == []


def _run(*args: str) -> subprocess.CompletedProcess:
    return subprocess.run([sys.executable, *args], capture_output=True, text=True, cwd=REPO_ROOT)


def test_check_source_refs_cli_passes_on_repo():
    r = _run(str(SCRIPTS / "check_source_refs.py"))
    assert r.returncode == 0, r.stdout + r.stderr
    assert "all resolve" in r.stdout


def test_verify_compendium_cli_passes_on_repo():
    r = _run(str(SCRIPTS / "verify_compendium.py"), "--check", "all")
    assert r.returncode == 0, r.stdout + r.stderr
    assert "COMPENDIUM_COVERAGE_COUNTS_OK" in r.stdout


def test_coverage_page_matches_generator_counts():
    text = (DOCS / "coverage.md").read_text(encoding="utf-8")
    assert "**36 entries. 22 have" in text
    assert '"36 bodies & schemes"' in (REPO_ROOT / "badges" / "entries.json").read_text()
