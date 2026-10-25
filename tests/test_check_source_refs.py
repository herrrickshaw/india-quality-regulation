"""scripts/check_source_refs.py on a synthetic repo tree."""
from conftest import load

cs = load("check_source_refs")


def test_detects_broken_refs_and_ignores_patterns(tmp_path, monkeypatch, capsys):
    (tmp_path / "sources/bis").mkdir(parents=True)
    (tmp_path / "sources/bis/ok.pdf").write_bytes(b"%PDF")
    (tmp_path / "docs/bis").mkdir(parents=True)
    (tmp_path / "docs/bis/a.md").write_text("see `sources/bis/ok.pdf`\nand\n`sources/bis/missing.pdf`\n")
    (tmp_path / "README.md").write_text("pattern `sources/*/MANIFEST.md` and prose `sources/...`")
    monkeypatch.setattr(cs, "REPO_ROOT", tmp_path)
    assert cs.main() == 1
    out = capsys.readouterr().out
    assert "docs/bis/a.md:3  ->  sources/bis/missing.pdf" in out
    assert "2 references checked, 1 broken" in out
    (tmp_path / "sources/bis/missing.pdf").write_bytes(b"%PDF")
    assert cs.main() == 0
