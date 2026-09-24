# AYUSH — GMP & Premium Mark

**Authority:** Ministry of AYUSH, with the Quality Council of India (QCI) as scheme manager for the voluntary mark
**Status:** Mixed (GMP certification mandatory; AYUSH Standard/Premium Mark voluntary)
**Established:** Schedule T added to the Drugs and Cosmetics Rules in 2000; AYUSH Mark certification scheme launched January 2010 (QCI-run since 2009)
**Legal basis:** Drugs and Cosmetics Act, 1940 and Rules, 1945 — Schedule T (GMP for Ayurvedic, Siddha and Unani drugs, made under Rule 157); AYUSH Mark Certification Scheme (QCI/Ministry of AYUSH scheme document)
**Marks issued:** AYUSH Standard Mark, AYUSH Premium Mark
**Source tier:** Statutory / regulatory text — the Act, Rules, Regulations, Order or gazette notification itself is mirrored, not just a page about it.

## Scope

The Ministry of AYUSH regulates Ayurvedic, Siddha, Unani and Homoeopathy (ASU&H) drug manufacturing through the same central Drugs and Cosmetics Act, 1940 framework that CDSCO administers for allopathic drugs — but through its own schedule. Schedule T of the Drugs and Cosmetics Rules, 1945 lays down mandatory Good Manufacturing Practice requirements for ASU drug manufacturers: factory premises standards, hygienic conditions, recommended machinery and equipment, and in-house quality-control requirements, with licensing handled by the relevant [state drug controller](state-drug-controllers.md). On top of this mandatory floor sits the voluntary AYUSH Mark Certification Scheme, developed by the Ministry of AYUSH with QCI as scheme manager and accreditation body: it has two tiers, the AYUSH Standard Mark (based on domestic Schedule T/GMP compliance) and the AYUSH Premium Mark (aligned to WHO GMP and other stricter international benchmarks, aimed at manufacturers exporting ASU&H products). Certification is carried out by NABCB-accredited third-party certification bodies against the scheme document, not by the Ministry directly. As of the scheme's public reporting, over a hundred products carry the Premium Mark and roughly twice that number the Standard Mark — small numbers relative to India's ASU&H manufacturing base, reflecting the mark's voluntary, export-oriented niche.

## Primary source

- [Schedule T, Drugs and Cosmetics Rules, 1945](https://cdsco.gov.in/opencms/export/sites/CDSCO_WEB/Pdf-documents/acts_rules/2016DrugsandCosmeticsAct1940Rules1945.pdf) (See Rule 157) — "Good Manufacturing Practices for Ayurvedic, Siddha and Unani Medicines," the actual mandatory-GMP legal text — mirrored at `sources/health-pharma/ayush-schedule-t.pdf`, fetched 2026-09-24. This is a fuller CDSCO consolidation of the Drugs and Cosmetics Act, 1940 + Rules, 1945 (635 pp, all Schedules) than the Act-only PDF already mirrored for [CDSCO](cdsco.md) (`sources/health-pharma/cdsco.pdf`, 64 pp) — that shorter file does **not** contain Schedule T, confirmed by direct text search; this longer one does, starting at its page ~553 ("SCHEDULE T (See rule 157)").
- Full text: [`sources/health-pharma/cdsco.md`](../../sources/health-pharma/cdsco.md) (extracted, for search/offline reading)
- Full text: [`sources/health-pharma/ayush-schedule-t.md`](../../sources/health-pharma/ayush-schedule-t.md) (extracted, for search/offline reading)
- [Ayush Mark Certification Scheme](https://www.pib.gov.in/PressReleasePage.aspx?PRID=1843836) (Press Information Bureau, Government of India) — the voluntary AYUSH Mark scheme announcement, kept as secondary — mirrored at `sources/health-pharma/ayush-gmp-premium-mark.html`, fetched 2026-09-24

## Notes

- The Ministry of AYUSH's own site (`ayush.gov.in`) hosts Schedule T and scheme material, but its content-heavy subdomains — `main.ayush.gov.in` and `ayushnext.ayush.gov.in`, both cited by search results as the canonical AYUSH Mark pages — do not currently resolve in DNS (confirmed via two independent resolvers, not just a local network issue), and `ayush.gov.in` itself serves a JavaScript-rendered single-page app that returns 404/empty content to a non-browser fetch. The PIB press release remains the best available source specifically for the voluntary AYUSH Mark scheme document itself (as opposed to the mandatory Schedule T GMP floor, now covered above); treat it as an entry point, not the full scheme text.
- No separate AYUSH Premium Mark scheme notification was found on an `ayush.gov.in` path outside the JS-shell root during this pass.
- Two certification bodies were named at the scheme's 2010 launch (FOODCERT Hyderabad and Bureau Veritas Bombay); the current NABCB-accredited CB list should be checked at the time of use rather than assumed static.
- Don't confuse Schedule T (mandatory GMP floor) with the AYUSH Mark (voluntary, export-grade signal) — a manufacturer can be fully legal under Schedule T without ever pursuing the AYUSH Mark.
- The mirrored D&C Rules text also cites specific IS standards for
  cosmetics (Schedule S/Q) and devices elsewhere in the same consolidation
  — catalogued, not downloaded, in
  [`docs/is-standards-referenced.md`](../is-standards-referenced.md).
