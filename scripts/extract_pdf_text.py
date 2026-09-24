#!/usr/bin/env python3
"""Extract the full text of every mirrored PDF under sources/ into a
companion .md file next to it (sources/<cat>/<slug>.pdf -> <slug>.md).

Native-text PDFs (the vast majority) go through `pdftotext -layout`, which
keeps enough of the original column/table alignment to stay readable for a
gazette notification. A PDF with no extractable text layer (a pure scan)
is rendered page-by-page to an image via PyMuPDF and OCR'd with tesseract
instead — detected automatically by running pdftotext first and checking
whether it returned anything.

Deterministic and re-runnable: run this again after re-fetching a PDF
(the OCR path is the only part with any inherent variance across
tesseract versions; everything else is byte-for-byte reproducible from the
same input PDF).
"""
import os
import re
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
SOURCES = REPO_ROOT / "sources"
DOCS = REPO_ROOT / "docs"

OCR_DPI = 300
NATIVE_TEXT_THRESHOLD = 40  # non-whitespace chars; below this, treat as scan-only


PDFTOTEXT_TIMEOUT_S = 120  # generous for even the largest (635-page) PDF here
TESSERACT_TIMEOUT_S = 90   # per page — generous for a single 300-DPI page image


def run(cmd, **kw):
    return subprocess.run(cmd, check=True, capture_output=True, text=True, **kw)


def native_text(pdf_path: Path) -> str:
    """Try `pdftotext -layout` first (keeps column/table alignment); if the
    installed poppler version chokes on this specific PDF's structure —
    seen in practice on Ubuntu's older poppler-utils against a Word-
    exported PDF that a newer Homebrew poppler parses fine — fall back to
    plain `pdftotext` (no -layout), which is a simpler code path and more
    tolerant of exactly this kind of quirk. Returns "" (never raises on a
    subprocess failure OR a hang — both are treated as "needs OCR" rather
    than left to block the whole run indefinitely; a real hang here is
    exactly what left the first CI attempts stuck for 15+ minutes)."""
    try:
        return run(["pdftotext", "-layout", str(pdf_path), "-"], timeout=PDFTOTEXT_TIMEOUT_S).stdout
    except subprocess.TimeoutExpired:
        print(f"WARNING: 'pdftotext -layout' timed out after {PDFTOTEXT_TIMEOUT_S}s on "
              f"{pdf_path.name}; retrying without -layout", file=sys.stderr)
    except subprocess.CalledProcessError as e:
        print(f"WARNING: 'pdftotext -layout' failed on {pdf_path.name} "
              f"(exit {e.returncode}); retrying without -layout: "
              f"{e.stderr.strip()[:300]}", file=sys.stderr)
    try:
        return run(["pdftotext", str(pdf_path), "-"], timeout=PDFTOTEXT_TIMEOUT_S).stdout
    except subprocess.TimeoutExpired:
        print(f"WARNING: plain 'pdftotext' also timed out after {PDFTOTEXT_TIMEOUT_S}s on "
              f"{pdf_path.name}", file=sys.stderr)
        return ""
    except subprocess.CalledProcessError as e:
        print(f"WARNING: plain 'pdftotext' also failed on {pdf_path.name} "
              f"(exit {e.returncode}): {e.stderr.strip()[:300]}", file=sys.stderr)
        return ""


def ocr_pdf(pdf_path: Path) -> str:
    import pymupdf  # imported lazily: only needed on the OCR path

    doc = pymupdf.open(pdf_path)
    pages_text = []
    for page_index in range(doc.page_count):
        page = doc[page_index]
        pix = page.get_pixmap(dpi=OCR_DPI)
        png_bytes = pix.tobytes("png")
        # Gazette notifications in this repo are routinely bilingual
        # (Hindi text precedes the English text on the same scanned page),
        # so English-only OCR mangles half the page. eng+hin lets
        # tesseract recognize both scripts on the same pass.
        try:
            result = subprocess.run(
                ["tesseract", "stdin", "stdout", "-l", "eng+hin"],
                input=png_bytes,
                capture_output=True,
                check=True,
                timeout=TESSERACT_TIMEOUT_S,
            )
        except subprocess.TimeoutExpired:
            print(f"WARNING: tesseract timed out after {TESSERACT_TIMEOUT_S}s on "
                  f"{pdf_path.name} page {page_index + 1} — leaving that page blank "
                  f"rather than hanging the whole run", file=sys.stderr)
            pages_text.append("")
            continue
        pages_text.append(result.stdout.decode("utf-8", errors="replace"))
    doc.close()
    return "\f".join(pages_text)  # \f (form feed) matches pdftotext's own page separator


def find_doc_title(cat_key: str, slug: str) -> str:
    """Best-effort: find the docs/<cat>/<slug>.md whose Primary source cites
    this exact PDF, and return its H1 title, for a friendly header. Falls
    back to a slug-derived title if no doc references this PDF."""
    cat_dir = DOCS / cat_key
    if cat_dir.is_dir():
        for md in cat_dir.glob("*.md"):
            text = md.read_text(encoding="utf-8")
            if f"sources/{cat_key}/{slug}.pdf" in text:
                m = re.search(r"^# (.+)$", text, re.M)
                if m:
                    return m.group(1)
    return slug.replace("-", " ").title()


HINDI_ENCODING_CAVEAT = (
    " Several of these gazette PDFs embed their Hindi text in a legacy, "
    "pre-Unicode font (common in Indian government PDFs of this era, e.g. "
    "Krutidev/Chanakya-style encodings) where the underlying character "
    "codes don't map to actual Devanagari — `pdftotext` extracts those "
    "runs as ASCII-range gibberish while the English text alongside it "
    "extracts cleanly and correctly. This is a property of the source "
    "PDF's font encoding, not an extraction error; the operative English "
    "legal text is intact."
)


def build_markdown(pdf_relpath: str, title: str, method: str, raw_text: str) -> str:
    pages = raw_text.split("\f")
    # Drop a trailing empty "page" produced by a final form-feed.
    while pages and not pages[-1].strip():
        pages.pop()

    body_parts = []
    for i, page_text in enumerate(pages, start=1):
        cleaned = page_text.rstrip()
        if not cleaned.strip():
            continue
        body_parts.append(f"<!-- page {i} -->\n\n{cleaned}")
    body = "\n\n---\n\n".join(body_parts)

    caveat = HINDI_ENCODING_CAVEAT if method.startswith("`pdftotext") else ""
    header = (
        f"# {title} — extracted text\n\n"
        f"*Raw text extracted from [`{pdf_relpath}`]({Path(pdf_relpath).name}) via {method}. "
        f"This is a mechanical transcription of the mirrored PDF for full-text search and "
        f"offline reading — formatting (tables, multi-column layout, page numbers, diacritics "
        f"in scanned text) may not be perfectly preserved, and OCR output in particular can "
        f"contain recognition errors.{caveat} For the authoritative document, use the PDF "
        f"itself or the original URL cited in the entry's doc page and this category's "
        f"`MANIFEST.md`. Generated by `scripts/extract_pdf_text.py` on "
        f"{datetime.now(timezone.utc).strftime('%Y-%m-%d')}.*\n\n"
        f"---\n\n"
    )
    return header + body + "\n"


def process_pdf(pdf_path: Path) -> tuple[str, int]:
    """Returns (method_used, output_char_count)."""
    cat_key = pdf_path.parent.name
    slug = pdf_path.stem
    pdf_relpath = pdf_path.relative_to(REPO_ROOT).as_posix()

    extracted = native_text(pdf_path)
    if len(extracted.strip()) >= NATIVE_TEXT_THRESHOLD:
        method = "`pdftotext` (native PDF text layer)"
        raw_text = extracted
    else:
        method = f"OCR (`tesseract`, {OCR_DPI} DPI page renders via PyMuPDF) — no native text layer found"
        raw_text = ocr_pdf(pdf_path)

    title = find_doc_title(cat_key, slug)
    markdown = build_markdown(pdf_relpath, title, method, raw_text)

    out_path = pdf_path.with_suffix(".md")
    out_path.write_text(markdown, encoding="utf-8")
    return method, len(markdown)


def link_extraction_from_docs(pdf_relpath: str, md_relpath: str) -> int:
    """In every docs/**/*.md page whose Primary source cites this exact PDF
    (via the `sources/...pdf` backtick path), insert a companion bullet
    linking the extracted .md transcription — unless it's already there
    (idempotent: safe to re-run after re-extracting).

    Returns the number of doc pages updated."""
    pdf_citation = f"`{pdf_relpath}`"
    updated = 0
    for md in DOCS.rglob("*.md"):
        text = md.read_text(encoding="utf-8")
        if pdf_citation not in text:
            continue
        marker = f"`{md_relpath}`"
        if marker in text:
            continue  # already linked, from a previous run

        rel_link_str = Path(
            os.path.relpath(REPO_ROOT / md_relpath, start=md.parent)
        ).as_posix()

        lines = text.split("\n")
        out_lines = []
        for line in lines:
            out_lines.append(line)
            if pdf_citation in line and line.lstrip().startswith("- ["):
                indent = line[: len(line) - len(line.lstrip())]
                out_lines.append(
                    f"{indent}- Full text: [`{md_relpath}`]({rel_link_str}) "
                    f"(extracted, for search/offline reading)"
                )
        md.write_text("\n".join(out_lines), encoding="utf-8")
        updated += 1
    return updated


def main():
    pdfs = sorted(SOURCES.rglob("*.pdf"))
    if not pdfs:
        print("No PDFs found under sources/.", file=sys.stderr)
        return 1

    docs_updated_total = 0
    for pdf_path in pdfs:
        method, n_chars = process_pdf(pdf_path)
        rel = pdf_path.relative_to(REPO_ROOT)
        md_rel = rel.with_suffix(".md")
        print(f"{rel} -> {md_rel} ({n_chars:,} chars, {method})")
        n_docs = link_extraction_from_docs(rel.as_posix(), md_rel.as_posix())
        docs_updated_total += n_docs

    print(f"\nExtracted {len(pdfs)} PDFs; linked from {docs_updated_total} doc page(s).")
    return 0


if __name__ == "__main__":
    sys.exit(main())
