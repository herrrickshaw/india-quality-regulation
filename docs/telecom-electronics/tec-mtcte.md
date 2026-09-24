# TEC — MTCTE (Mandatory Testing & Certification of Telecommunication Equipment)

**Authority:** Telecommunication Engineering Centre (TEC), Department of Telecommunications
**Status:** Mandatory
**Established:** 2017 (procedure notified under the Indian Telegraph (Amendment) Rules, 2017)
**Legal basis:** Indian Telegraph Act, 1885 (as amended); Indian Telegraph (Amendment) Rules, 2017
**Marks issued:** MTCTE certificate (issued per telecom equipment category against Essential Requirements / Generic Requirements / Interface Requirements)
**Source tier:** Statutory / regulatory text — the Act, Rules, Regulations, Order or gazette notification itself is mirrored, not just a page about it.

## Scope

TEC is the Department of Telecommunications' standards and testing arm. Under the Indian Telegraph (Amendment) Rules, 2017, it administers MTCTE, which requires telecom equipment to be tested and certified before it can be connected to or sold for use on Indian telecom networks. Testing is carried out by TEC-designated Conformance Assessment Bodies (CABs) — accredited Indian labs — against category-specific Essential Requirements (ER), Generic Requirements (GR) and Interface Requirements (IR); TEC issues the certificate once a CAB's test report confirms compliance. The scheme exists to ensure equipment doesn't degrade the performance of the network it connects to, keeps radio-frequency emissions within prescribed limits, and meets relevant national/international standards — a network-integrity and interoperability check, distinct from [WPC's ETA](wpc-eta.md), which is about radio-spectrum compliance, and from BIS's Compulsory Registration Scheme (CRS, see [../bis-core/bis-crs.md](../bis-core/bis-crs.md)), which covers electrical and IT-hardware safety for many of the same devices. A modem, router or IoT gateway sold in India can need MTCTE, WPC ETA and BIS CRS certification simultaneously, each covering a different risk. TEC administers the whole online process through its dedicated `mtcte.tec.gov.in` certification portal.

## Primary source

- [Procedure for Mandatory Testing & Certification of Telecommunication Equipment (MTCTE), 2017](https://tec.gov.in/public/pdf/Whatsnew/Final%20MTCTE%202017%20Procedure.pdf) — mirrored at `sources/telecom-electronics/tec-mtcte.pdf`, fetched 2026-09-24
- Full text: [`sources/telecom-electronics/tec-mtcte.md`](../../sources/telecom-electronics/tec-mtcte.md) (extracted, for search/offline reading)

## Notes

- MTCTE has been rolled out in phases by equipment category since 2018, with implementation dates repeatedly extended for later phases (wireless/IoT categories in particular) — the mirrored 2017 procedure document is the base framework; category-specific ER/GR/IR standards and phase notification dates are separate, frequently updated TEC publications not covered by this single mirror.
- `../bis-core/bis-crs.md` is an aspirational cross-link — the `bis-core/` docs folder is empty as of this research pass, so that page does not exist yet; the link is included per the task's cross-linking instruction and will resolve once BIS's CRS page is written.
- The dedicated MTCTE portal (`mtcte.tec.gov.in`) is where actual applications and category status are tracked; it wasn't mirrored here since the 2017 procedure PDF is the more durable "primary source" document for this orientation page.
