# How India Regulates Quality

[![Link check](https://github.com/herrrickshaw/india-quality-regulation/actions/workflows/link-check.yml/badge.svg)](https://github.com/herrrickshaw/india-quality-regulation/actions/workflows/link-check.yml)

A field guide to BIS and the ~36 other statutory regulators, accreditation
boards and voluntary marks that certify, license and grade quality in
India — grounded in the actual Acts, Quality Control Orders, gazette
notifications and scheme pages behind each one, not just descriptions of
them.

**Start here → [`docs/00-overview.md`](docs/00-overview.md)** — the
four-layer model (Acts → statutory regulators → accreditation apex →
certification/testing bodies → marks on the product) that the rest of this
repo is organised around.

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
docs/                    one page per body/scheme — authority, legal basis,
                          status, scope, cross-references, primary-source link
sources/                  mirrored primary documents (Acts, QCOs, gazette
                          notifications, official scheme pages), grouped in
                          the same categories as docs/
sources/*/MANIFEST.md     per-category table: entry, local file, original
                          URL, fetch date, document type, notes
```

Every `docs/*.md` page ends with a **Primary source** section linking both
to the original URL and to the mirrored copy under `sources/`. Where no
stable public document could be found or a site blocked automated fetching,
the page says so explicitly instead of silently omitting it — see the
per-category `MANIFEST.md` files for exactly what was and wasn't mirrored,
and why (a handful of `.gov.in`/`.nic.in` hosts serve JS-only shells or
timed out; those are documented per entry, with an alternate official
source substituted where one exists).

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
every push/PR to `main`, weekly on a schedule, and on demand, split into two
jobs with different reliability:

- **Internal links (blocking)** — every relative cross-link between doc
  pages, checked offline via [lychee](https://lychee.cli.rs) (config:
  [`.lychee.toml`](.lychee.toml)), plus every inline `` `sources/...` ``
  path via [`scripts/check_source_refs.py`](scripts/check_source_refs.py)
  (a hyperlink checker doesn't see those — they're code spans, not links —
  and a mismatched one is exactly the kind of mistake this repo has hit
  before). Fully deterministic, no network involved, and fails the build.
- **External sources (best-effort)** — every "Primary source" URL, over
  the network. Several official `.gov.in`/`.nic.in` hosts in this repo are
  reachable normally but not reliably from GitHub's hosted runners — broken
  TLS chains or what looks like IP-range blocking, confirmed by comparing a
  clean local run against this job's failures — so it *reports* rather than
  blocking merges. Read the job summary for what's actually unreachable.

Run both locally before pushing:

```bash
lychee --offline --config .lychee.toml README.md "docs/**/*.md"   # internal, blocking
python3 scripts/check_source_refs.py                              # internal, blocking
lychee --config .lychee.toml README.md "docs/**/*.md"             # external, best-effort
```

## License

Original analysis and prose (`docs/`, this file) are MIT-licensed — see
[`LICENSE`](LICENSE). Mirrored files under `sources/` remain the copyright
of their originating government body or organisation; they're included here
for research, reference and continuity, with attribution and a link back to
the original in every case (see the `MANIFEST.md` in each `sources/`
subfolder).
