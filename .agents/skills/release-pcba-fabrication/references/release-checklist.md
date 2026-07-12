# Manufacturing release checklist

## Revision integrity

- Native schematic/generator, PCB/project, sourcing lock, BOM, CPL generator,
  constraints, and derived files identify one revision.
- Source and output hashes are recorded after final generation.
- Any circuit, MPN/package, footprint, placement, routing, zone, BOM, or CPL
  change invalidates affected outputs and requires regeneration.

## Fabrication outputs

- Complete copper, mask, paste, silkscreen, outline, cutout, and required
  mechanical layers.
- Plated and non-plated drills, slots, drill map/report, and via/drill histogram.
- Dimensions, layer count, thickness, material, finish, copper weight, stackup,
  impedance intent, edge treatment, fingers/contacts, castellations, controlled
  depth, and panel/depanel instructions where applicable.
- Independent viewer check for missing/duplicate layers, outline gaps, inverted
  mask, clipped copper, text on pads, drill anomalies, and unintended features.

## Assembly outputs

- BOM has exact references, quantities, values, MPNs, supplier parts, package,
  DNP status, and approved-alternate policy.
- CPL has exact assembled reference set, declared units/origin, side, X/Y, and
  rotation convention. Every polarized/asymmetric package has pin-1 evidence.
- Assembly drawing and top/bottom renders agree with BOM/CPL and board source.
- Footprint physical pads, paste, exposed tabs, connector anchors, and package
  bodies have been visually checked.

## Gate evidence

- ERC/equivalent, raw connectivity, real DRC, power connectivity, layout checks,
  critical-net measurements, DFM, and visual/mechanical review.
- Every waiver is narrow, evidence-backed, owner-approved, and lists what it
  does not waive.
- Sourcing evidence is current enough for the intended order date.

## `PASS` manifest contract

The release builder/validator enforce these names so a standalone leaf user
does not have to infer them:

- artifact roles: `board_source`, `eda_project`, `gerber`, `drill`, `bom`,
  `cpl`, `constraints`, `render_top`, `render_bottom`, `circuit_review`,
  `schematic_connectivity`, `schematic_visual_audit`, `layout_review`, and
  `sourcing_lock`;
- constraints: positive `board_width_mm`, `board_height_mm`, `layer_count`,
  `thickness_mm`, `quantity_pcbs`, and `quantity_assembled` (assembled cannot
  exceed PCB quantity), plus nonempty `surface_finish` and `assembly_sides`;
- zero-valued checks: `unexplained_raw_disconnects`, `real_drc_errors`, and
  `layout_check_failures`;
- PASS checks: `circuit_gate`, `layout_gate`, `raw_connectivity`,
  `power_connectivity`, `visual_mechanical_review`, `dfm_review`,
  `sourcing_lock_current`, and `revision_reconciled`;
- boolean `design_critical_substitution_required`; when true, the separate
  substitution approval and evidence must be present.

Assembly placement, final-price, and payment approvals normally remain pending
at fabrication release. They are not transferred from one another.
