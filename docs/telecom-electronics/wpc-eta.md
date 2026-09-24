# WPC Wing — Equipment Type Approval (ETA)

**Authority:** Wireless Planning & Coordination (WPC) Wing, Department of Telecommunications, Ministry of Communications
**Status:** Mandatory
**Established:** 1952 (WPC Wing created as India's National Radio Regulatory Authority)
**Legal basis:** Indian Wireless Telegraphy Act, 1933 (Act No. 17 of 1933)
**Marks issued:** Equipment Type Approval (ETA) certificate/self-declaration; SACFA clearance (for spectrum/site coordination)

## Scope

The WPC Wing is India's national radio-spectrum regulator, created in 1952 under the Indian Wireless Telegraphy Act, 1933. Any equipment that transmits on radio frequency — Wi-Fi and Bluetooth devices, cordless phones, RFID readers, drones, walkie-talkies, cellular modules and much of modern consumer electronics — needs Equipment Type Approval before it can be imported, sold or used in India, confirming the device operates within permitted frequency bands and power limits and won't interfere with licensed spectrum users. For equipment operating in de-licensed bands under prescribed parameters, ETA is available on self-declaration through WPC's online system; equipment outside those parameters needs full testing and approval. WPC also runs the separate SACFA (Standing Advisory Committee on Frequency Allocation) clearance process, which coordinates frequency and site allocation for larger installations such as telecom towers and broadcast transmitters. ETA is the radio-frequency/spectrum-compliance counterpart to [TEC's MTCTE](tec-mtcte.md), which separately certifies the same telecom equipment against network-safety and interoperability requirements — a single device (e.g. a Wi-Fi router) can need both WPC ETA and TEC MTCTE certification before sale.

## Primary source

- [Equipment Type Approval (ETA)](https://eservices.dot.gov.in/equipment-type-approval-eta) (Department of Telecom eServices Portal) — mirrored at `sources/telecom-electronics/wpc-eta.html`, fetched 2026-09-24

## Notes

- The founding Act's own PDF, hosted at `dot.gov.in/sites/default/files/THE_INDIAN_WIRELESS_TELEGRAPHY_ACT_1933_1.pdf`, returned a 404 during this research despite appearing in search results as a live official link — DoT appears to have reorganised its file paths. The main `dot.gov.in` domain also now serves a JavaScript-rendered (Next.js) site that returns only an empty app shell to a non-browser fetch, so its HTML pages (including the WPC-specific `wpc.dot.gov.in` subdomain, which timed out entirely) could not be mirrored either. The eServices subdomain used here is the one DoT property that still serves real server-rendered content.
- If a stable copy of the 1933 Act text itself is needed later, `indiacode.nic.in`'s bitstream copy is the next thing to try (it timed out during this pass but is a plausible official mirror of the statute).
- Under India's evolving telecom law (the Telecommunications Act, 2023, which is gradually replacing the 1885 Telegraph Act framework and touches wireless licensing too), the WPC's ETA process may migrate to new statutory footing — this page reflects the 1933 Act as the still-current legal basis at time of fetch.
