# Public asset privacy review

Reviewed at full resolution on 2026-07-12 before the `v1.0.0` release.

## Scope

- `assets/case-studies/nescart/schematic-before.png`
- `assets/case-studies/nescart/schematic-humanized.png`
- `assets/case-studies/nescart/schematic-before-after.gif`
- `assets/case-studies/nescart/operating-architecture.svg`
- `assets/case-studies/nescart/operating-architecture.png`
- `assets/case-studies/nescart/pcb-render.png`
- `assets/case-studies/nescart/jlc-placement-source.png`
- `assets/banner.png`

## Review result

The schematic, architecture, and PCB files contain only public design content.
The JLCPCB source was cropped to the board/placement table and visually checked
for account email, personal name, postal/ship-to address, phone number, quote or
order identifier, upload token, cookie, payment details, and browser URL; none
is visible. A metadata inspection found no EXIF or user/comment fields in the
published raster files. The workflow banner is generated only from the
reviewed assets.

The public placement crop intentionally retains vendor UI labels, component
references, supplier part numbers, and the project-generic memory-family text
because they are relevant engineering evidence, not account credentials.

Raster privacy cannot be proven by text scanning alone. Any replacement image
requires another full-resolution visual review and an update to this record
before release.
