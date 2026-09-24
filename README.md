# How India Regulates Quality

[![Link check](https://github.com/herrrickshaw/india-quality-regulation/actions/workflows/link-check.yml/badge.svg)](https://github.com/herrrickshaw/india-quality-regulation/actions/workflows/link-check.yml)
[![Entries](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/herrrickshaw/india-quality-regulation/main/badges/entries.json)](docs/coverage.md)

A field guide to BIS and the ~36 other statutory regulators, accreditation
boards and voluntary marks that certify, license and grade quality in
India — grounded in the actual Acts, Quality Control Orders, gazette
notifications and scheme pages behind each one, not just descriptions of
them.

**Start here → [`docs/00-overview.md`](docs/00-overview.md)** — the
four-layer model (Acts → statutory regulators → accreditation apex →
certification/testing bodies → marks on the product) that the rest of this
repo is organised around.

**Source coverage → [`docs/coverage.md`](docs/coverage.md)** — all 36
entries: 22 have the actual Act/Rules/Regulations/gazette notification
mirrored, 14 have an official scheme/administrative page (the correct
primary source for a body with no founding statute — an accreditation
board, a voluntary industry mark). Zero entries have nothing mirrored.

**Everything in one file → [`COMPENDIUM.md`](COMPENDIUM.md)** — the
overview, all 36 entries, and the coverage table flattened into a single
self-contained Markdown file, for offline reading, pasting elsewhere, or
handing to something without repo access. Generated from `docs/`; see
"Checks" below for how it stays in sync.

**Referenced technical standards → [`docs/is-standards-referenced.md`](docs/is-standards-referenced.md)**
— 37 Indian Standard (IS) numbers that the mirrored Acts/Regulations
actually cite (e.g. Hallmarking's IS 1417 for gold purity), catalogued
with title and context but **not downloaded** — unlike the public-domain
Acts elsewhere in this repo, individual IS standards are BIS's paid,
DRM-locked commercial product, sold through
[standardsbis.bsbedge.com](https://standardsbis.bsbedge.com/).

## Why this exists

BIS is the name most people reach for, but "quality regulation in India" is
actually a federation of independent regulators — FSSAI for food, CDSCO for
drugs and devices, BEE for energy labels, PESO for explosives, Legal
Metrology for weights and measures, and a separate accreditation apex (QCI)
that certifies the certifiers rather than the products. Each entry in this
repo names the actual authority, its legal basis, whether the mark is
mandatory or voluntary, and mirrors the primary source document so the claim
isn't just secondhand paraphrase.

## Index

### Apex & Accreditation Infrastructure
*Certifies the certifiers — issues no product mark itself.*

| Body | Status | Page |
|---|---|---|
| Quality Council of India (QCI) | Infrastructure | [docs](docs/apex-accreditation/quality-council-of-india.md) |
| NABCB — National Accreditation Board for Certification Bodies | Infrastructure | [docs](docs/apex-accreditation/nabcb.md) |
| NABL — National Accreditation Board for Testing and Calibration Laboratories | Infrastructure | [docs](docs/apex-accreditation/nabl.md) |
| NABH — National Accreditation Board for Hospitals & Healthcare Providers | Infrastructure | [docs](docs/apex-accreditation/nabh.md) |
| NABET — National Accreditation Board for Education and Training | Infrastructure | [docs](docs/apex-accreditation/nabet.md) |

### Cross-Sector Statutory — BIS Core
*BIS's own schemes, which touch almost every industry.*

| Body | Status | Page |
|---|---|---|
| BIS — ISI Mark | Mixed | [docs](docs/bis-core/bis-isi-mark.md) |
| BIS — Compulsory Registration Scheme (CRS) | Mandatory | [docs](docs/bis-core/bis-crs.md) |
| BIS — Hallmarking | Mandatory (gold); voluntary (silver) | [docs](docs/bis-core/bis-hallmarking.md) |
| BIS — Management System Certification | Voluntary | [docs](docs/bis-core/bis-management-system-certification.md) |
| BIS / MoEFCC — Ecomark | Voluntary | [docs](docs/bis-core/ecomark.md) |
| STQC | Mixed | [docs](docs/bis-core/stqc.md) |

### Food & Agriculture

| Body | Status | Page |
|---|---|---|
| FSSAI | Mandatory | [docs](docs/food-agriculture/fssai.md) |
| AGMARK | Mixed | [docs](docs/food-agriculture/agmark.md) |
| APEDA — NPOP (organic) | Voluntary | [docs](docs/food-agriculture/apeda-npop.md) |
| PGS-India | Voluntary | [docs](docs/food-agriculture/pgs-india.md) |
| Spices Board India | Voluntary | [docs](docs/food-agriculture/spices-board.md) |
| Tea Board / Coffee Board | Mixed | [docs](docs/food-agriculture/tea-board-coffee-board.md) |
| MPEDA | Mandatory (for exporters) | [docs](docs/food-agriculture/mpeda.md) |

### Health, Pharma & AYUSH

| Body | Status | Page |
|---|---|---|
| CDSCO | Mandatory | [docs](docs/health-pharma/cdsco.md) |
| State Drug Controllers | Mandatory | [docs](docs/health-pharma/state-drug-controllers.md) |
| AYUSH — GMP & Premium Mark | Mixed | [docs](docs/health-pharma/ayush-gmp-premium-mark.md) |

### Energy, Safety & Environment

| Body | Status | Page |
|---|---|---|
| BEE — Star Label | Mandatory (for notified categories) | [docs](docs/energy-safety-environment/bee-star-label.md) |
| PESO | Mandatory | [docs](docs/energy-safety-environment/peso.md) |
| AERB | Mandatory | [docs](docs/energy-safety-environment/aerb.md) |
| CPCB / State PCBs | Mandatory | [docs](docs/energy-safety-environment/cpcb-state-pcbs.md) |

### Telecom & Electronics

| Body | Status | Page |
|---|---|---|
| WPC Wing — Equipment Type Approval (ETA) | Mandatory | [docs](docs/telecom-electronics/wpc-eta.md) |
| TEC — MTCTE | Mandatory | [docs](docs/telecom-electronics/tec-mtcte.md) |

### Textiles & Handicrafts

| Body | Status | Page |
|---|---|---|
| Silk Mark | Voluntary | [docs](docs/textiles/silk-mark.md) |
| Handloom Mark / India Handloom Brand | Voluntary | [docs](docs/textiles/handloom-mark.md) |
| Textiles Committee | Mixed | [docs](docs/textiles/textiles-committee.md) |

### Origin & Trademarks

| Body | Status | Page |
|---|---|---|
| Geographical Indications (GI) Registry | Voluntary | [docs](docs/ip-trademarks/gi-registry.md) |
| Certification Trade Marks | Voluntary | [docs](docs/ip-trademarks/certification-trade-marks.md) |

### Legal Metrology

| Body | Status | Page |
|---|---|---|
| Legal Metrology | Mandatory | [docs](docs/legal-metrology/legal-metrology.md) |

### Private / Industry Voluntary Marks
*Real marks, but not government-run.*

| Body | Status | Page |
|---|---|---|
| Halal Certification | Voluntary | [docs](docs/private-voluntary/halal-certification.md) |
| Woolmark | Voluntary | [docs](docs/private-voluntary/woolmark.md) |
| GreenPro / Green Building Marks | Voluntary | [docs](docs/private-voluntary/greenpro.md) |

## Repository layout

```
docs/00-overview.md       the four-layer model
docs/coverage.md          generated source-coverage table (see below)
docs/                     one page per body/scheme — authority, legal basis,
                          status, source tier, scope, cross-references,
                          primary-source link
COMPENDIUM.md             generated: every docs/ page flattened into one
                          self-contained file
sources/                  mirrored primary documents (Acts, QCOs, gazette
                          notifications, official scheme pages), grouped in
                          the same categories as docs/
sources/*/*.pdf.md        generated: full-text extraction of the PDF next
                          to it (pdftotext, or OCR for the one scan with
                          no text layer) — a <slug>.pdf's transcription is
                          always <slug>.md in the same folder
sources/*/MANIFEST.md     per-category table: entry, local file, original
                          URL, fetch date, document type, notes
badges/entries.json       shields.io endpoint badge (entry count) — also
                          written by generate_coverage.py
scripts/generate_coverage.py   regenerates docs/coverage.md and
                          badges/entries.json from every doc page's
                          **Source tier:** field
scripts/build_compendium.py    regenerates COMPENDIUM.md from every
                          docs/*.md page, rewiring cross-doc links to
                          in-file anchors
scripts/verify_compendium.py   checks COMPENDIUM.md against its source
                          docs (headings/fields/sections/anchors/coverage
                          counts) — CI check, see "Checks" below
scripts/extract_pdf_text.py    regenerates every sources/*/*.md PDF
                          transcription, and links each one from its
                          entry's doc page
scripts/verify_pdf_extraction.py   checks every PDF transcription
                          (coverage/OCR content/completeness/doc
                          links/reproducibility) — CI check, see "Checks"
                          below
scripts/check_source_refs.py   CI check — see "Checks" below
```

Every `docs/*.md` page carries a **Source tier** field (`Statutory /
regulatory text` or `Official scheme/administrative page`) right in its
header, and ends with a **Primary source** section linking both to the
original URL and to the mirrored copy under `sources/`. `docs/coverage.md`
is generated from that field, so after re-sourcing an entry, update the doc
page and re-run `python3 scripts/generate_coverage.py` rather than editing
the coverage table by hand. Where a site blocked automated fetching, the
page's Notes section says so and records what was tried — see the
per-category `MANIFEST.md` files for the full detail (a handful of
`.gov.in`/`.nic.in` hosts, including `indiacode.nic.in` and
`legislative.gov.in`, are consistently unreachable from this environment;
IndianKanoon and Wayback Machine snapshots covered most of the resulting
gaps).

Every PDF mirrored under `sources/` also has a full-text `.md`
transcription next to it, generated by
[`scripts/extract_pdf_text.py`](scripts/extract_pdf_text.py) — useful for
full-text search or reading a 600-page gazette PDF without a PDF viewer.
Most of these Acts/Regulations extract cleanly via `pdftotext`; one PDF
(`sources/bis-core/bis-crs.pdf`) is a pure scan with no text layer and was
OCR'd instead (`tesseract`, English + Hindi, since these gazette scans are
routinely bilingual). A handful of the native-text PDFs also embed their
Hindi text in a legacy pre-Unicode font that `pdftotext` can't decode into
real Devanagari — that's a property of the source PDF's font encoding, not
an extraction bug, and each affected file says so; the English legal text
extracts correctly regardless. Every doc page whose entry has a mirrored
PDF links to that PDF's transcription in its Primary source section.

## Reading the marks correctly

This is an orientation map, not a compliance checklist. Whether a specific
product needs BIS registration, which Quality Control Order applies, or
which CDSCO device class a product falls into depends on current
notifications and changes often — the furniture QCO (2025), the FSSAI
BIS/AGMARK omission (October 2024), the expanded BEE mandatory list
(January 2026), and "Scheme-X" (September 2026) all moved in the last two
years. Check the fetch date on each page's primary source and verify
against the regulator's current gazette notification before relying on
anything here for an actual filing.

## Checks

A GitHub Actions workflow (`.github/workflows/link-check.yml`) runs on
every push/PR to `main`, monthly on a schedule, and on demand, split into two
jobs with different reliability:

- **Internal links (blocking)** — every relative cross-link between doc
  pages (including `COMPENDIUM.md`'s in-file anchors), checked offline via
  [lychee](https://lychee.cli.rs) (config: [`.lychee.toml`](.lychee.toml)),
  plus every inline `` `sources/...` `` path via
  [`scripts/check_source_refs.py`](scripts/check_source_refs.py) (a
  hyperlink checker doesn't see those — they're code spans, not links —
  and a mismatched one is exactly the kind of mistake this repo has hit
  before). This job also re-runs `generate_coverage.py` and
  `build_compendium.py` and fails on any diff, so a doc page edited
  without regenerating its derived files fails the build instead of
  silently drifting, and re-runs
  [`scripts/verify_compendium.py`](scripts/verify_compendium.py) to check
  the compendium's headings, fields, section content, anchors, and
  embedded coverage counts all still match their source docs exactly, and
  [`scripts/verify_pdf_extraction.py`](scripts/verify_pdf_extraction.py)
  to check every PDF's `.md` transcription is present, complete (within 3%
  of a fresh direct extraction), correctly OCR'd where OCR was needed, and
  linked from its doc page — the regeneration step above already re-runs
  `extract_pdf_text.py` itself and diffs `sources/`/`docs/`, which is what
  proves reproducibility (a separate scratch-copy re-run here once made
  this job hang for 15+ minutes on a slow CI runner; removed in favour of
  the cheaper diff-based check already used for coverage/compendium).
  Fully deterministic, no network involved, and fails the build. (Needs
  `poppler-utils`, `tesseract-ocr` + `tesseract-ocr-hin`, and `pymupdf` —
  the CI job installs these; see below to run locally.)
- **External sources (best-effort)** — every "Primary source" URL, over
  the network. Several official `.gov.in`/`.nic.in` hosts in this repo are
  reachable normally but not reliably from GitHub's hosted runners — broken
  TLS chains or what looks like IP-range blocking, confirmed by comparing a
  clean local run against this job's failures — so it *reports* rather than
  blocking merges. Read the job summary for what's actually unreachable.

Run it all locally before pushing (macOS: `brew install poppler tesseract
tesseract-lang`; `pip install pymupdf==1.28.2` either way — pinned to
match CI, since a different PyMuPDF release can legitimately extract a
given PDF's text slightly differently):

```bash
python3 scripts/generate_coverage.py                                      # regenerate coverage + badge
python3 scripts/build_compendium.py                                       # regenerate COMPENDIUM.md
lychee --offline --config .lychee.toml README.md "docs/**/*.md" COMPENDIUM.md   # internal, blocking
python3 scripts/check_source_refs.py                                      # internal, blocking
python3 scripts/verify_compendium.py --check all                          # internal, blocking
python3 scripts/verify_pdf_extraction.py --check all                      # internal, blocking
lychee --config .lychee.toml README.md "docs/**/*.md" COMPENDIUM.md       # external, best-effort
```

## License

Original analysis and prose (`docs/`, this file) are MIT-licensed — see
[`LICENSE`](LICENSE). Mirrored files under `sources/` remain the copyright
of their originating government body or organisation; they're included here
for research, reference and continuity, with attribution and a link back to
the original in every case (see the `MANIFEST.md` in each `sources/`
subfolder).
