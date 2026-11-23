"""build_compendium.rewrite_links edge branches; check_source_refs and generate_coverage CLI paths on tmp trees."""

import pytest

from conftest import load

bc = load("build_compendium")
csr = load("check_source_refs")


def test_source_links_keep_repo_relative_paths_and_fragments(monkeypatch, tmp_path):
    (tmp_path / "sources" / "bis-core").mkdir(parents=True)
    (tmp_path / "sources" / "bis-core" / "x.md").write_text("t")
    monkeypatch.setattr(bc, "REPO_ROOT", tmp_path)
    titles = {"bis-core/entry.md": "Entry"}
    out = bc.rewrite_links("[a](../../sources/bis-core/x.md) [b](../../sources/bis-core/x.md#L5)", "bis-core", titles, {})
    assert out == "[a](sources/bis-core/x.md) [b](sources/bis-core/x.md#L5)"
    # a sources/ path that does not exist falls through to the unresolved warning, link left untouched
    gone = "[c](../../sources/bis-core/missing.md)"
    assert bc.rewrite_links(gone, "bis-core", titles, {}) == gone


def test_doc_links_with_fragments_become_section_anchors():
    titles = {"bis-core/entry.md": "BIS — Entry"}
    assert bc.rewrite_links("[e](entry.md#part)", "bis-core", titles, {}) == "[e](#bis--entry)"
    assert bc.rewrite_links("[e](entry.md)", "bis-core", titles, {}) == "[e](#bis--entry)"


def test_unresolved_links_warn_on_stderr(capsys):
    text = "[a](nope.md) [d](../nodir/) [x](file.txt) [m](mailto:a@b.c)"
    assert bc.rewrite_links(text, "bis-core", {}, {}) == text
    err = capsys.readouterr().err
    assert "WARNING: unresolved cross-link 'nope.md' in bis-core" in err
    assert "WARNING: unresolved directory link '../nodir/' in bis-core" in err and "file.txt" not in err
    bc.rewrite_links("[a](nope.md)", "", {}, {})
    assert "in ." in capsys.readouterr().err


def test_check_source_refs_reports_broken_paths_with_line_numbers(monkeypatch, tmp_path, capsys):
    (tmp_path / "docs" / "cat").mkdir(parents=True)
    (tmp_path / "sources" / "cat").mkdir(parents=True)
    (tmp_path / "sources" / "cat" / "ok.pdf").write_bytes(b"x")
    (tmp_path / "README.md").write_text("see `sources/cat/ok.pdf` and `sources/*/MANIFEST.md` and `sources/...`\n")
    (tmp_path / "docs" / "cat" / "a.md").write_text("line1\nline2 `sources/cat/gone.pdf` here\n")
    monkeypatch.setattr(csr, "REPO_ROOT", tmp_path)
    assert csr.main() == 1
    out = capsys.readouterr().out
    assert "Found 1 broken source reference(s):" in out and "docs/cat/a.md:2  ->  sources/cat/gone.pdf" in out
    assert "2 references checked, 1 broken." in out
    (tmp_path / "docs" / "cat" / "a.md").write_text("fine `sources/cat/ok.pdf`\n")
    assert csr.main() == 0
    assert capsys.readouterr().out == "2 source references checked, all resolve.\n"
