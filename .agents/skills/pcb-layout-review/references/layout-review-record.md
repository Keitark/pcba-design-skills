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
  "stackup": [],
  "placement": {"logical": "BLOCKED", "visual_mechanical": "BLOCKED"},
  "connectivity": {"raw_disconnects": 0, "signal_splits": 0, "power_disconnects": 0},
  "drc": {"real_errors": 0, "waivers": []},
  "layout_checks": {"failures": 0, "warnings": []},
  "critical_nets": [],
  "via_drill_histogram": {},
  "manufacturing_findings": [],
  "silkscreen": {"status": "PASS|BLOCKED|USER_REVIEW", "findings": []},
  "renders": {"top": "", "bottom": "", "isometric": "", "layers": []},
  "unresolved": []
}
```

Do not write PASS unless every numeric and visual gate refers to the same saved
board/project state.
