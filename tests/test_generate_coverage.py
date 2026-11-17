"""scripts/generate_coverage.py: per-page parsing and the generated coverage summary."""
import pytest

from conftest import load

gc = load("generate_coverage")

PAGE = """# Example Board (EB)

**Source tier:** {tier}

## Scope
Text.

## Primary source
- [Example Act, 2001](https://example.gov.in/act.pdf) — mirrored as `sources/x/example-act.pdf`
- Rules: `sources/x/example-rules.pdf`
{extra}
## Notes
None.
"""


def write(tmp_path, tier, extra=""):
    p = tmp_path / "docs" / "bis-core" / "eb.md"
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(PAGE.format(tier=tier, extra=extra), encoding="utf-8")
    return p


def test_parse_doc(tmp_path, monkeypatch):
    monkeypatch.setattr(gc, "DOCS", tmp_path / "docs")
    e = gc.parse_doc(write(tmp_path, "Statutory / regulatory text (Act)"))
    assert e == {"title": "Example Board (EB)", "tier": gc.STATUTORY_LABEL, "citation": "Example Act, 2001",
                 "n_sources": 2, "doc_link": "bis-core/eb.md"}
    e = gc.parse_doc(write(tmp_path, "Official scheme/administrative page"))
    assert e["tier"] == gc.OFFICIAL_LABEL


def test_parse_doc_requires_tier(tmp_path, monkeypatch):
    monkeypatch.setattr(gc, "DOCS", tmp_path / "docs")
    p = write(tmp_path, "x"); p.write_text(p.read_text().replace("**Source tier:**", "Tier:"))
    with pytest.raises(SystemExit):
        gc.parse_doc(p)


def _run(tmp_path, monkeypatch, pages):
    docs = tmp_path / "docs"
    for i, body in enumerate(pages):
        p = docs / "bis-core" / f"e{i}.md"; p.parent.mkdir(parents=True, exist_ok=True); p.write_text(body, encoding="utf-8")
    monkeypatch.setattr(gc, "REPO_ROOT", tmp_path)
    monkeypatch.setattr(gc, "DOCS", docs)
    monkeypatch.setattr(gc, "OUTPUT", docs / "coverage.md")
    monkeypatch.setattr(gc, "BADGE_OUTPUT", tmp_path / "badges" / "entries.json")
    gc.main()
    return (docs / "coverage.md").read_text(encoding="utf-8"), (tmp_path / "badges" / "entries.json").read_text()


def test_counts_and_badge(tmp_path, monkeypatch):
    cov, badge = _run(tmp_path, monkeypatch, [PAGE.format(tier="Statutory / regulatory text", extra=""),
                                              PAGE.format(tier="Official scheme/administrative page", extra="")])
    assert "**2 entries. 1 have the actual statutory" in cov and "1 are administrative/scheme pages" in cov
    assert '"message": "2 bodies & schemes"' in badge
    assert "| [Example Board (EB)](bis-core/e0.md) | Statutory text | Example Act, 2001 | 2 |" in cov


def test_zero_source_claim_is_derived_not_hard_coded(tmp_path, monkeypatch):
    """The summary always printed 'Zero entries have no primary source mirrored at all.' — a generated
    file asserting something the generator never checked. With an entry that mirrors nothing it must not say so."""
    bare = "# Bare Scheme\n\n**Source tier:** Official scheme/administrative page\n\n## Primary source\n- [Page](https://x.gov.in)\n\n## Notes\n"
    cov, _ = _run(tmp_path, monkeypatch, [PAGE.format(tier="Statutory / regulatory text", extra=""), bare])
    assert "| 0 |" in cov
    assert "Zero entries have no primary source mirrored" not in cov
