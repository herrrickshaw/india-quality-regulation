# How India Regulates Quality

A field guide to BIS and the ~36 other statutory regulators, accreditation boards and voluntary marks that
certify, license and grade quality in India, grounded in the actual Acts, Quality Control Orders, gazette
notifications and scheme pages behind each one. It is a Markdown reference (one page per body) plus the
mirrored primary documents and the small Python scripts that keep the derived files in sync.

> Status: maintained reference. Orientation map, not a compliance checklist: always verify against the
> regulator's current gazette notification before relying on it for a filing. Mirrored files under
> `sources/` remain the copyright of their originators (see Licence).

[![Link check](https://github.com/herrrickshaw/india-quality-regulation/actions/workflows/link-check.yml/badge.svg)](https://github.com/herrrickshaw/india-quality-regulation/actions/workflows/link-check.yml)
[![Entries](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/herrrickshaw/india-quality-regulation/main/badges/entries.json)](docs/coverage.md)

<!-- how-to-use-with-ai -->
New to this? See [How to use this repo with AI](HOW_TO_USE_WITH_AI.md) (clone, paste into an AI tool, ask in
plain English).

## What it does
- **Start here:** [`docs/00-overview.md`](docs/00-overview.md) explains the four-layer model
  (Acts, statutory regulators, accreditation apex, certification/testing bodies, marks on the product).
- **36 entries**, each naming the authority, legal basis, whether the mark is mandatory or voluntary, and
  linking the mirrored primary source. [`docs/coverage.md`](docs/coverage.md): 22 have the Act/Rules/Regulations/
  gazette text mirrored, 14 an official scheme or administrative page (the correct source for a body with no
  founding statute); none lack a mirrored source.
- **One-file edition:** [`COMPENDIUM.md`](COMPENDIUM.md) flattens the overview, all entries and the coverage
  table for offline reading or pasting elsewhere (generated from `docs/`).
- **Referenced standards:** [`docs/is-standards-referenced.md`](docs/is-standards-referenced.md) catalogues 37 IS
  numbers cited by the mirrored texts (e.g. IS 1417 for hallmarking). They are listed, **not downloaded**: IS
  standards are BIS's paid, DRM-locked product ([standardsbis.bsbedge.com](https://standardsbis.bsbedge.com/)).
- **Full-text transcriptions** of every mirrored PDF (`sources/*/<slug>.md`, via `pdftotext`, OCR for the one scan).

## Quick start
```bash
git clone https://github.com/herrrickshaw/india-quality-regulation.git
cd india-quality-regulation
python3 -m venv .venv && source .venv/bin/activate
pip install pytest ruff pymupdf==1.28.2     # PDF steps also need poppler + tesseract (+ Hindi data)
python3 scripts/generate_coverage.py        # regenerate docs/coverage.md and badges/entries.json
```
Reading needs nothing installed: open [`docs/00-overview.md`](docs/00-overview.md).

## How it works
`docs/**/*.md` is the maintained source; everything else is derived or checked from it.

| Stage | Module | Output |
|---|---|---|
| Extract PDF text | `scripts/extract_pdf_text.py` | `sources/*/<slug>.md`, plus "Full text" links in doc pages |
| Coverage table + badge | `scripts/generate_coverage.py` | `docs/coverage.md`, `badges/entries.json` |
| Flatten to one file | `scripts/build_compendium.py` | `COMPENDIUM.md` |
| Verify compendium | `scripts/verify_compendium.py --check all` | headings/fields/sections/anchors/counts match `docs/` |
| Verify extractions | `scripts/verify_pdf_extraction.py --check all` | coverage, OCR, completeness (within 3%), doc links |
| Verify references | `scripts/check_source_refs.py` | every inline `sources/...` path resolves |
| Shared constants | `scripts/_common.py` | category order, paths, `slugify` |

Every doc page carries a **Source tier** field (`Statutory / regulatory text` or `Official scheme/administrative
page`) and ends with a **Primary source** section linking the original URL and the mirrored copy. After
re-sourcing an entry, edit the page and re-run the generators; never hand-edit generated files. Sources that
blocked automated fetching are explained in the page's Notes and in each category's `MANIFEST.md` (several
`.gov.in`/`.nic.in` hosts, including `indiacode.nic.in` and `legislative.gov.in`, were unreachable; IndianKanoon
and Wayback Machine snapshots filled most gaps).

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
| Path | Purpose |
|---|---|
| `docs/` | one page per body/scheme (hand-written), plus `00-overview.md`, `is-standards-referenced.md`, generated `coverage.md` |
| `sources/<category>/` | mirrored primary documents, per-category `MANIFEST.md` (entry, file, URL, fetch date, type), generated PDF transcriptions |
| `scripts/` | generators and verifiers listed above |
| `tests/` | offline pytest unit/smoke tests for the scripts |
| `COMPENDIUM.md`, `badges/entries.json` | generated |
| `.github/workflows/` | `link-check.yml` (links, regeneration diff, verifiers), `ci.yml` (ruff + pytest) |

## Data sources
Official regulator and gazette sites (BIS, FSSAI, CDSCO, BEE, PESO, AERB, WPC, TEC, QCI boards, and others),
fetched by hand and mirrored under `sources/` with the original URL and fetch date in each `MANIFEST.md`.
Secondary copies (IndianKanoon, Wayback Machine) are used only where the official host was unreachable and are
marked as such. Copyright stays with the originating body.

## Configuration
None. No credentials are used or stored.

## Testing
```bash
ruff check . && pytest -q                                   # offline unit tests (what ci.yml runs)
python3 scripts/check_source_refs.py                        # internal, blocking in CI
python3 scripts/verify_compendium.py --check all            # internal, blocking in CI
python3 scripts/verify_pdf_extraction.py --check all        # needs poppler, tesseract, pymupdf==1.28.2
lychee --offline --config .lychee.toml README.md "docs/**/*.md" COMPENDIUM.md
```
`link-check.yml` additionally re-runs the three generators and fails on any diff in `docs/`, `COMPENDIUM.md` or
`badges/entries.json`. It deliberately does not byte-diff `sources/*.md`: poppler's output is version-dependent,
so `verify_pdf_extraction.py` checks coverage, OCR content, completeness and linkage instead. A second,
non-blocking job checks external URLs, because several `.gov.in` hosts are unreliable from GitHub runners.
Use `pymupdf==1.28.2` locally to match CI.

## Limitations and known issues
- Regulation changes often: the furniture QCO (2025), the FSSAI BIS/AGMARK omission (October 2024), the expanded
  BEE mandatory list (January 2026) and "Scheme-X" (September 2026) all moved recently. Check each page's fetch
  date and the current gazette.
- Some native-text gazette PDFs embed Hindi in a legacy pre-Unicode font; `pdftotext` cannot decode it into
  Devanagari (the English legal text is intact, and each affected transcription says so).
- `sources/bis-core/bis-crs.pdf` is a pure scan, OCR'd with tesseract (English + Hindi).
- `ayush-schedule-t.pdf` has a malformed trailer and is forced through PyMuPDF so local and CI output agree.
- IS standards are catalogued, not mirrored.

## Licence
Original analysis and prose (`docs/`, this file) are MIT-licensed; see [`LICENSE`](LICENSE). Mirrored files under
`sources/` remain the copyright of their originating government body or organisation, included for research and
reference with attribution and a link back in every case (see each `sources/*/MANIFEST.md`).
