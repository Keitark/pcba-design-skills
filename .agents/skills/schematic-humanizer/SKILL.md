---
name: schematic-humanizer
description: Reorganize label-heavy or netlist-like electronic schematics into human-readable functional diagrams with visible local wiring while preserving proven connectivity. Use for schematic readability correction, overlapping wires or symbols, visually floating connectors or support logic, functional-sheet restructuring, bus presentation, layout annotations, or multi-EDA handoff across KiCad, Altium, EasyEDA, EAGLE/Fusion, gEDA/Lepton, SPICE/netlist, and PDF/image sources.
---

# Schematic Humanizer

Turn an electrically connected but label-heavy schematic into a diagram a human
can trace. Preserve the circuit unless the user separately authorizes an
electrical change. Readability is not electrical approval.

## Establish the adapter

Before editing, read [references/adapters.md](references/adapters.md) and define:

1. Native source of truth, generator, libraries, project rules, and protected
   PCB/layout artifacts.
2. Baseline connectivity exporter/parser and its limitations.
3. Normalization to `schematic-connectivity-v1`: component identity, named net,
   and every `(reference, pin)` membership.
4. Supported edit path: generator, native API, text format, or controlled GUI.
5. Renderer and ERC/lint path.
6. Repeatable post-edit export and exact comparison.

Never call an unverified conversion equivalent. If only PDF/image evidence
exists, preserve it, create a companion native drawing, and label electrical
equivalence unverified.

Read the mandatory
[visual audit checklist](references/visual-audit-checklist.md) before editing.
Record its result with
[references/visual-audit-record.md](references/visual-audit-record.md).
When layout guidance is requested or placement-sensitive buses, clocks, power,
controlled interfaces, RF, or manufacturer rules are obvious, also read
[layout handoff annotations](references/layout-handoff-annotations.md).

## Workflow

1. **Capture baseline.** Read repository instructions. Export canonical
   connectivity and ERC/lint. Record hashes or a clean diff for protected
   layout files. If a generator owns the schematic, edit the generator. In a
   recorded workflow, also render and preserve the intentionally netlist-style
   whole schematic before changing its presentation; this is the authoritative
   “before” frame, not a reconstructed mockup.
2. **Plan functional sheets.** Group by real flow: connector/input → protection
   or translation → processing/control → memory/output. Separate power/reset
   and repetitive decoupling when useful. Prefer left-to-right flow, power at
   top, and ground at bottom.
3. **Show local relationships.** Draw native wires for nearby connectors, USB,
   oscillators, MCU support, memory controls, translators, glue, reset/boot,
   pulls, LEDs, and power chains. Rotate connectors toward the served circuit.
   Use real buses and entries for repeated address/data groups. Reserve labels
   mainly for cross-sheet or genuinely long connections.
4. **Enforce drawing hygiene.** Never route a wire or bus under a symbol,
   reference, value, title, note, or unrelated label. Avoid wire-through-pin
   ambiguity, unintended junctions, four-way crossings, stacked labels, long
   loops, and crowded bus entries. Use orthogonal grid-aligned routes, visible
   junctions, consistent entry pitch, and sufficient whitespace.
5. **Render before annotation.** Export every sheet to PDF and readable PNG.
   Inspect whole pages, page edges, and dense crops around large ICs, modules,
   connectors, memories, buses, reset, and power. Fix every overlap, apparent
   floating function, reversed flow, clipped item, and avoidable label chain.
6. **Add justified layout guidance.** Mark each statement `[SPEC]`, `[TARGET]`,
   or `[TBD-MEASURE]`. Capture rate plus edge-rate caveat, topology/stubs,
   reference plane, skew intent, current allocation, trace/via intent,
   placement/keepout, and authoritative guidance. Keep calculations and full
   URLs in a companion document.
7. **Render again.** Reinspect every page and changed dense crop after comments.
   Reject any annotation hiding a wire, bus, pin, reference, value, heading, or
   dominant signal path.
8. **Prove preservation.** Export and normalize final connectivity with the
   same adapter. Run `python scripts/compare_connectivity.py before after`;
   KiCad XML netlists are accepted directly. Require exact identities, net
   names, and ref/pin memberships, no new ERC/lint findings, and no protected
   layout changes.

In recorded mode, append separate checkpoints for the raw schematic,
humanized all-sheet render, dense-area visual audit, and connectivity proof.
Use promotion-safe frames and keep machine reports as hashed outputs. Do not
create a fake overlap or electrical fault merely to make the transformation
look dramatic.

## Completion report

Report adapter, authoritative files, baseline/final counts, comparison result,
ERC/lint before and after, protected-file proof, every rendered page/crop
inspected, remaining limitations, and the final snapshot. Write
`.pcba-workflow/schematic-visual-audit.json`. Route circuit-design
findings to `$design-and-review-circuit` rather than mixing them into visual
approval.

For ready-to-copy user requests, read
[references/prompt-template.md](references/prompt-template.md).
