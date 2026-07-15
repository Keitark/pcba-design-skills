# Physical stencil ordering

Use this reference only for an optional physical stencil shipped to the user.
It is separate from JLCPCB's internal assembly tooling.

## Release preflight

1. Read the board or production-panel bounding box from frozen manufacturing
   data.
2. Confirm which paste layers exist. Request only the assembled side unless a
   second side has a real use case.
3. Confirm that paste, copper, mask, outline, BOM, and CPL belong to the same
   revision and hashes.
4. Record frame type, outer size, thickness, side, fiducial choice, quantity,
   and remark in the release manifest or order record.

Do not create unrelated stencil artwork to set the shipped stencil's outer
size. JLCPCB generates apertures from the paste layer; outer size is an order
setting.

## Frame and outer size

For hand assembly and prototypes, prefer a frameless stencil unless the user
has a matching frame or fixture. Do not make a freehand stencil exactly the
board size. Start with roughly 15-25 mm working margin on each side, round up
to a convenient supported size, and keep the board inside the site's stated
valid engraving area. Increase the margin for a fixture, panel tabs, or easier
registration.

If JLCPCB panels the board, size and verify the stencil against the production
panel rather than one PCB. Do not hardcode a project example as a suite-wide
default.

## Thickness and aperture source

Select thickness from the smallest paste apertures, package mix, and assembly
method. A 0.12 mm frameless stencil is a common prototype starting point for
fine-pitch SMT, but it is not a universal rule. Confirm the current vendor
choices and the actual paste geometry.

When the paste layer is reviewed and no aperture modification is intended,
prefer an explicit remark such as `Follow the paste layer only`. Do not use
copper pads as a silent substitute for missing paste data.

## Browser evidence and gate

Capture and verify whether the stencil is ordered with the PCB or separately,
frame type, side, displayed outer size and valid area, thickness, fiducials,
quantity, price, shipping impact, and lead time. Include these in the final
price approval gate.

Any paste-data correction invalidates the release and requires regeneration,
new hashes, and a fresh upload.

## Official references

- [JLCPCB: How to order a stencil](https://jlcpcb.com/help/article/how-to-order-a-stencil)
- [JLCPCB: Instructions for stencil order](https://jlcpcb.com/help/article/instructions-for-stencil-order)
