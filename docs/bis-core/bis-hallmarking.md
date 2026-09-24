# BIS — Hallmarking

**Authority:** Bureau of Indian Standards (BIS), Ministry of Consumer Affairs
**Status:** Mandatory (gold); voluntary (silver)
**Established:** Scheme launched 2000; gold hallmarking made mandatory from June 2021
**Legal basis:** Bureau of Indian Standards Act, 2016, read with the BIS (Hallmarking) Regulations, 2018 (gazetted 14 June 2018) and subsequent amendments (2021, 2022, 2026)
**Marks issued:** BIS Hallmark (BIS logo + purity/fineness grade + six-digit alphanumeric HUID), applied via BIS-registered Assaying & Hallmarking Centres (AHCs)
**Source tier:** Statutory / regulatory text — the Act, Rules, Regulations, Order or gazette notification itself is mirrored, not just a page about it.

## Scope

Hallmarking certifies the *purity* of precious-metal jewellery, not the
jewellery's design or manufacture quality. India brought gold under
mandatory hallmarking in phases starting June 2021; a Hallmark Unique
Identification (HUID) number was introduced the same year as the third
component of every hallmark, alongside the BIS logo and the caratage/fineness
grade — it lets a buyer or inspector look up a specific piece's assaying
centre and jeweller via the BIS CARE app or website, turning a physical stamp
into a traceable database record. Expansion has continued by district:
by early 2026 gold hallmarking covered roughly 380 districts across six
phases. Silver hallmarking, by contrast, remains voluntary as of this
writing — a jeweller who chooses to hallmark silver must still issue a HUID
under the revised IS 2112:2025 standard, but nothing compels them to
hallmark silver at all. The testing and assaying work is done by BIS-registered
AHCs, which sit at the same "certification/testing bodies" layer of the
[four-layer model](../00-overview.md) as
[NABL-accredited labs](../apex-accreditation/nabl.md), though AHCs are
recognised directly by BIS under the Hallmarking Regulations rather than
accredited through NABL.

## Primary source

- [BIS (Hallmarking) Regulations, 2018 — Gazette notification](https://www.bis.gov.in/bs/BIS_Hallmarking_Regulations_2018_Gazette_notification.pdf) — mirrored at `sources/bis-core/bis-hallmarking.pdf`, fetched 2026-09-24
- Full text: [`sources/bis-core/bis-hallmarking.md`](../../sources/bis-core/bis-hallmarking.md) (extracted, for search/offline reading)

## Notes

- The mirrored PDF is a genuine 60-page Gazette scan (confirmed via
  `pdfinfo`: title "Microsoft Word - 3346gi", created 19 June 2018,
  Ghostscript-produced, 2,430,021 bytes matching the server's declared
  Content-Length) — it repeatedly truncated on ordinary `curl` downloads
  (bis.gov.in appears to throttle/reset large-file transfers) and needed
  resumed (`-C -`) downloads across two attempts to land intact; worth
  remembering for any other large PDF pulled from bis.gov.in in this repo.
- BIS has since amended these regulations multiple times (27 October 2021,
  4 March 2022, and again 14 September 2026 per BIS's own listing) — this
  mirror is the original 2018 regulation text, not a consolidated
  up-to-date version; treat the amendments as a to-do if a fully current
  text is ever needed.
- Silver-hallmarking-voluntary-but-HUID-required-if-done is a subtle,
  easy-to-misstate distinction — don't round it off to "silver is
  hallmarked" or "silver hallmarking is mandatory."
