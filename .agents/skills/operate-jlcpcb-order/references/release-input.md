# Required release input

The operator accepts only `pcba-release-manifest-v1` with `status: PASS`.
Recompute every listed SHA-256 and require one revision across the native board
source/project, Gerber, drill, BOM, CPL, constraints, top/bottom renders,
circuit review, schematic connectivity/visual audit, layout review, and
sourcing lock.

Before any upload, require:

- `unexplained_raw_disconnects`, `real_drc_errors`, and
  `layout_check_failures` equal zero;
- circuit, layout, raw connectivity, power connectivity, visual/mechanical,
  DFM, sourcing freshness, and revision reconciliation equal `PASS`;
- positive board dimensions, layer count, thickness, PCB/assembly quantities,
  and declared finish and assembly side;
- any required design-critical substitution separately approved with evidence.

If the release specialist is installed, run its
`scripts/validate_release_manifest.py`. Otherwise apply this same contract
directly. Do not continue from `BLOCKED`, `USER_REVIEW`, a missing field, or a
hash/revision mismatch.
