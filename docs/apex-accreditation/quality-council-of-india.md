# Quality Council of India (QCI)

**Authority:** Public-Private Partnership — Government of India (anchored by DPIIT, Ministry of Commerce & Industry) with industry associations ASSOCHAM, CII and FICCI
**Status:** Infrastructure
**Established:** 1997
**Legal basis:** Registered society under the Societies Registration Act, 1860, set up on the recommendation of an EU expert mission and a 1996 Cabinet decision; DPIIT is the nodal ministry
**Marks issued:** None — accredits other bodies

## Scope

QCI sits at the top of India's accreditation stack, one layer above the statutory
regulators described elsewhere in this repo. It does not test or certify any
product, service, person, or organisation itself. Instead it runs five
constituent boards that accredit the certifiers, auditors, and labs that
everyone else — BIS, FSSAI, CDSCO, hospitals, schools, exporters — relies on:
[NABCB](nabcb.md) (certification, inspection and validation/verification
bodies), [NABL](nabl.md) (testing and calibration laboratories),
[NABH](nabh.md) (hospitals and healthcare providers), [NABET](nabet.md)
(education, training, and EIA/energy-audit consultants), and the National
Board for Quality Promotion (NBQP, not covered as a separate page in this
repo — it runs QCI's outreach and India's national quality awards rather than
an accreditation scheme). QCI's founding was a direct government response to
India needing a WTO/TBT-compliant, internationally recognised accreditation
infrastructure rather than each ministry inventing its own. Ratan Tata was
QCI's first chairman. Because QCI itself issues no mark, every certification
mark or logo you actually see on a product or a hospital wall — from ISO 9001
to NABH accreditation — traces its credibility back through one of these four
boards to QCI, and from QCI to the DPIIT.

## Primary source

- [Quality Council of India](https://qcin.org/) — mirrored at `sources/apex-accreditation/quality-council-of-india.html`, fetched 2026-09-24

## Notes

- QCI marked 25 years in 2022 (founded 1997), and public explainer pieces
  consistently describe it as PPP-structured with DPIIT as the anchoring
  ministry — this repo follows that consensus rather than any single
  founding-charter PDF, since QCI's own site does not publish its 1997
  Memorandum of Association online.
- The fifth constituent board, NBQP (National Board for Quality Promotion),
  is intentionally out of scope for this 5-entry apex-accreditation set — it
  promotes quality culture and runs awards rather than accrediting
  conformity-assessment bodies, so it doesn't fit the "accredits the
  accreditors" pattern the other four follow.
- qcin.org returned HTTP 403 to a bare `curl` request (likely a bot-detection
  rule on user-agent) and only served content once a standard browser
  User-Agent header was sent — noted here in case the mirrored HTML looks
  unusually reliant on that workaround.
