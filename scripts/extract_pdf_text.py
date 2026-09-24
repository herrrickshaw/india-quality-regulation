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

# The only genuinely-scanned PDF in this repo (sources/bis-core/bis-crs.pdf)
# is 14 pages. If native-text extraction comes back empty for a much longer
# document, that's almost certainly a parser failure on an otherwise-native
# PDF (confirmed for ayush-schedule-t.pdf: 635 pages, extracts cleanly with
# 2M+ characters under a newer poppler, but both `pdftotext -layout` and
# plain `pdftotext` failed under Ubuntu's older poppler-utils in CI) rather
# than an actual scan — OCR-ing hundreds of pages to "fix" that would be
# absurdly expensive and just papers over the real problem. Past this page
# count, fail loudly instead of silently trying to OCR the whole thing.
OCR_MAX_PAGES = 40

# sources/health-pharma/ayush-schedule-t.pdf has a genuinely malformed
# xref/trailer that a newer poppler (this repo's local dev machines) reads
# fine but an older poppler (Ubuntu's apt package, used in CI) rejects
# outright ("Syntax Error: Couldn't find trailer dictionary"). Left to the
# normal try-pdftotext-then-fall-back chain, that means local runs commit
# a pdftotext-flavoured extraction while CI regenerates a PyMuPDF-flavoured
# one for the exact same PDF — a permanent, unfixable-by-retry mismatch in
# the "regenerate and diff" CI check. Forcing this one known file straight
# to PyMuPDF makes the method deterministic across both environments
# regardless of which poppler happens to be installed.
FORCE_PYMUPDF = {"sources/health-pharma/ayush-schedule-t.pdf"}

PDFTOTEXT_TIMEOUT_S = 120  # generous for even the largest (635-page) PDF here
TESSERACT_TIMEOUT_S = 90   # per page — generous for a single 300-DPI page image


def run(cmd, **kw):
    return subprocess.run(cmd, check=True, capture_output=True, text=True, **kw)


def native_text(pdf_path: Path) -> tuple[str, str]:
    """Three independent attempts, in order, each only tried if the last
    one came back empty/near-empty or failed outright:

    1. `pdftotext -layout` — keeps column/table alignment, best fidelity.
    2. plain `pdftotext` (no -layout) — simpler code path, sometimes more
       tolerant of a PDF structure that trips up -layout mode specifically.
    3. PyMuPDF's own `page.get_text()` — a completely independent PDF
       parser (not poppler at all), so a poppler-version-specific failure
       (seen in practice: a 635-page Word-exported PDF that both pdftotext
       modes failed to parse under Ubuntu's older poppler-utils, despite
       extracting cleanly under a newer Homebrew poppler locally) doesn't
       propagate here.

    Returns (text, method_label); text is "" only if all three failed or
    returned near-empty output, which the caller then treats as "needs
    OCR" — but only below OCR_MAX_PAGES, since a failure this deep for a
    large document is almost certainly a parser bug, not a real scan."""
    try:
        text = run(["pdftotext", "-layout", str(pdf_path), "-"], timeout=PDFTOTEXT_TIMEOUT_S).stdout
        if len(text.strip()) >= NATIVE_TEXT_THRESHOLD:
            return text, "`pdftotext -layout` (native PDF text layer)"
        print(f"WARNING: 'pdftotext -layout' on {pdf_path.name} exited 0 but returned "
              f"near-empty text; trying without -layout", file=sys.stderr)
    except subprocess.TimeoutExpired:
        print(f"WARNING: 'pdftotext -layout' timed out after {PDFTOTEXT_TIMEOUT_S}s on "
              f"{pdf_path.name}; retrying without -layout", file=sys.stderr)
    except subprocess.CalledProcessError as e:
        print(f"WARNING: 'pdftotext -layout' failed on {pdf_path.name} "
              f"(exit {e.returncode}); retrying without -layout: "
              f"{e.stderr.strip()[:300]}", file=sys.stderr)

    try:
        text = run(["pdftotext", str(pdf_path), "-"], timeout=PDFTOTEXT_TIMEOUT_S).stdout
        if len(text.strip()) >= NATIVE_TEXT_THRESHOLD:
            return text, "`pdftotext` (native PDF text layer)"
        print(f"WARNING: plain 'pdftotext' on {pdf_path.name} exited 0 but returned "
              f"near-empty text; trying PyMuPDF's own extractor next", file=sys.stderr)
    except subprocess.TimeoutExpired:
        print(f"WARNING: plain 'pdftotext' also timed out after {PDFTOTEXT_TIMEOUT_S}s on "
              f"{pdf_path.name}; trying PyMuPDF's own extractor next", file=sys.stderr)
    except subprocess.CalledProcessError as e:
        print(f"WARNING: plain 'pdftotext' also failed on {pdf_path.name} "
              f"(exit {e.returncode}): {e.stderr.strip()[:300]} — trying PyMuPDF's own "
              f"extractor next", file=sys.stderr)

    try:
        text = pymupdf_native_text(pdf_path)
        if len(text.strip()) >= NATIVE_TEXT_THRESHOLD:
            return text, "PyMuPDF `page.get_text()` (native PDF text layer; pdftotext/poppler failed on this file)"
        print(f"WARNING: PyMuPDF's own extractor on {pdf_path.name} also returned "
              f"near-empty text", file=sys.stderr)
    except Exception as e:
        print(f"WARNING: PyMuPDF's own extractor also failed on {pdf_path.name}: {e}",
              file=sys.stderr)

    return "", ""


def pymupdf_native_text(pdf_path: Path) -> str:
    import pymupdf

    doc = pymupdf.open(pdf_path)
    try:
        return "\f".join(page.get_text() for page in doc)
    finally:
        doc.close()


def pdf_page_count(pdf_path: Path) -> int:
    result = run(["pdfinfo", str(pdf_path)], timeout=30)
    m = re.search(r"^Pages:\s*(\d+)", result.stdout, re.M)
    if not m:
        raise RuntimeError(f"pdfinfo gave no page count for {pdf_path.name}")
    return int(m.group(1))


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
    """Find the doc page this PDF belongs to, and return its H1 title, for
    a friendly extraction-file header.

    Tries the naming convention first (docs/<cat>/<slug>.md — true for
    most PDFs, and unambiguous) before falling back to a text search for
    PDFs cited by a differently-named doc (e.g. a secondary source, like
    tea-board-coffee-board-coffee-act.pdf being cited by
    tea-board-coffee-board.md). That fallback search matches only the
    literal "mirrored at `sources/<cat>/<slug>.pdf`" citation phrase, not
    a bare substring — this file's own path can legitimately appear in
    ANOTHER doc's prose for an unrelated reason (confirmed in practice:
    ayush-gmp-premium-mark.md's Notes section discusses cdsco.pdf while
    explaining why it's a different, shorter file than
    ayush-schedule-t.pdf — a bare-substring search picked THAT doc's title
    for cdsco.md's own header, on whichever filesystem happened to iterate
    the category directory in an order that hit it first).

    Falls back to a slug-derived title if nothing matches either way."""
    same_name_doc = DOCS / cat_key / f"{slug}.md"
    if same_name_doc.is_file():
        text = same_name_doc.read_text(encoding="utf-8")
        m = re.search(r"^# (.+)$", text, re.M)
        if m:
            return m.group(1)

    cat_dir = DOCS / cat_key
    citation_marker = f"mirrored at `sources/{cat_key}/{slug}.pdf`"
    if cat_dir.is_dir():
        for md in sorted(cat_dir.glob("*.md")):
            text = md.read_text(encoding="utf-8")
            if citation_marker in text:
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

    if pdf_relpath in FORCE_PYMUPDF:
        extracted, native_method = pymupdf_native_text(pdf_path), "PyMuPDF `page.get_text()` (native PDF text layer; forced — see FORCE_PYMUPDF)"
    else:
        extracted, native_method = native_text(pdf_path)
    if len(extracted.strip()) >= NATIVE_TEXT_THRESHOLD:
        method = native_method
        raw_text = extracted
    else:
        page_count = pdf_page_count(pdf_path)
        if page_count > OCR_MAX_PAGES:
            raise RuntimeError(
                f"{pdf_path.relative_to(REPO_ROOT)}: native-text extraction came back empty, "
                f"but this PDF has {page_count} pages (over the {OCR_MAX_PAGES}-page OCR safety "
                f"cap). This is almost certainly a pdftotext/poppler-version parsing failure on "
                f"a real native-text PDF, not a genuine scan — OCR-ing a document this size "
                f"would be extremely slow and is very likely masking the real problem rather "
                f"than fixing it. Investigate the pdftotext WARNING above instead of raising "
                f"OCR_MAX_PAGES."
            )
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
    import time

    pdfs = sorted(SOURCES.rglob("*.pdf"))
    if not pdfs:
        print("No PDFs found under sources/.", file=sys.stderr)
        return 1

    run_start = time.monotonic()
    docs_updated_total = 0
    for pdf_path in pdfs:
        file_start = time.monotonic()
        method, n_chars = process_pdf(pdf_path)
        elapsed = time.monotonic() - file_start
        rel = pdf_path.relative_to(REPO_ROOT)
        md_rel = rel.with_suffix(".md")
        print(f"[{elapsed:6.1f}s] {rel} -> {md_rel} ({n_chars:,} chars, {method})")
        n_docs = link_extraction_from_docs(rel.as_posix(), md_rel.as_posix())
        docs_updated_total += n_docs

    total_elapsed = time.monotonic() - run_start
    print(f"\nExtracted {len(pdfs)} PDFs in {total_elapsed:.1f}s total; "
          f"linked from {docs_updated_total} doc page(s).")
    return 0


if __name__ == "__main__":
    sys.exit(main())
