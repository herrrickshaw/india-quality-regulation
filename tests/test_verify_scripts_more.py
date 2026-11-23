"""verify_pdf_extraction.py and verify_compendium.py against small synthetic repo trees (tmp_path)."""

import sys

import pytest

from conftest import load

vp = load("verify_pdf_extraction")
vc = load("verify_compendium")


def fails(capsys, fn, *args):
    with pytest.raises(SystemExit) as e:
        fn(*args)
    assert e.value.code == 1
    return capsys.readouterr().err


# ---------------------------------- verify_pdf_extraction ----------------------------------


@pytest.fixture()
def pdf_tree(monkeypatch, tmp_path):
    for mod in (vp,):
        monkeypatch.setattr(mod, "REPO_ROOT", tmp_path)
        monkeypatch.setattr(mod, "SOURCES", tmp_path / "sources")
        monkeypatch.setattr(mod, "DOCS", tmp_path / "docs")
    (tmp_path / "sources" / "cat").mkdir(parents=True)
    (tmp_path / "docs" / "cat").mkdir(parents=True)
    return tmp_path


def add_pdf(root, name="a.pdf", md_text=None, cat="cat"):
    p = root / "sources" / cat / name
    p.write_bytes(b"%PDF")
    if md_text is not None:
        p.with_suffix(".md").write_text(md_text, encoding="utf-8")
    return p


def md_for(body, method="`pdftotext -layout`"):
    return f"# T — extracted text\n\n*via {method}.*\n\n---\n\n<!-- page 1 -->\n\n{body}\n"


def test_all_pdfs_sorted(pdf_tree):
    add_pdf(pdf_tree, "b.pdf")
    add_pdf(pdf_tree, "a.pdf")
    assert [p.name for p in vp.all_pdfs()] == ["a.pdf", "b.pdf"]


def test_coverage_check_variants(pdf_tree, capsys):
    assert "no PDFs found under sources/" in fails(capsys, vp.check_coverage)
    add_pdf(pdf_tree, "ok.pdf", "x" * vp.MIN_EXTRACTION_BYTES)
    add_pdf(pdf_tree, "none.pdf")
    add_pdf(pdf_tree, "tiny.pdf", "x" * (vp.MIN_EXTRACTION_BYTES - 1))
    err = fails(capsys, vp.check_coverage)
    assert "sources/cat/none.pdf: no companion .md extraction file" in err
    assert f"sources/cat/tiny.md: only {vp.MIN_EXTRACTION_BYTES - 1} bytes" in err and "ok" not in err.replace("looks", "")
    (pdf_tree / "sources" / "cat" / "none.md").write_text("x" * vp.MIN_EXTRACTION_BYTES)
    (pdf_tree / "sources" / "cat" / "tiny.md").write_text("x" * vp.MIN_EXTRACTION_BYTES)
    vp.check_coverage()
    assert capsys.readouterr().out == "EXTRACTION_COVERAGE_OK (3 PDFs, all have a non-trivial .md extraction)\n"


def test_strip_extraction_markup():
    text = md_for("Body one") + "\n---\n\n<!-- page 2 -->\n\nBody two\n"
    assert vp.strip_extraction_markup(text) == "Body one\n\nBody two\n"
    assert vp.strip_extraction_markup("no header at all") == "no header at all"


def test_ocr_content_check(pdf_tree, monkeypatch, capsys):
    assert "expected OCR-path fixture" in fails(capsys, vp.check_ocr_content)
    (pdf_tree / "sources" / "bis-core").mkdir(exist_ok=True)
    target = add_pdf(pdf_tree, "bis-crs.pdf", cat="bis-core")
    monkeypatch.setattr(vp.extractor, "native_text", lambda p: ("x" * 40, "m"))
    assert "unexpectedly has native text" in fails(capsys, vp.check_ocr_content)
    monkeypatch.setattr(vp.extractor, "native_text", lambda p: ("x" * 39, ""))
    assert "bis-crs.md does not exist" in fails(capsys, vp.check_ocr_content)
    target.with_suffix(".md").write_text("# X\n\nOCR output\n" + "z" * 100, encoding="utf-8")
    err = fails(capsys, vp.check_ocr_content)
    assert "missing 'no native text layer found'" in err and "too short for a real 14-page OCR pass" in err
    assert "'Compulsory Registration' not found" in err
    good = "no native text layer found\n" + "compulsory registration " * 300
    target.with_suffix(".md").write_text(good, encoding="utf-8")
    vp.check_ocr_content()
    assert capsys.readouterr().out.startswith("EXTRACTION_OCR_OK")
    short = "no native text layer found\n" + "Compulsory Registration " * 100
    target.with_suffix(".md").write_text(short, encoding="utf-8")                      # on-topic but under 5000 chars
    err = fails(capsys, vp.check_ocr_content)
    assert "too short" in err and "missing 'no native text layer found'" not in err and "not found anywhere" not in err


def test_completeness_check(pdf_tree, monkeypatch, capsys):
    fresh = "a" * 1000
    monkeypatch.setattr(vp.extractor, "native_text", lambda p: (fresh, "m"))
    add_pdf(pdf_tree, "nomd.pdf")                                                   # skipped: coverage's job
    add_pdf(pdf_tree, "ocr.pdf", md_for("x") .replace("`pdftotext -layout`", "no native text layer found"))
    add_pdf(pdf_tree, "good.pdf", md_for("a" * 1000))
    add_pdf(pdf_tree, "edge.pdf", md_for("a" * 1030))                                  # exactly 3% drift is allowed
    vp.check_completeness()
    assert capsys.readouterr().out == "EXTRACTION_COMPLETENESS_OK (2 native-text PDFs, all within 3% of a fresh direct extraction)\n"
    add_pdf(pdf_tree, "short.pdf", md_for("a" * 900))
    add_pdf(pdf_tree, "long.pdf", md_for("a" * 1100))
    err = fails(capsys, vp.check_completeness)
    assert "short.md: 10.0% drift" in err and "long.md: 10.0% drift" in err and "good.md" not in err and "edge.md" not in err


def test_completeness_forced_pymupdf_and_empty_fresh(pdf_tree, monkeypatch, capsys):
    add_pdf(pdf_tree, "forced.pdf", md_for("b" * 500))
    monkeypatch.setattr(vp.extractor, "FORCE_PYMUPDF", {"sources/cat/forced.pdf"})
    monkeypatch.setattr(vp.extractor, "pymupdf_native_text", lambda p: "b" * 500)
    monkeypatch.setattr(vp.extractor, "native_text", lambda p: pytest.fail("forced file must use PyMuPDF"))
    vp.check_completeness()
    assert "1 native-text PDFs" in capsys.readouterr().out
    monkeypatch.setattr(vp.extractor, "pymupdf_native_text", lambda p: "  \n ")
    vp.check_completeness()                                                          # zero-length fresh text: skipped, no ZeroDivisionError
    assert "0 native-text PDFs" in capsys.readouterr().out


def test_doc_links_check(pdf_tree, capsys):
    add_pdf(pdf_tree, "a.pdf")
    add_pdf(pdf_tree, "b.pdf")
    docs = pdf_tree / "docs" / "cat"
    (docs / "one.md").write_text("cites `sources/cat/a.pdf` and `sources/cat/a.md`", encoding="utf-8")
    (docs / "two.md").write_text("cites `sources/cat/a.pdf` only", encoding="utf-8")
    err = fails(capsys, vp.check_doc_links)
    assert "sources/cat/b.pdf: no doc page cites this PDF at all" in err
    assert "docs/cat/two.md: cites sources/cat/a.pdf but doesn't link its extraction sources/cat/a.md" in err and "one.md" not in err
    (docs / "two.md").write_text("`sources/cat/a.pdf` `sources/cat/a.md` `sources/cat/b.pdf` `sources/cat/b.md`", encoding="utf-8")
    (docs / "one.md").write_text("`sources/cat/a.pdf` `sources/cat/a.md`", encoding="utf-8")
    vp.check_doc_links()
    assert capsys.readouterr().out == "EXTRACTION_DOC_LINKS_OK (2 PDFs, every citing doc page links the extraction)\n"


def test_verify_pdf_main_dispatch(pdf_tree, monkeypatch, capsys):
    called = []
    monkeypatch.setattr(vp, "CHECKS", {"x": lambda: called.append("x"), "y": lambda: called.append("y")})
    monkeypatch.setattr(sys, "argv", ["v", "--check", "y"])
    vp.main()
    monkeypatch.setattr(sys, "argv", ["v", "--check", "all"])
    monkeypatch.setattr(vp, "CHECKS", {"x": lambda: called.append("x"), "y": lambda: called.append("y")})
    vp.main()
    assert called == ["y", "x", "y"]
    monkeypatch.setattr(sys, "argv", ["v"])
    with pytest.raises(SystemExit) as e:
        vp.main()
    assert e.value.code == 2


# ---------------------------------- verify_compendium ----------------------------------

FIELDS = {"Authority": "BIS", "Status": "Statutory", "Established": "1986", "Legal basis": "BIS Act", "Marks issued": "ISI", "Source tier": "Statutory text"}


def entry_doc(title, scope="This scope paragraph is long enough to compare.", notes=None, src_url="https://x.gov.in/a", tier="Statutory text"):
    f = {**FIELDS, "Source tier": tier}
    lines = [f"# {title}", ""] + [f"**{k}:** {v}" for k, v in f.items()] + ["", "## Scope", scope, ""]
    if notes:
        lines += ["## Notes", notes, ""]
    lines += ["## Primary source", f"- [Official Act]({src_url})", "", "## Other", "x"]
    return "\n".join(lines)


def comp_entry(title, scope="This scope paragraph is long enough to compare.", notes=None, src_url="https://x.gov.in/a", tier="Statutory text", extra=""):
    f = {**FIELDS, "Source tier": tier}
    lines = [f"### {title}", ""] + [f"**{k}:** {v}" for k, v in f.items()] + ["", scope, ""]
    if notes:
        lines += [notes, ""]
    lines += [f"- [Official Act]({src_url})", extra, ""]
    return "\n".join(lines)


def comp(entries, summary="**2 entries. 1 have the actual statutory or regulatory text, 1 are administrative/scheme pages"):
    return (
        "# Compendium\n\n" + summary + "\n\n## Apex & Accreditation Infrastructure\n\n" + "\n".join(entries)
        + "\n## Referenced Technical Standards\n\n### Not an entry\n"
    )


@pytest.fixture()
def cmp_tree(monkeypatch, tmp_path):
    monkeypatch.setattr(vc, "REPO_ROOT", tmp_path)
    monkeypatch.setattr(vc, "DOCS", tmp_path / "docs")
    monkeypatch.setattr(vc, "COMPENDIUM", tmp_path / "COMPENDIUM.md")
    (tmp_path / "docs" / "cat").mkdir(parents=True)
    (tmp_path / "docs" / "empty").mkdir()
    (tmp_path / "docs" / "loose.md").write_text("# not an entry (top-level file)")
    return tmp_path


def write_docs(root, **docs):
    for name, text in docs.items():
        (root / "docs" / "cat" / f"{name}.md").write_text(text, encoding="utf-8")


def test_slugify_and_normalize_and_strip_links():
    assert vc.slugify("  BIS — ISI Mark  ") == "bis--isi-mark" and vc.slugify("A (B) & C!") == "a-b--c"
    assert vc.normalize("  a \n\t b   c ") == "a b c"
    assert vc.strip_links("see [label](http://x) and [b](#y)") == "see label and b" and vc.strip_links("[a]") == "[a]"


def test_entry_docs_only_category_directories(cmp_tree):
    write_docs(cmp_tree, b=entry_doc("B"), a=entry_doc("A"))
    assert [p.name for p in vc.entry_docs()] == ["a.md", "b.md"]


def test_load_compendium_missing(cmp_tree, capsys):
    assert "COMPENDIUM.md does not exist" in fails(capsys, vc.load_compendium)


def test_region_and_entry_slice():
    text = comp([comp_entry("A"), comp_entry("B")])
    region = vc.main_entries_region(text)
    assert "### A" in region and "### Not an entry" not in region and region.startswith("\n## Apex")
    a = vc.entry_slice(region, "A")
    assert "**Authority:** BIS" in a and "### B" not in a
    assert vc.entry_slice(region, "B").rstrip().endswith("")
    with pytest.raises(ValueError):
        vc.entry_slice(region, "Zzz")
    with pytest.raises(ValueError):
        vc.main_entries_region("no markers")


def test_headings_check(cmp_tree, capsys):
    write_docs(cmp_tree, a=entry_doc("A"), b=entry_doc("B"))
    (cmp_tree / "COMPENDIUM.md").write_text(comp([comp_entry("A"), comp_entry("B")]), encoding="utf-8")
    vc.check_headings()
    assert capsys.readouterr().out == "COMPENDIUM_HEADINGS_OK (2 entries, exact match)\n"
    (cmp_tree / "COMPENDIUM.md").write_text(comp([comp_entry("A"), comp_entry("A"), comp_entry("Extra")]), encoding="utf-8")
    err = fails(capsys, vc.check_headings)
    assert "expected 2 H3 entry headings, found 3" in err and "missing headings for: ['B']" in err
    assert "unexpected headings not in any source doc: ['Extra']" in err and "duplicate H3 headings: {'A': 2}" in err


def test_fields_check(cmp_tree, capsys):
    write_docs(cmp_tree, a=entry_doc("A"), b=entry_doc("B"))
    (cmp_tree / "COMPENDIUM.md").write_text(comp([comp_entry("A"), comp_entry("B")]), encoding="utf-8")
    vc.check_fields()
    assert capsys.readouterr().out == "COMPENDIUM_FIELDS_OK (2 entries × 6 fields, all present verbatim)\n"
    broken = comp_entry("B").replace("**Authority:** BIS", "**Authority:** Someone else")
    (cmp_tree / "COMPENDIUM.md").write_text(comp([comp_entry("A"), broken]), encoding="utf-8")
    err = fails(capsys, vc.check_fields)
    assert "B: field 'Authority' not found verbatim (link-stripped) in its own compendium section" in err and "A:" not in err
    (cmp_tree / "COMPENDIUM.md").write_text(comp([comp_entry("A")]), encoding="utf-8")
    assert "B: entry heading not found in compendium at all" in fails(capsys, vc.check_fields)
    write_docs(cmp_tree, a=entry_doc("A").replace("**Status:** Statutory\n", ""))
    (cmp_tree / "COMPENDIUM.md").write_text(comp([comp_entry("A"), comp_entry("B")]), encoding="utf-8")
    assert "a.md: source doc itself missing field 'Status'" in fails(capsys, vc.check_fields)


def test_fields_are_scoped_to_their_own_entry(cmp_tree, capsys):
    write_docs(cmp_tree, a=entry_doc("A"), b=entry_doc("B"))
    a_missing = comp_entry("A").replace("**Established:** 1986", "")
    (cmp_tree / "COMPENDIUM.md").write_text(comp([a_missing, comp_entry("B")]), encoding="utf-8")
    err = fails(capsys, vc.check_fields)                                   # B still has the value, but A's section does not
    assert "A: field 'Established'" in err


def test_sections_check(cmp_tree, capsys):
    scope = "This scope paragraph is long enough to compare."
    write_docs(cmp_tree, a=entry_doc("A", scope=scope, notes="Notes paragraph that is also long enough."), b=entry_doc("B", scope="Short"))
    good = comp([comp_entry("A", scope=scope, notes="Notes paragraph that is also long enough."), comp_entry("B", scope="Short")])
    (cmp_tree / "COMPENDIUM.md").write_text(good, encoding="utf-8")
    vc.check_sections()
    assert capsys.readouterr().out == "COMPENDIUM_SECTIONS_OK (2 entries, Scope/Notes/Primary-source content all present)\n"
    bad = comp([comp_entry("A", scope="Different words entirely here.", notes="Notes paragraph that is also long enough.", src_url="https://other.example/zzz"),
                comp_entry("B", scope="Short")])
    (cmp_tree / "COMPENDIUM.md").write_text(bad, encoding="utf-8")
    err = fails(capsys, vc.check_sections)
    assert "A / Scope: chunk not found in its own compendium section" in err and "Notes" not in err.split("A / Scope")[0]
    assert "A / Primary source: URL missing from its own section: https://x.gov.in/a" in err
    (cmp_tree / "COMPENDIUM.md").write_text(comp([comp_entry("A", scope=scope, notes="Notes paragraph that is also long enough.")]), encoding="utf-8")
    assert "B: entry heading not found in compendium at all" in fails(capsys, vc.check_sections)


def test_sections_ignore_link_targets_and_wrapping_and_short_chunks(cmp_tree, capsys):
    write_docs(cmp_tree, a=entry_doc("A", scope="See [the rules](../x.md) for details\nover two lines here."))
    (cmp_tree / "COMPENDIUM.md").write_text(
        comp([comp_entry("A", scope="See [the rules](#anchor) for details over two lines here.")]), encoding="utf-8")
    vc.check_sections()
    assert "COMPENDIUM_SECTIONS_OK (1 entries" in capsys.readouterr().out


def test_anchor_check(cmp_tree, capsys):
    (cmp_tree / "COMPENDIUM.md").write_text("# T\n\n## BIS — ISI Mark\n\nsee [x](#bis--isi-mark) and [y](#t)\n", encoding="utf-8")
    vc.check_anchors()
    assert capsys.readouterr().out == "COMPENDIUM_ANCHORS_OK (2 internal links, all resolve to a real heading)\n"
    (cmp_tree / "COMPENDIUM.md").write_text("# T\n[x](#gone) [z](#t)\n", encoding="utf-8")
    assert "dead anchor #gone (link text: 'x')" in fails(capsys, vc.check_anchors)
    (cmp_tree / "COMPENDIUM.md").write_text("# T\nno links\n", encoding="utf-8")
    assert "no internal anchor links found at all" in fails(capsys, vc.check_anchors)


def test_coverage_counts_check(cmp_tree, capsys):
    write_docs(cmp_tree, a=entry_doc("A", tier="Statutory text"), b=entry_doc("B", tier="Official page"), c=entry_doc("C", tier="Statutory regulation"))
    ok = "**3 entries. 2 have the actual statutory or regulatory text, and\nthe rest; 1 are administrative/scheme pages"
    (cmp_tree / "COMPENDIUM.md").write_text(f"x {ok} y", encoding="utf-8")
    vc.check_coverage_counts()
    assert capsys.readouterr().out == "COMPENDIUM_COVERAGE_COUNTS_OK (total=3, statutory=2, official=1)\n"
    (cmp_tree / "COMPENDIUM.md").write_text("**4 entries. 1 have the actual statutory or regulatory text. 1 are administrative/scheme pages", encoding="utf-8")
    err = fails(capsys, vc.check_coverage_counts)
    assert "total: embedded=4 live=3" in err and "statutory: embedded=1 live=2" in err and "official: embedded=1 live=1" not in err
    (cmp_tree / "COMPENDIUM.md").write_text("no summary", encoding="utf-8")
    assert "coverage summary sentence not found" in fails(capsys, vc.check_coverage_counts)
    write_docs(cmp_tree, d="# D\nno tier here")
    (cmp_tree / "COMPENDIUM.md").write_text(ok, encoding="utf-8")
    assert "d.md: missing Source tier field" in fails(capsys, vc.check_coverage_counts)


def test_verify_compendium_main(cmp_tree, monkeypatch):
    called = []
    monkeypatch.setattr(vc, "CHECKS", {"a": lambda: called.append("a"), "b": lambda: called.append("b")})
    monkeypatch.setattr(sys, "argv", ["v", "--check", "b"])
    vc.main()
    monkeypatch.setattr(sys, "argv", ["v", "--check", "all"])
    vc.main()
    assert called == ["b", "a", "b"]
    monkeypatch.setattr(sys, "argv", ["v", "--check", "nope"])
    with pytest.raises(SystemExit) as e:
        vc.main()
    assert e.value.code == 2
