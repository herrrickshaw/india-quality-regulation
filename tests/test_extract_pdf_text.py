"""Pure helpers of the PDF extraction pipeline (no pdftotext/tesseract run)."""
from conftest import load

ex = load("extract_pdf_text")
vp = load("verify_pdf_extraction")


def test_build_markdown_pages_and_roundtrip():
    md = ex.build_markdown("sources/bis/act.pdf", "BIS Act", "`pdftotext -layout`", "Page one\f\fPage three  \n\f")
    assert md.startswith("# BIS Act — extracted text\n")
    assert "<!-- page 1 -->\n\nPage one" in md and "<!-- page 3 -->\n\nPage three" in md
    assert "<!-- page 2 -->" not in md                       # blank page skipped, numbering kept
    assert "[`sources/bis/act.pdf`](act.pdf)" in md
    assert ex.HINDI_ENCODING_CAVEAT in md                   # pdftotext path carries the caveat
    assert vp.strip_extraction_markup(md) == "Page one\n\nPage three\n"


def test_build_markdown_ocr_has_no_pdftotext_caveat():
    md = ex.build_markdown("sources/x/scan.pdf", "Scan", "OCR (tesseract)", "text")
    assert ex.HINDI_ENCODING_CAVEAT not in md
