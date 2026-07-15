---
name: manage-pcba-program
description: Coordinate an evidence-gated electronic product and PCBA workflow from an idea, circuit description, schematic, netlist, PCB, BOM, or fabrication package through a reviewed order. Use for end-to-end requests, multi-stage hardware projects, workflow recovery, gate tracking, change invalidation, or deciding which specialist skill is required next.
---

# PCBA Program Manager

Coordinate specialists; do not replace them. Default shared artifacts to
`.pcba-workflow/` and use only `PASS`, `BLOCKED`, or `USER_REVIEW` for gate
status.

## Start

1. Read repository instructions and inventory available descriptions, native
   EDA sources, generators, netlists, renders, PCB files, BOM/CPL files,
   manufacturing packages, test evidence, and approvals.
2. Read [references/stage-gates.md](references/stage-gates.md).
3. Identify which specialist skills are installed. If a required specialist is
   absent, report its exact name and stop that stage; never improvise its
   approval.
4. Initialize or validate `.pcba-workflow/program-state.json` with
   `scripts/program_state.py`.
5. When the user requests a timelapse, tutorial, case study, or recorded demo,
   read [references/recorded-workflow.md](references/recorded-workflow.md) and
   initialize the hash-chained event log before the first design action.

## Route the work

- Description or incomplete requirements: `$plan-electronic-product`.
- BOM, MPN, stock, package, CAD, lifecycle, or substitution: `$qualify-pcba-sourcing`.
- Electrical architecture, ratings, power, reset, timing, safe state, or circuit
  correctness: `$design-and-review-circuit`.
- Label-heavy, visually floating, overlapping, or netlist-like schematic:
  `$schematic-humanizer` after capturing a connectivity baseline.
- Placement, routing, layers, planes, DRC, SI/PI, RF, or DFM:
  `$pcb-layout-review`.
- Gerber, drill, BOM, CPL, render, and revision-consistent release:
  `$release-pcba-fabrication`.
- Live JLCPCB quote, matching, preview, price, cart, or order:
  `$operate-jlcpcb-order`.

Run the humanizer early when presentation blocks review, but never use its
readability result as circuit approval. Require sourcing and circuit gates
before placement freeze.

## Manage evidence and change

- Record every artifact path, revision, SHA-256, gate status, unresolved risk,
  and approval evidence in program state.
- Invalidate downstream gates after controlled data changes. Use
  `scripts/program_state.py invalidate --change ...`; do not manually preserve
  a stale PASS.
- Keep substitution, assembly-placement, final-price, and payment approvals
  separate. Approval at one gate never implies another.
- Respect user intent: review-only requests do not authorize design edits,
  browser mutations, cart changes, or payments.
- In recorded mode, append events only after saved, inspectable checkpoints.
  Keep promotion-safe frames separate from private evidence, record authentic
  failures and corrections without staging fake defects, and validate hashes
  after every stage.
- Stop on contradictory revisions, missing source-of-truth data, unverifiable
  safety assumptions, or a specialist BLOCKED result.

## Finish

Report current gate, completed evidence, invalidated work, unresolved risks,
required user reviews, and the next specialist. A program is complete only
when the requested terminal gate is PASS and no required work remains.
For a pre-order demo, finish at `order_stop: USER_REVIEW`, validate and close
the recording, and do not cross its declared `stop_before` boundary.
