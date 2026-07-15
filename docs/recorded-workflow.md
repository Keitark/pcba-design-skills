# Record an end-to-end PCBA demo

Use the full suite with `$manage-pcba-program` when you want an engineering
workflow that can later become a timelapse, tutorial, or case study. Recording
is evidence-first: it saves meaningful states and their hashes rather than a
screen capture of every cursor movement.

## Copy-paste request

```text
Use $manage-pcba-program and enable recorded-workflow mode. Start from my
product description, record timestamped and hash-bound checkpoints for every
stage, preserve the raw netlist-style schematic before $schematic-humanizer,
and continue through PCB/PCBA review. Keep public frames separate from private
evidence and stop on the reviewed page immediately before final order submit.
Do not click submit or payment.
```

The manager creates `.pcba-workflow/events.jsonl`, `recording-session.json`,
and directories for public frames, private evidence, and design snapshots.
The log is sequence-checked and hash-chained; referenced artifacts are checked
again when the session closes.

## Recommended story beats

1. Product brief and architecture.
2. Design-critical sourcing decisions.
3. Netlist-style schematic “before.”
4. Humanized schematic “after” plus exact connectivity proof.
5. Initial placement, reviewed placement, routing progress, and real rejected
   experiments.
6. Final layers, DRC/connectivity evidence, and top/bottom 3D.
7. Gerber, drill, BOM, CPL, and release manifest.
8. JLCPCB quote, part matching, diagnostic CPL import, authentic source-side
   rotation/origin correction, and final placement preview.
9. Coupon comparison, compact frameless-stencil decision, final total, and the
   page immediately before submit.

Do not introduce a fake circuit, routing, placement, or ordering fault for the
video. A real failure and verified recovery is useful evidence; a staged defect
weakens the release.

## Privacy and irreversible actions

Only cropped or redacted media belongs in `.pcba-workflow/frames/`. Remove
account name, email, address, phone number, browser URL/query, order/quote IDs,
cookies/tokens, payment details, and unrelated tabs. Keep uncropped proof as
private evidence. Inspect every public image at full resolution; text scanning
cannot establish pixel-level privacy.

“Stop before final-submit” means exactly that. Placement approval, final-price
approval, final submit, and payment are separate actions. Reaching the button
does not authorize clicking it.

## Build the timelapse

After closing and validating the session, read `events.jsonl` in sequence and
use each event's public `frames`, English/Japanese caption, and artifact hashes
as the edit decision list. Keep private evidence out of the media export.
