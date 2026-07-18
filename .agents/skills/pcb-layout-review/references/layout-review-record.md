# Layout review record

Write `.pcba-workflow/layout-review.json` with at least:

```json
{
  "schema": "pcb-layout-review-v1",
  "status": "PASS|BLOCKED|USER_REVIEW",
  "board_revision": "",
  "board_sha256": "",
  "project_sha256": "",
  "variant_port": {
    "donor_board_sha256": "",
    "delta_manifest": "",
    "mating_geometry": "PASS|BLOCKED|NOT_APPLICABLE",
    "same_scale_comparison": ""
  },
  "connector_stack": {
    "status": "PASS|BLOCKED|USER_REVIEW|NOT_APPLICABLE",
    "exact_mpn": "",
    "manufacturer_drawing": "",
    "footprint_geometry": "PASS|BLOCKED|NOT_APPLICABLE",
    "pad_support": "PASS|BLOCKED|NOT_APPLICABLE",
    "sample_measured": false,
    "mating_card_thickness_mm": null,
    "insertion_depth_mm": null,
    "retention": "PASS|BLOCKED|NOT_APPLICABLE",
    "dimension_basis": "MEASURED|DRAWING|INFERRED|TBD"
  },
  "mechanical_assembly": {
    "status": "PASS|BLOCKED|USER_REVIEW|NOT_APPLICABLE",
    "same_scale_render": "",
    "orthographic_dimension_view": "",
    "overall_height_mm": null,
    "overall_height_basis": "MEASURED|DRAWING|INFERRED|TBD",
    "proxies": []
  },
  "stackup": [],
  "placement": {"logical": "BLOCKED", "visual_mechanical": "BLOCKED"},
  "fanout": {"dense_connector_power_ground": "PASS|BLOCKED|NOT_APPLICABLE"},
  "connectivity": {"raw_disconnects": 0, "signal_splits": 0, "power_disconnects": 0},
  "drc": {"real_errors": 0, "waivers": []},
  "layout_checks": {"failures": 0, "warnings": []},
  "critical_nets": [],
  "via_drill_histogram": {},
  "manufacturing_findings": [],
  "silkscreen": {"status": "PASS|BLOCKED|USER_REVIEW", "findings": []},
  "renders": {"top": "", "bottom": "", "isometric": "", "layers": []},
  "experiment_baseline": {
    "frozen_input_sha256": "",
    "best_safe_candidate_sha256": ""
  },
  "unresolved": []
}
```

Do not write PASS unless every numeric and visual gate refers to the same saved
board/project state.
