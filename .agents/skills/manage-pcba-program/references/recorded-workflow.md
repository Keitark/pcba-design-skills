# Recorded workflow mode

Use this optional mode when the user wants an auditable process recording,
timelapse, case study, tutorial, or promotional demo. It does not weaken any
technical or approval gate.

## Start the recording

From the project root, initialize before the first design action:

```bash
python <skill-dir>/scripts/workflow_record.py init \
  --project <project-id> --stop-before final-submit
```

This creates `.pcba-workflow/events.jsonl`, a session manifest, and separate
directories for public frames, private evidence, and design snapshots. The
event stream is sequence-checked and hash-chained. Every referenced artifact is
SHA-256 checked again during validation and close.

## Record useful checkpoints

Add an event after a saved, inspectable state—not after every mouse movement:

```bash
python <skill-dir>/scripts/workflow_record.py add \
  --stage schematic_visual --action humanize-and-verify \
  --tool schematic-humanizer --gate-status PASS \
  --caption-en "Visible buses replace floating net labels" \
  --caption-ja "浮いたネットラベルを見えるバス配線に整理" \
  --input .pcba-workflow/schematic-before-connectivity.json \
  --output .pcba-workflow/schematic-after-connectivity.json \
  --frame .pcba-workflow/frames/004-schematic-humanized.png
```

Record at least these transitions when applicable:

1. Product brief and architecture block diagram.
2. Sourcing lock and design-critical part decisions.
3. Raw netlist-style schematic render plus connectivity baseline.
4. Humanized all-sheet render, dense-area crops, visual audit, and exact
   connectivity comparison.
5. Initial placement, reviewed placement, routing candidates, rejected
   experiments, final routing, signal layers, DRC, and top/bottom 3D.
6. Gerber, drill, BOM, CPL, render, and release-manifest checkpoints.
7. JLCPCB initial quote, component matching, diagnostic CPL preview, authentic
   correction loops, final placement preview, coupon comparison, compact
   stencil decision, and the page immediately before final submit.

Do not invent a placement, DRC, sourcing, or browser error for the video.
Capture real failures when they occur and record the verified correction.

## Public and private evidence

- `--frame` means promotion-safe media. Crop or redact account name, email,
  address, phone, browser URL/query, quote/order/batch identifiers, cookies,
  tokens, payment data, and unrelated tabs before recording it.
- `--private-evidence` preserves uncropped engineering/order proof but excludes
  it from the promotion frame list.
- Keep editable/native sources and machine reports as `--input` or `--output`.
- Visually inspect every public raster at full resolution. The recorder can
  detect common sensitive text in captions and filenames, but it cannot prove
  that pixels are private-data-free.

## Finish safely

For a demo that ends near ordering, record the reviewed pre-submit page with
`stage=order_stop` and `gate_status=USER_REVIEW`. Do not click the final submit
or payment action. `stop_before=final-submit` is a recording boundary, not an
authorization to cross it.

Validate throughout and close only after the media index is complete:

```bash
python <skill-dir>/scripts/workflow_record.py validate
python <skill-dir>/scripts/workflow_record.py close
```

A closed session fails validation if an event, frame, snapshot, or referenced
artifact later changes or disappears.
