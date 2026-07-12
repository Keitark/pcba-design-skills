---
name: release-pcba-fabrication
description: Build and verify a vendor-neutral PCB/PCBA manufacturing release from one frozen design revision. Use when generating or auditing Gerber, drill, IPC-2581/ODB++, BOM, CPL/pick-and-place, assembly drawings, constraints, renders, DFM evidence, hashes, or release manifests, and when preventing mixed-revision fabrication or assembly uploads.
---

# PCBA Fabrication Release

Release artifacts; do not redesign the circuit or layout inside this stage.
Read [references/release-checklist.md](references/release-checklist.md) and
[references/eda-release-adapters.md](references/eda-release-adapters.md).

## Preflight

1. Read repository rules, sourcing lock, circuit/layout gate results, approved
   waivers, native board/project files, fabrication constraints, quantities,
   and target manufacturer capabilities.
2. Freeze one named source revision and record board/project hashes. Stop if
   schematic, PCB, BOM, CPL source, sourcing lock, or constraints disagree.
3. Require circuit and layout gates to be PASS. Zero opens alone is not enough:
   raw connectivity, real DRC, power connectivity, planes, critical nets,
   mechanical and visual review must all be resolved.

## Generate

Use the authoritative EDA tool to export all applicable layers, solder mask,
paste, silkscreen, outline/cutouts, mechanical information, plated/non-plated
drill, drill map/report, BOM, CPL, assembly drawings, stackup/impedance notes,
and top/bottom renders. Preserve units, origin, side convention, rotation
convention, DNP policy, polarity, and pin-1 evidence.

Inspect the generated files in an independent Gerber/assembly viewer. Compare
outline and dimensions, layer count, copper/mask, drills, text, apertures,
keepouts, edge treatments, panel/depanel needs, and assembly side. Export a
via/drill histogram and identify every feature below the current standard-cost
process threshold.

## Manifest

Build `.pcba-workflow/release-manifest.json` with
`scripts/build_release_manifest.py`. Supply an explicit revision for every
artifact; the script rejects mixed revisions. Record:

- source and derived artifact SHA-256, size, role, and revision;
- board dimensions, layers, thickness, finish, stackup, controlled options,
  quantities, assembly side, and DNP policy;
- ERC, raw connectivity, classified DRC, power, layout, DFM, and visual results;
- approved waivers and the sourcing-lock hash/time;
- substitution, placement, final-price, and payment approval state.

Run `scripts/validate_release_manifest.py` after moving or packaging the
release. A missing file, hash drift, mixed revision, stale sourcing lock, or
failed required check blocks release.

## Handoff

Deliver an immutable release directory containing the manifest, manufacturing
files, assembly files, constraints, and review evidence. State the exact upload
Gerber/archive, BOM, and CPL. Hand live supplier interpretation to
`$operate-jlcpcb-order`; it must not silently repair this release.
