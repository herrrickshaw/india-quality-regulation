#!/usr/bin/env python3
"""Verify the sources/**/*.pdf -> sources/**/*.md text extractions.

Each --check prints a distinct success-only token and exits 0 only if
every assertion for that check passes; otherwise it prints the specific
failure(s) to stderr and exits 1. Used as the CHECK oracle for GATES.md.
"""
import argparse
import re
import subprocess
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import extract_pdf_text as extractor  # reuse its exact pdftotext-with-fallback logic

REPO_ROOT = Path(__file__).resolve().parent.parent
SOURCES = REPO_ROOT / "sources"
DOCS = REPO_ROOT / "docs"

MIN_EXTRACTION_BYTES = 400  # below this, the file is basically just the header
COMPLETENESS_TOLERANCE = 0.03  # allow 3% drift between extraction and a fresh direct pdftotext run


def all_pdfs():
    return sorted(SOURCES.rglob("*.pdf"))


def check_coverage():
    pdfs = all_pdfs()
    if not pdfs:
        print("FAIL: no PDFs found under sources/ at all", file=sys.stderr)
        sys.exit(1)

    failures = []
    for pdf in pdfs:
        md = pdf.with_suffix(".md")
        if not md.is_file():
            failures.append(f"{pdf.relative_to(REPO_ROOT)}: no companion .md extraction file")
            continue
        size = md.stat().st_size
        if size < MIN_EXTRACTION_BYTES:
            failures.append(f"{md.relative_to(REPO_ROOT)}: only {size} bytes — looks empty/near-empty")

    if failures:
        for f in failures:
            print(f"FAIL: {f}", file=sys.stderr)
        sys.exit(1)
    print(f"EXTRACTION_COVERAGE_OK ({len(pdfs)} PDFs, all have a non-trivial .md extraction)")


def check_ocr_content():
    # The one PDF known to have no native text layer at build time.
    target = SOURCES / "bis-core" / "bis-crs.pdf"
    if not target.is_file():
        print(f"FAIL: expected OCR-path fixture {target} not found", file=sys.stderr)
        sys.exit(1)

    # Negative control: confirm THIS PDF really has no usable native text
    # layer (otherwise this whole check is testing nothing — see
    # references/gates.md on testing a known positive before trusting an
    # absence claim... here it's the inverse: confirm the "positive" input
    # to the OCR path is genuinely OCR-only, not silently native).
    native = extractor.native_text(target)
    if len(native.strip()) >= 40:
        print(f"FAIL: {target.relative_to(REPO_ROOT)} unexpectedly has native text — "
              f"the OCR-path fixture assumption is stale, update this check", file=sys.stderr)
        sys.exit(1)

    md = target.with_suffix(".md")
    if not md.is_file():
        print(f"FAIL: {md.relative_to(REPO_ROOT)} does not exist", file=sys.stderr)
        sys.exit(1)
    text = md.read_text(encoding="utf-8")

    failures = []
    # "OCR" alone appears in every file's generic caveat sentence, native or
    # not ("OCR output in particular can contain recognition errors") — a
    # vacuous assertion that's true regardless of which method actually ran.
    # Match the method line's specific phrasing instead.
    if "no native text layer found" not in text[:600]:
        failures.append("extraction file's own header doesn't say OCR was used "
                         "(missing 'no native text layer found')")
    if len(text) < 5000:
        failures.append(f"only {len(text)} chars — too short for a real 14-page OCR pass")
    # A term that should survive OCR of this specific Order even with
    # some character-level noise elsewhere on the page.
    if not re.search(r"Compulsory Registration", text, re.I):
        failures.append("expected term 'Compulsory Registration' not found anywhere in the OCR text")

    if failures:
        for f in failures:
            print(f"FAIL: {f}", file=sys.stderr)
        sys.exit(1)
    print(f"EXTRACTION_OCR_OK (bis-crs.pdf confirmed scan-only; OCR text is substantial and on-topic)")


def strip_extraction_markup(text: str) -> str:
    """Remove the header block, page-comment markers, and '---' page
    separators this repo's own extractor adds, leaving just the PDF's own
    text — so it can be compared to a fresh, unwrapped pdftotext run."""
    # Drop everything up to and including the "---\n\n" that ends the header.
    m = re.search(r"\n---\n\n", text)
    body = text[m.end():] if m else text
    body = re.sub(r"<!-- page \d+ -->\n\n", "", body)
    body = re.sub(r"\n\n---\n\n", "\n\n", body)
    return body


def check_completeness():
    failures = []
    checked = 0
    for pdf in all_pdfs():
        md = pdf.with_suffix(".md")
        if not md.is_file():
            continue  # covered by check_coverage
        text = md.read_text(encoding="utf-8")
        # Every file's generic caveat mentions "OCR" in passing ("OCR output
        # in particular can contain recognition errors"), so that word alone
        # can't tell native-text files apart from OCR'd ones — match the
        # method line's specific phrasing instead.
        if "no native text layer found" in text[:600]:
            continue  # OCR path has its own dedicated check, not diffable against pdftotext

        fresh = extractor.native_text(pdf)
        fresh_len = len(re.sub(r"\s+", "", fresh))
        if fresh_len == 0:
            continue  # shouldn't happen (would've gone through OCR), but don't divide by zero

        extracted_len = len(re.sub(r"\s+", "", strip_extraction_markup(text)))
        drift = abs(extracted_len - fresh_len) / fresh_len
        checked += 1
        if drift > COMPLETENESS_TOLERANCE:
            failures.append(
                f"{md.relative_to(REPO_ROOT)}: {drift:.1%} drift from a fresh pdftotext run "
                f"(extracted={extracted_len} chars, fresh={fresh_len} chars) — looks truncated or altered"
            )

    if failures:
        for f in failures:
            print(f"FAIL: {f}", file=sys.stderr)
        sys.exit(1)
    print(f"EXTRACTION_COMPLETENESS_OK ({checked} native-text PDFs, all within "
          f"{COMPLETENESS_TOLERANCE:.0%} of a fresh direct extraction)")


def check_doc_links():
    failures = []
    checked = 0
    for pdf in all_pdfs():
        pdf_rel = pdf.relative_to(REPO_ROOT).as_posix()
        md_rel = pdf.with_suffix(".md").relative_to(REPO_ROOT).as_posix()
        pdf_citation = f"`{pdf_rel}`"
        extraction_marker = f"`{md_rel}`"

        citing_docs = [
            d for d in DOCS.rglob("*.md")
            if pdf_citation in d.read_text(encoding="utf-8")
        ]
        if not citing_docs:
            failures.append(f"{pdf_rel}: no doc page cites this PDF at all — can't check link placement")
            continue

        checked += 1
        for d in citing_docs:
            text = d.read_text(encoding="utf-8")
            if extraction_marker not in text:
                failures.append(
                    f"{d.relative_to(REPO_ROOT)}: cites {pdf_rel} but doesn't link its extraction {md_rel}"
                )

    if failures:
        for f in failures:
            print(f"FAIL: {f}", file=sys.stderr)
        sys.exit(1)
    print(f"EXTRACTION_DOC_LINKS_OK ({checked} PDFs, every citing doc page links the extraction)")


def check_reproducible():
    """Re-run the extractor into a scratch copy and diff against the
    committed files — confirms nothing was hand-edited after generation."""
    import shutil
    import tempfile

    with tempfile.TemporaryDirectory() as tmp:
        tmp_path = Path(tmp)
        shutil.copytree(SOURCES, tmp_path / "sources")
        shutil.copytree(DOCS, tmp_path / "docs")

        script = REPO_ROOT / "scripts" / "extract_pdf_text.py"
        code = script.read_text(encoding="utf-8")
        code = code.replace(
            'REPO_ROOT = Path(__file__).resolve().parent.parent',
            f'REPO_ROOT = Path({str(tmp_path)!r})',
        )
        scratch_script = tmp_path / "extract_pdf_text.py"
        scratch_script.write_text(code, encoding="utf-8")

        result = subprocess.run(
            [sys.executable, str(scratch_script)],
            capture_output=True, text=True, cwd=tmp_path,
        )
        if result.returncode != 0:
            print(f"FAIL: re-run of extract_pdf_text.py failed: {result.stderr[-2000:]}", file=sys.stderr)
            sys.exit(1)

        failures = []
        for pdf in all_pdfs():
            rel = pdf.relative_to(REPO_ROOT)
            committed_md = pdf.with_suffix(".md")
            scratch_md = tmp_path / rel.with_suffix(".md")
            if not scratch_md.is_file():
                failures.append(f"{rel}: scratch re-run produced no output at all")
                continue
            if committed_md.read_bytes() != scratch_md.read_bytes():
                # Header line 4 embeds today's date — allow that one line to
                # differ (a re-run on a later date is still "reproducible"
                # in every way that matters) but nothing else.
                committed_lines = committed_md.read_text(encoding="utf-8").splitlines()
                scratch_lines = scratch_md.read_text(encoding="utf-8").splitlines()
                diff_lines = [
                    i for i, (a, b) in enumerate(zip(committed_lines, scratch_lines)) if a != b
                ]
                non_date_diffs = [i for i in diff_lines if "Generated by" not in committed_lines[i]]
                if non_date_diffs or len(committed_lines) != len(scratch_lines):
                    failures.append(f"{rel}: re-extraction differs from the committed .md beyond just the date")

        if failures:
            for f in failures:
                print(f"FAIL: {f}", file=sys.stderr)
            sys.exit(1)
    print("EXTRACTION_REPRODUCIBLE_OK (fresh re-run matches every committed extraction file)")


CHECKS = {
    "coverage": check_coverage,
    "ocr-content": check_ocr_content,
    "completeness": check_completeness,
    "doc-links": check_doc_links,
    "reproducible": check_reproducible,
}


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--check", required=True, choices=list(CHECKS) + ["all"])
    args = parser.parse_args()
    if args.check == "all":
        for fn in CHECKS.values():
            fn()
    else:
        CHECKS[args.check]()


if __name__ == "__main__":
    sys.exit(main())
