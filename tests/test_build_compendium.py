"""scripts/build_compendium.py: anchors, heading demotion, link rewriting and reproducible output."""
import datetime as dt
from pathlib import Path

import pytest

from conftest import load

bc = load("build_compendium")
vc = load("verify_compendium")


@pytest.mark.parametrize("title,slug", [
    ("BIS — ISI Mark", "bis--isi-mark"),
    ("Health, Pharma & AYUSH", "health-pharma--ayush"),
    ("Cross-Sector Statutory — BIS Core", "cross-sector-statutory--bis-core"),
    ("National Accreditation Board for Hospitals & Healthcare Providers (NABH)",
     "national-accreditation-board-for-hospitals--healthcare-providers-nabh"),
    ("Legal Metrology", "legal-metrology"),
    ("FSSAI", "fssai"),
])
def test_slugify_matches_github_anchors(title, slug):
    """GitHub's heading anchor = lowercase, drop punctuation, each space -> '-', with NO collapsing of
    repeated hyphens. Collapsing them sent 56 of the compendium's 120 in-file links (every heading with
    an em dash or '&') to anchors that do not exist on GitHub. verify_compendium shares the same
    slugify, so its anchor check could not see it."""
    assert bc.slugify(title) == slug
    assert vc.slugify(title) == slug


def test_demote_and_strip_h1():
    assert bc.demote("# A\n## B\ntext", 2) == "### A\n#### B\ntext"
    assert bc.strip_h1("# Title\n\nBody\n# Not first") == "Body\n# Not first"
    assert bc.strip_h1("no heading") == "no heading"


@pytest.mark.parametrize("base,target,out", [
    ("bis-core", "../apex-accreditation/nabl.md", "apex-accreditation/nabl.md"),
    ("bis-core", "bis-isi-mark.md", "bis-core/bis-isi-mark.md"),
    ("", "./00-overview.md", "00-overview.md"),
    ("bis-core", "../", ""),
    ("bis-core", "../../sources/bis-core/x.md", "sources/bis-core/x.md"),
])
def test_resolve_docs_relative(base, target, out):
    assert bc.resolve_docs_relative(base, target) == out


def test_rewrite_links():
    tm = {"apex-accreditation/nabl.md": "NABL — Testing Labs", "00-overview.md": "Overview"}
    cm = {"bis-core": "Cross-Sector Statutory — BIS Core"}
    text = ("[NABL](../apex-accreditation/nabl.md) [ext](https://bis.gov.in/x.md) [frag](#here) "
            "[cat](../bis-core/) [ov](../00-overview.md#scope) [gone](../nope.md)")
    out = bc.rewrite_links(text, "food-agriculture", tm, cm)
    assert "[NABL](#nabl--testing-labs)" in out
    assert "[ext](https://bis.gov.in/x.md)" in out and "[frag](#here)" in out
    assert "[cat](#cross-sector-statutory--bis-core)" in out
    assert "[ov](#overview)" in out                # fragment into a flattened doc dropped
    assert "[gone](../nope.md)" in out             # unresolved left as-is (warned)


def test_rebuild_from_unchanged_docs_is_byte_identical(monkeypatch, tmp_path):
    """CI regenerates COMPENDIUM.md and fails on `git diff --exit-code`. The header embedded today's date,
    so a rebuild from unchanged docs on any later day (e.g. the monthly scheduled run) produced a diff."""
    out = tmp_path / "COMPENDIUM.md"
    monkeypatch.setattr(bc, "OUTPUT", out)
    monkeypatch.setattr(bc, "REPO_ROOT", tmp_path.parent)  # only used for the printed relative path

    class Day1(dt.datetime):
        @classmethod
        def now(cls, tz=None):
            return dt.datetime(2026, 1, 1, tzinfo=tz)

    class Day2(Day1):
        @classmethod
        def now(cls, tz=None):
            return dt.datetime(2026, 2, 1, tzinfo=tz)

    monkeypatch.setattr(bc, "datetime", Day1)
    bc.main()
    first = out.read_text(encoding="utf-8")
    monkeypatch.setattr(bc, "datetime", Day2)
    bc.main()
    assert out.read_text(encoding="utf-8") == first
