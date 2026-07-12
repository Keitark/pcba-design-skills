# Prompt recipes

[日本語](prompts.ja.md) · [Back to README](../README.md)

Replace bracketed text. Codex uses `$skill-name`; Claude Code uses
`/skill-name`.

## Complete workflow

```text
Use $manage-pcba-program to inspect [project/path] from its product description,
schematic/netlist, BOM, and PCB. Initialize .pcba-workflow/program-state.json,
invoke only installed specialists, preserve source-of-truth rules, and stop at
every BLOCKED or USER_REVIEW gate. Do not place an order or pay.
```

## Product brief

```text
Use $plan-electronic-product to turn [description] into product-brief.yaml and
architecture.md. Separate SPEC, TARGET, ASSUMPTION, and TBD_MEASURE; ask only
about choices that materially change architecture or safety.
```

## Sourcing

```text
Use $qualify-pcba-sourcing to verify [BOM/path] for [quantity]. Use current
official datasheets and supplier evidence. Check exact MPN, physical pinout,
package, footprint, CAD/3D model, lifecycle, stock, MOQ, assembly class, total
cost, and approved substitutes. Do not change the design.
```

## Circuit audit

```text
Use $design-and-review-circuit to audit [schematic/netlist/path] against the
product brief and sourcing lock. Explain operation, component roles, power,
voltage domains, reset/boot states, bus ownership, timing, protection, and
layout constraints. Review only; do not edit yet.
```

## Schematic humanization

```text
Use $schematic-humanizer to reorganize [source/path] into visibly wired
functional sheets. Preserve canonical connectivity, use real buses, remove all
overlaps and apparent floating local logic, render every page and dense crop,
then compare final connectivity and ERC with the baseline.
```

## PCB layout

```text
Use $pcb-layout-review to audit [board/path] using the humanized architecture
and circuit constraints. Evaluate placement, decoupling, layer/reference
strategy, power, routing, RF/mechanics, raw connectivity, real DRC, drill cost,
and fresh 2D/3D renders. Score candidates; do not accept zero opens alone.
```

## Manufacturing release

```text
Use $release-pcba-fabrication to generate and verify one immutable [revision]
release. Export and independently inspect Gerber, drill, BOM, CPL, constraints,
assembly drawings, and renders; hash every artifact into release-manifest.json
and reject mixed revisions.
```

## JLCPCB review

```text
Use $operate-jlcpcb-order with [release-manifest/path]. Configure only released
options, inspect cost anomalies and every component match, calibrate and audit
CPL physical pad instances, visually inspect every top/bottom placement, and
stop for separate substitution, placement, final-price, and payment approvals.
```
