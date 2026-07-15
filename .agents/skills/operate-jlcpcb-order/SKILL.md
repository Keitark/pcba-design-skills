---
name: operate-jlcpcb-order
description: Operate and review a JLCPCB PCB/PCBA quote, optional physical-stencil request, or order using a frozen Gerber/drill, BOM, CPL, sourcing lock, constraints, and release manifest. Use for browser upload, board or stencil options, cost anomalies, coupons, component matching, substitutions, imported placement calibration, top/bottom preview inspection, cart preparation, or order records without silently accepting placement errors or payment.
---

# JLCPCB Order Operator

Treat JLCPCB as a second interpretation of the released design, not proof that
the design was understood. Use the released artifacts without redesigning them
inside the browser.

Keep four approvals separate:

1. Design-critical component match or substitution.
2. Assembly placement preview.
3. Final price and shipping address.
4. Payment.

One approval never implies another.

## Preflight

1. Obtain the immutable release manifest, Gerber/drill archive, BOM, CPL,
   sourcing lock, constraints, quantities, and review evidence. Read
   [references/release-input.md](references/release-input.md).
2. Require manifest `status: PASS`, every required release verification PASS,
   and zero unexplained disconnect/DRC/layout-check counts. Recompute every
   hash. Stop on a non-PASS manifest, failed/missing check, mixed revision, or
   hash mismatch; a successful upload cannot waive the release gate.
3. Stop if reference sets, DNP policy, dimensions, layers, assembly side, or
   controlled options disagree.
4. Record the current JLCPCB project/quote identity and capture the starting
   page without exposing private account data in public artifacts.

## Configure and price the PCB

Enter only released parameters. Do not infer a cheaper thickness, finish,
stackup, impedance option, edge treatment, panel method, or mechanical feature.
Capture warnings and the itemized quote.

Inspect whether trace/space, via diameter, mechanical drill, via type, layer
count, finish, thickness, stackup, impedance, or another threshold activates a
premium process. Use the live quote rather than a hardcoded universal value.
If a material surcharge is caused by geometry, stop and return measured feedback
to `$pcb-layout-review`; require a new verified release before re-uploading.

## Request an optional physical stencil

When the user wants a physical stencil shipped with or separately from the
PCB, read [references/stencil-ordering.md](references/stencil-ordering.md).
Distinguish it from JLCPCB's internal PCBA tooling. Verify that the requested
paste side exists in the frozen Gerber release.

Treat frame type, outer size, thickness, side, and fiducial handling as order
settings. Do not design a second stencil outline merely to request a custom
outer size: JLCPCB derives apertures from the released paste layer. Store the
project-specific request in the release manifest or order record, not as a
generic hardcoded default. A paste-data change requires a regenerated and
rehashed release.

## Match components

Match every line to the exact MPN or an explicitly approved alternate. Verify
package, pin count, value, tolerance, ratings, lifecycle, stock, MOQ, assembly
class, and total order cost. For unavailable or dominant-cost parts, read
[references/cost-aware-substitution.md](references/cost-aware-substitution.md).
Any electrical, package, footprint, tie, circuit, or layout change returns to
upstream design and release; never implement it as a browser-only substitution.

## Calibrate and review placement

Read [references/cpl-placement-review.md](references/cpl-placement-review.md).

1. Treat the first import as diagnostic. On each assembled side, select at
   least three separated, non-collinear asymmetric/polarized anchors with
   visible pin 1, including every known package-origin or zero-angle exception.
2. Reconcile every expected reference across source, submitted, and imported
   X/Y/side/rotation with declared units and tolerance. Use
   `scripts/reconcile_cpl_import.py` for the final submitted-to-imported table;
   any nonzero exit blocks the gate.
3. Audit physical package registration. Use `scripts/audit_cpl_geometry.py`
   with `pcba-footprint-geometry-v1`; duplicated electrical pad numbers, tabs,
   exposed pads, or supplier aliases require explicit physical-instance maps.
4. Inspect the actual top and bottom preview at useful zoom. Verify every part,
   not only suspicious ICs: each lead, terminal, shell anchor, and exposed tab
   overlaps its pad; body, pin 1, polarity, connector opening, and side are
   correct; nothing is shifted, mirrored, overlapping, or off-board.
5. Save full-board screenshots plus closeups for every critical or exceptional
   package and write `.pcba-workflow/assembly-placement-review.json`.

Browser X/Y/rotation edits are diagnostics only. If anything fails, record the
exact mismatch, correct the source CPL generator or package mapping, regenerate
the manifest, discard browser-only edits, re-upload, and repeat the entire
machine and visual review until unresolved count is zero.

## Final quote and order

Report PCB, assembly, parts, optional physical stencil, setup/extended charges,
shipping, tax, lead time, coupons, and total. Confirm the shipping address on
screen with the user.

Never approve placement, save a materially changed cart, or pay without the
applicable explicit user authorization. Payment authorization must refer to the
final displayed total. After an authorized order, preserve confirmation pages,
order numbers, final artifacts/hashes, component matches, placement evidence,
approved substitutions, price, and payment record.
