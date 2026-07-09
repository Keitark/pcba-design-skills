# Source adapters and evidence levels

[日本語](adapters.ja.md) · [Back to README](../README.md)

Schematic Humanizer applies one review method through format-specific adapters. An adapter is not necessarily a software plugin; it is the combination of source discovery, safe editing, rendering, and validation available for a format.

## Shared adaptation layer

Every adapter must answer four questions before work begins:

1. **What is authoritative?** Native design file, generator, database, netlist, or only a rendered artifact?
2. **What can be edited safely?** Native source, automation API, generator tables, interchange file, or nothing?
3. **What can be rendered reproducibly?** CLI, headless exporter, application automation, or manual export?
4. **What can be proven?** Exact connectivity, partial structural equality, or visual similarity only?

Use the strongest evidence supported by the source. Never upgrade a visually guided result into an “exact” result through wording alone.

## Evidence levels

| Level | Meaning | Minimum report |
|---|---|---|
| A — exact | Authoritative before/after connectivity can be exported and compared | Net/component counts, changed nets or pin memberships, ERC/compiler result, rendered-page review |
| B — structured | Editable structured source exists, but exact native comparison is unavailable | Parser/export checks, stable identifiers, warnings, rendered-page review, remaining uncertainty |
| C — visually guided | PDF/image is the only trustworthy input | Page list, traced functional paths, unreadable/ambiguous areas, no claim of connectivity preservation |

## KiCad

**Typical level: A. First-class support.**

- Prefer the project’s generator when it owns `.kicad_sch`; otherwise edit native source through supported tooling.
- Capture the netlist and ERC before editing.
- Use real wires, bus entries, hierarchical sheets, and labels according to KiCad semantics.
- Regenerate and export with the installed KiCad CLI when available.
- Compare component references, pin-to-net membership, net names, ERC, and rendered pages.
- Never hand-edit a generated `.kicad_sch` when repository instructions identify another source of truth.

## Altium Designer

**Typical level: A or B.**

- Prefer native automation/API workflows or an explicitly supported ASCII/interchange export.
- Save a copy and export a before/after netlist or project compile report.
- Preserve unique component IDs and sheet relationships.
- If only PDF and BOM exports are available, fall back to level C instead of claiming native preservation.

## EasyEDA

**Typical level: A or B, depending on edition and export access.**

- Identify Standard versus Pro and whether project JSON/native source is available.
- Use native exports for netlist and PDF/SVG evidence where possible.
- Avoid assuming that visual wire endpoints imply connectivity; verify junction semantics through export.
- Treat converted or downloaded projects as a new source and record conversion limitations.

## Autodesk EAGLE and Fusion Electronics

**Typical level: A or B.**

- EAGLE XML `.sch` can provide structured evidence; Fusion-managed designs may require application export.
- Preserve devicesets, gates, pin swaps, and supply-symbol semantics.
- Export a netlist or run the native electrical-rule check before and after.
- Do not rewrite library identifiers merely to improve appearance.

## gEDA and Lepton EDA

**Typical level: A or B.**

- Text schematic sources are inspectable, but net semantics depend on the installed toolchain and symbol libraries.
- Use `gnetlist`/Lepton equivalents and native checks when available.
- Preserve refdes, slotting, attributes, and net naming.
- Render with the matching library environment; missing symbols make visual validation incomplete.

## SPICE and standalone netlists

**Typical level: A for listed connectivity, B for schematic intent.**

- Treat the netlist as authoritative for nodes and device terminals.
- Build a functional diagram without inventing unlisted connections.
- Record subcircuit expansion, global nodes, aliases, and model-pin mappings.
- Compare the reconstructed connectivity back to the source netlist.
- Require human review for power intent, connector meaning, hidden pins, and functional grouping.

## PDF and image-only sources

**Level: C only.**

- Work from the highest-resolution original pages available.
- Trace visible wires, junction dots, labels, page references, and functional blocks.
- Mark cropped, blurred, occluded, or ambiguous connections.
- Produce annotations or a redraw plan; do not silently create an “authoritative” editable schematic.
- State clearly that connectivity preservation cannot be independently verified.

## Adding an adapter

An adapter contribution should document source-of-truth discovery, safe edit path, deterministic render path, connectivity checks, expected failure modes, and its maximum honest evidence level. See [CONTRIBUTING.md](../CONTRIBUTING.md).
