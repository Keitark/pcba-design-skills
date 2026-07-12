---
name: plan-electronic-product
description: Turn an electronic product idea, behavior description, reverse-engineering note, or incomplete circuit concept into a decision-ready engineering brief and architecture. Use before schematic design or audit when functions, operating states, power, interfaces, mechanics, production quantity, cost, or measurable requirements are missing or ambiguous.
---

# Electronic Product Planner

Produce `.pcba-workflow/product-brief.yaml` and
`.pcba-workflow/architecture.md`. Do not invent requirements merely to fill a
template.

## Workflow

1. Read repository instructions and all supplied descriptions, diagrams,
   existing circuits, firmware behavior, mechanics, and commercial constraints.
2. Use [references/intake-checklist.md](references/intake-checklist.md) to
   distinguish known facts, design targets, assumptions, and unresolved choices.
3. Copy [assets/product-brief.yaml](assets/product-brief.yaml) into the project
   state directory and complete only supported fields.
4. Describe system boundaries, actors, external connectors, major functional
   blocks, data and energy flow, operating modes, startup/shutdown/fault states,
   and ownership of shared resources in `architecture.md`.
5. For every interface, record voltage domains, direction, protocol or bus,
   nominal rate, edge-rate uncertainty, topology, cable/connector environment,
   and protection expectations.
6. Build a provisional power budget by rail and mode. Mark calculated or
   measured provenance; do not treat typical datasheet current as a guaranteed
   system maximum.
7. Record mechanical envelope, user-accessible parts, antenna/enclosure needs,
   programming and test access, expected quantity, target cost, lifecycle, and
   compliance context.
8. Ask the user only for unresolved choices that materially alter architecture
   or safety. Record the rest as explicit unknowns with an owner and next
   evidence needed.

## Gate

Set `status: PASS` only when downstream circuit and sourcing specialists can
work without guessing core behavior, power source, interfaces, physical limits,
or production intent. Use `USER_REVIEW` for a decision awaiting the owner and
`BLOCKED` for missing evidence that prevents safe progress.

Do not select exact components or approve a circuit in this skill. Hand exact
parts to `$qualify-pcba-sourcing` and electrical implementation to
`$design-and-review-circuit`.
