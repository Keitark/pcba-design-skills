# Schematic visual-audit record

Write UTF-8 JSON to `.pcba-workflow/schematic-visual-audit.json`:

```json
{
  "schema": "schematic-visual-audit-v1",
  "status": "PASS|BLOCKED|USER_REVIEW",
  "source_type": "",
  "adapter": "",
  "authoritative_sources": [],
  "baseline_connectivity": "",
  "final_connectivity": "",
  "connectivity_result": "PASS|BLOCKED|UNVERIFIABLE",
  "erc_or_lint": {"before": "", "after": ""},
  "protected_artifacts_unchanged": false,
  "sheets": [{"name": "", "full_page_render": "", "status": "PASS|BLOCKED"}],
  "dense_crops": [{"region": "", "render": "", "status": "PASS|BLOCKED"}],
  "remaining_limitations": [],
  "final_snapshot": ""
}
```

Every sheet and relevant dense crop needs a row. `UNVERIFIABLE` means the input
cannot supply trusted connectivity; it never means PASS.
