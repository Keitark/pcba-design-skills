# CPL placement review

## Import calibration

For each assembled side choose at least three separated, non-collinear anchors
with asymmetric geometry and visible pin 1. Include connectors/modules near
opposite extents and every package family with a known origin, angle,
duplicated-pad, tab, or exposed-pad exception. Record source, submitted, and
imported X/Y/side/rotation plus package identity and expected physical pose.

## Machine reconciliation

- Exact reference set; no missing, duplicate, unexpected, blank, or DNP rows.
- Declared units and tolerance; detect constant translation, axis swap, unit
  conversion, mirroring, whole-board rotation, and bottom-side convention.
- Package-specific rotation/origin mapping keyed by exact supplier part/package
  version and PCB footprint physical-pad signature.
- Physical pad instance counts and identities, not only unique electrical pin
  numbers or averaged centers. Explicitly map tabs and supplier aliases.
- Record best and second-best registration residual plus physical pin-1
  agreement. A symmetric span or body silhouette is not placement proof.

## Visual review

Inspect every placed body in top and bottom previews. At close zoom, require
every lead, terminal, shell anchor, thermal/exposed tab, and polarized contact
to overlap the intended copper/paste pad. Verify terminal count, body center,
pin 1, diode/LED/capacitor polarity, connector mouth, regulator tab, module
antenna orientation, switch actuator, board edge, cutouts, and neighboring
bodies.

Required evidence: full top and bottom previews, critical closeups, imported
table, exception list, final CPL SHA-256, zero unresolved rows, no manual browser
edits, and explicit user approval tied to the evidence.

Bind every machine report to SHA-256 for the board geometry, supplier geometry,
package mapping, submitted CPL, and imported table. Record submitted/imported
units and numeric tolerances. A PASS without these hashes and settings does not
identify the reviewed upload iteration.

Any CPL/BOM/footprint/position/rotation/side or website edit invalidates the
placement approval. Correct the source, regenerate, re-upload, and repeat every
row and visual check.

## Review record

Write `.pcba-workflow/assembly-placement-review.json` with schema
`assembly-placement-review-v1`, final CPL SHA-256, upload iteration, calibration
references, expected/imported counts, reconciliation CSV, unresolved count,
manual-browser-edits flag, global transform findings, top/bottom and critical
screenshots, per-reference results, exceptions, supplier project identity, and
`user_approval` (`PENDING`, `APPROVED`, or `REJECTED`). Machine and visual
status are independent `PASS` or `BLOCKED` fields. Placement cannot PASS when
unresolved count is nonzero or manual browser edits remain.
