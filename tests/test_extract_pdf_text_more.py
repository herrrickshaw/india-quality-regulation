"""scripts/extract_pdf_text.py with pdftotext/pdfinfo/tesseract/PyMuPDF faked (no PDF is ever parsed)."""

import subprocess
import sys
import types
from pathlib import Path

import pytest

from conftest import load

ex = load("extract_pdf_text")

LONG = "word " * 20  # >= 40 non-whitespace characters


class CP:
    def __init__(self, stdout="", stderr="", returncode=0):
        self.stdout, self.stderr, self.returncode = stdout, stderr, returncode


def cpe(msg="bad", code=1):
    return subprocess.CalledProcessError(code, "cmd", stderr=msg)


def script(monkeypatch, results):
    """Replace ex.run with a scripted sequence of results/exceptions; records commands."""
    calls = []

    def fake(cmd, **kw):
        calls.append((cmd, kw))
        item = results.pop(0)
        if isinstance(item, BaseException):
            raise item
        return item

    monkeypatch.setattr(ex, "run", fake)
    return calls


def fake_pymupdf(monkeypatch, pages=(), png=b"PNG", page_count=None, boom=False):
    mod = types.ModuleType("pymupdf")
    closed = []

    class Pix:
        def tobytes(self, fmt):
            assert fmt == "png"
            return png

    class Page:
        def __init__(self, text):
            self.text = text

        def get_text(self):
            return self.text

        def get_pixmap(self, dpi):
            Page.dpi = dpi
            return Pix()

    class Doc:
        def __init__(self, p):
            if boom:
                raise RuntimeError("corrupt pdf")
            self.pages = [Page(t) for t in pages]
            self.page_count = len(self.pages) if page_count is None else page_count

        def __iter__(self):
            return iter(self.pages)

        def __getitem__(self, i):
            return self.pages[i]

        def close(self):
            closed.append(1)

    mod.open = lambda p: Doc(p)
    mod.Page = Page
    monkeypatch.setitem(sys.modules, "pymupdf", mod)
    return mod, closed


# ---------------------------------- run ----------------------------------


def test_run_passes_check_capture_and_text(monkeypatch):
    seen = {}
    monkeypatch.setattr(
        ex.subprocess, "run", lambda cmd, **kw: seen.update(cmd=cmd, kw=kw) or "R"
    )
    assert ex.run(["x"], timeout=5) == "R"
    assert seen["kw"] == {
        "check": True,
        "capture_output": True,
        "text": True,
        "timeout": 5,
    }


# ---------------------------------- native_text chain ----------------------------------


def test_native_text_layout_success(monkeypatch):
    calls = script(monkeypatch, [CP(LONG)])
    text, method = ex.native_text(Path("a.pdf"))
    assert (text, method) == (LONG, "`pdftotext -layout` (native PDF text layer)")
    assert calls[0][0] == ["pdftotext", "-layout", "a.pdf", "-"]
    assert calls[0][1] == {"timeout": ex.PDFTOTEXT_TIMEOUT_S}


def test_native_text_threshold_is_inclusive(monkeypatch):
    assert ex.NATIVE_TEXT_THRESHOLD == 40
    exact = "x" * 40
    script(monkeypatch, [CP("  " + exact + "  ")])
    assert ex.native_text(Path("a.pdf"))[1].startswith("`pdftotext -layout`")
    script(monkeypatch, [CP("x" * 39), CP(LONG)])
    assert ex.native_text(Path("a.pdf"))[1] == "`pdftotext` (native PDF text layer)"


@pytest.mark.parametrize(
    "first,msg",
    [
        (CP("tiny"), "exited 0 but returned near-empty text"),
        (subprocess.TimeoutExpired("c", 1), "timed out after 120s"),
        (cpe("poppler broke", 3), "failed on a.pdf (exit 3)"),
    ],
)
def test_native_text_falls_back_to_plain_pdftotext(monkeypatch, capsys, first, msg):
    calls = script(monkeypatch, [first, CP(LONG)])
    text, method = ex.native_text(Path("a.pdf"))
    assert method == "`pdftotext` (native PDF text layer)" and text == LONG
    assert calls[1][0] == ["pdftotext", "a.pdf", "-"]
    assert msg in capsys.readouterr().err


@pytest.mark.parametrize(
    "second,msg",
    [
        (CP(""), "exited 0 but returned near-empty text"),
        (subprocess.TimeoutExpired("c", 1), "also timed out after 120s"),
        (cpe("again", 2), "also failed on a.pdf (exit 2)"),
    ],
)
def test_native_text_falls_back_to_pymupdf(monkeypatch, capsys, second, msg):
    script(monkeypatch, [cpe(), second])
    fake_pymupdf(monkeypatch, pages=[LONG, LONG])
    text, method = ex.native_text(Path("a.pdf"))
    assert text == LONG + "\f" + LONG and method.startswith("PyMuPDF `page.get_text()`")
    assert msg in capsys.readouterr().err


def test_native_text_all_three_fail_returns_empty(monkeypatch, capsys):
    script(monkeypatch, [CP(""), CP("")])
    fake_pymupdf(monkeypatch, pages=["short"])
    assert ex.native_text(Path("a.pdf")) == ("", "")
    assert "PyMuPDF's own extractor on a.pdf also returned near-empty text" in capsys.readouterr().err
    script(monkeypatch, [CP(""), CP("")])
    fake_pymupdf(monkeypatch, boom=True)
    assert ex.native_text(Path("a.pdf")) == ("", "")
    assert "also failed on a.pdf: corrupt pdf" in capsys.readouterr().err


def test_pymupdf_native_text_joins_pages_and_closes(monkeypatch):
    _, closed = fake_pymupdf(monkeypatch, pages=["a", "b", "c"])
    assert ex.pymupdf_native_text(Path("x.pdf")) == "a\fb\fc" and closed == [1]


# ---------------------------------- pdf_page_count / ocr ----------------------------------


def test_pdf_page_count(monkeypatch):
    calls = script(monkeypatch, [CP("Title: x\nPages:          14\nSize: 1")])
    assert ex.pdf_page_count(Path("a.pdf")) == 14 and calls[0][0] == ["pdfinfo", "a.pdf"] and calls[0][1] == {"timeout": 30}
    script(monkeypatch, [CP("no pages line")])
    with pytest.raises(RuntimeError, match="pdfinfo gave no page count for a.pdf"):
        ex.pdf_page_count(Path("a.pdf"))


def test_ocr_pdf_runs_tesseract_per_page_and_handles_timeouts(monkeypatch, capsys):
    mod, closed = fake_pymupdf(monkeypatch, pages=["", "", ""], png=b"IMG")
    seen = []
    outs = [types.SimpleNamespace(stdout="हिंदी one\n".encode()), subprocess.TimeoutExpired("t", 90), types.SimpleNamespace(stdout=b"bad \xff byte")]

    def fake_run(cmd, **kw):
        seen.append((cmd, kw))
        item = outs.pop(0)
        if isinstance(item, BaseException):
            raise item
        return item

    monkeypatch.setattr(ex.subprocess, "run", fake_run)
    text = ex.ocr_pdf(Path("scan.pdf"))
    assert text == "हिंदी one\n\f\fbad � byte" and closed == [1] and mod.Page.dpi == ex.OCR_DPI == 300
    cmd, kw = seen[0]
    assert cmd == ["tesseract", "stdin", "stdout", "-l", "eng+hin"]
    assert kw == {"input": b"IMG", "capture_output": True, "check": True, "timeout": ex.TESSERACT_TIMEOUT_S}
    assert "tesseract timed out after 90s on scan.pdf page 2" in capsys.readouterr().err


# ---------------------------------- find_doc_title ----------------------------------


@pytest.fixture()
def tree(monkeypatch, tmp_path):
    monkeypatch.setattr(ex, "REPO_ROOT", tmp_path)
    monkeypatch.setattr(ex, "SOURCES", tmp_path / "sources")
    monkeypatch.setattr(ex, "DOCS", tmp_path / "docs")
    (tmp_path / "sources" / "cat").mkdir(parents=True)
    (tmp_path / "docs" / "cat").mkdir(parents=True)
    return tmp_path


def test_find_doc_title_same_name_then_citation_then_slug(tree):
    d = tree / "docs" / "cat"
    (d / "act.md").write_text("intro\n# The Act\nmore", encoding="utf-8")
    assert ex.find_doc_title("cat", "act") == "The Act"
    (d / "act.md").write_text("no heading here", encoding="utf-8")           # same-name doc without an H1: fall through
    (d / "other.md").write_text("# Other Doc\n- mirrored at `sources/cat/act.pdf`\n", encoding="utf-8")
    assert ex.find_doc_title("cat", "act") == "Other Doc"
    (d / "aaa.md").write_text("# Mentions only\nsources/cat/act.pdf is discussed\n", encoding="utf-8")
    assert ex.find_doc_title("cat", "act") == "Other Doc"                    # bare substring is not a citation
    assert ex.find_doc_title("cat", "unknown-thing") == "Unknown Thing"
    assert ex.find_doc_title("nocat", "my-slug") == "My Slug"
    (d / "citer.md").write_text("mirrored at `sources/cat/zzz.pdf` but no heading", encoding="utf-8")
    assert ex.find_doc_title("cat", "zzz") == "Zzz"


# ---------------------------------- process_pdf ----------------------------------


def make_pdf(tree, name="act.pdf", cat="cat"):
    p = tree / "sources" / cat / name
    p.write_bytes(b"%PDF")
    return p


def test_process_pdf_native(tree, monkeypatch):
    pdf = make_pdf(tree)
    (tree / "docs" / "cat" / "act.md").write_text("# Act Title\n", encoding="utf-8")
    monkeypatch.setattr(ex, "native_text", lambda p: (LONG, "`pdftotext -layout` (native PDF text layer)"))
    monkeypatch.setattr(ex, "pdf_page_count", lambda p: pytest.fail("no page count needed"))
    method, n = ex.process_pdf(pdf)
    out = pdf.with_suffix(".md").read_text(encoding="utf-8")
    assert method.startswith("`pdftotext -layout`") and n == len(out)
    assert out.startswith("# Act Title — extracted text\n") and "sources/cat/act.pdf" in out and "<!-- page 1 -->" in out


def test_process_pdf_forced_pymupdf(tree, monkeypatch):
    pdf = make_pdf(tree, "forced.pdf")
    monkeypatch.setattr(ex, "FORCE_PYMUPDF", {"sources/cat/forced.pdf"})
    monkeypatch.setattr(ex, "pymupdf_native_text", lambda p: LONG)
    monkeypatch.setattr(ex, "native_text", lambda p: pytest.fail("forced file skips the pdftotext chain"))
    method, _ = ex.process_pdf(pdf)
    assert method.startswith("PyMuPDF `page.get_text()`") and "forced" in method


def test_process_pdf_ocr_path_and_page_cap(tree, monkeypatch):
    pdf = make_pdf(tree, "scan.pdf")
    monkeypatch.setattr(ex, "native_text", lambda p: ("", ""))
    monkeypatch.setattr(ex, "pdf_page_count", lambda p: ex.OCR_MAX_PAGES)               # at the cap: OCR is allowed
    monkeypatch.setattr(ex, "ocr_pdf", lambda p: "scanned text " * 5)
    method, _ = ex.process_pdf(pdf)
    assert method.startswith("OCR (`tesseract`, 300 DPI") and "no native text layer found" in method
    assert "scanned text" in pdf.with_suffix(".md").read_text(encoding="utf-8")
    monkeypatch.setattr(ex, "pdf_page_count", lambda p: ex.OCR_MAX_PAGES + 1)
    with pytest.raises(RuntimeError, match=r"sources/cat/scan.pdf: native-text extraction came back empty, but this PDF has 41 pages"):
        ex.process_pdf(pdf)


# ---------------------------------- link_extraction_from_docs ----------------------------------


def test_link_extraction_inserts_bullet_once(tree):
    d = tree / "docs" / "cat"
    (d / "a.md").write_text("# A\n- [Act (PDF)](x) mirrored at `sources/cat/act.pdf`\n  - [Other](y) `sources/cat/act.pdf`\nplain `sources/cat/act.pdf` prose\n", encoding="utf-8")
    (d / "b.md").write_text("# B\nno citation\n", encoding="utf-8")
    sub = tree / "docs" / "cat" / "nested"
    sub.mkdir()
    (sub / "c.md").write_text("- [Link](z) `sources/cat/act.pdf`", encoding="utf-8")
    n = ex.link_extraction_from_docs("sources/cat/act.pdf", "sources/cat/act.md")
    assert n == 2
    a = (d / "a.md").read_text(encoding="utf-8").split("\n")
    assert a[2] == "- Full text: [`sources/cat/act.md`](../../sources/cat/act.md) (extracted, for search/offline reading)"
    assert a[4].startswith("  - Full text: [")                                  # indentation of the cited bullet is kept
    assert "Full text" not in a[6]                                              # a non-bullet mention gets no link
    assert (d / "b.md").read_text(encoding="utf-8") == "# B\nno citation\n"
    assert "(../../../sources/cat/act.md)" in (sub / "c.md").read_text(encoding="utf-8")
    assert ex.link_extraction_from_docs("sources/cat/act.pdf", "sources/cat/act.md") == 0      # idempotent


# ---------------------------------- main ----------------------------------


def test_main_no_pdfs_returns_1(tree, capsys):
    assert ex.main() == 1 and "No PDFs found under sources/." in capsys.readouterr().err


def test_main_processes_every_pdf_and_reports(tree, monkeypatch, capsys):
    make_pdf(tree, "b.pdf")
    make_pdf(tree, "a.pdf")
    seen = []
    monkeypatch.setattr(ex, "process_pdf", lambda p: seen.append(p.name) or ("method-x", 1234))
    monkeypatch.setattr(ex, "link_extraction_from_docs", lambda pdf, md: 2)
    assert ex.main() == 0
    out = capsys.readouterr().out
    assert seen == ["a.pdf", "b.pdf"]
    assert "sources/cat/a.pdf -> sources/cat/a.md (1,234 chars, method-x)" in out
    assert "Extracted 2 PDFs in " in out and "linked from 4 doc page(s)." in out


def test_process_pdf_threshold_is_inclusive_at_40_chars(tree, monkeypatch):
    pdf = make_pdf(tree, "edge.pdf")
    monkeypatch.setattr(ex, "native_text", lambda p: ("y" * 40, "native-method"))
    monkeypatch.setattr(ex, "pdf_page_count", lambda p: pytest.fail("40 chars is enough: no OCR"))
    assert ex.process_pdf(pdf)[0] == "native-method"
    monkeypatch.setattr(ex, "native_text", lambda p: ("y" * 39, "native-method"))
    monkeypatch.setattr(ex, "pdf_page_count", lambda p: 3)
    monkeypatch.setattr(ex, "ocr_pdf", lambda p: "ocr text here")
    assert ex.process_pdf(pdf)[0].startswith("OCR (`tesseract`")


def test_build_markdown_separates_pages_with_rules():
    md = ex.build_markdown("sources/c/a.pdf", "T", "m", "one\ftwo\fthree")
    assert md.endswith("<!-- page 1 -->\n\none\n\n---\n\n<!-- page 2 -->\n\ntwo\n\n---\n\n<!-- page 3 -->\n\nthree\n")
