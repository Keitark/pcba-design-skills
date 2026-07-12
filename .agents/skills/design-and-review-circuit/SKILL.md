---
name: design-and-review-circuit
description: Design, audit, or correct an electronic circuit from a product brief, native schematic, netlist, block diagram, or circuit description. Use for architecture and component-function review, power and logic-domain checks, reset and boot sequencing, bus ownership, ratings, timing, protection, safe states, component suitability, circuit bugs, or layout-facing electrical constraints.
---

# Circuit Design Reviewer

Treat readability and electrical correctness as separate gates. Default to
review-only unless the user asks to change the authoritative circuit source.

## Establish truth

1. Read repository instructions, product brief, architecture, sourcing lock,
   native schematic or generator, netlist, BOM, datasheets, firmware-visible
   behavior, and existing review notes.
2. Identify the electrical source of truth. When a generator owns the
   schematic, modify the generator rather than only generated files.
3. Capture ERC/lint, connectivity, and protected PCB/layout hashes before any
   authorized correction.
4. Use official manufacturer documents for exact orderable parts. Browse when
   datasheets, standards, availability, or current guidance can have changed.
5. Select the evidence path in
   [references/evidence-adapters.md](references/evidence-adapters.md); never
   claim an edit or verification stronger than the source permits.

## Audit

Read [references/circuit-audit-checklist.md](references/circuit-audit-checklist.md)
and produce `.pcba-workflow/circuit-review.md` from
[assets/circuit-review.md](assets/circuit-review.md).

- Explain operating principle and data/power/control flow in plain language.
- Build a component-by-component function table, power tree, voltage-domain
  table, operating-state table, and reset/boot/ownership sequence.
- Trace every external interface, power entry, driver, receiver, memory/control
  path, and hardware default. Check partial-power and firmware-not-running states.
- Verify ratings, logic thresholds, enable polarity, unused pins, static ties,
  decoupling, regulator stability/thermal margin, protection, clocks/timing, and
  connector semantics.
- Classify each finding as critical, major, minor, or information; distinguish
  proven defect, design risk, and unknown evidence.
- Record layout constraints using `[SPEC]`, `[TARGET]`, or `[TBD-MEASURE]`.
  Include data/edge rate, topology and stubs, return plane, skew intent, current
  allocation, placement, keepout, and authoritative source where applicable.

## Correct only when authorized

For each change, state the defect and evidence, edit the source of truth, render
the complete schematic, inspect it visually, rerun ERC/lint, compare canonical
connectivity, and confirm protected layout files remain unchanged. A deliberate
electrical change must appear explicitly in the connectivity delta and design
decision record; do not hide it inside presentation cleanup.

## Gate

Use `PASS` only when no critical/major issue or safety-relevant unknown remains
and the selected parts match the sourcing lock. Use `USER_REVIEW` for explicit
engineering decisions and `BLOCKED` for missing evidence or a failed check.

Hand drawing readability to `$schematic-humanizer`, part risk to
`$qualify-pcba-sourcing`, and placement/routing constraints to
`$pcb-layout-review`.
