# Artifact contracts and stage gates

[日本語](artifact-contracts.ja.md) · [Back to README](../README.md)

All interoperable project state defaults to `.pcba-workflow/`. Artifact field
names and status values are English so independent agents and scripts can share
them without translation drift.

## Status

- `PASS`: the named gate and its required evidence passed.
- `BLOCKED`: missing, inconsistent, stale, or failed evidence prevents progress.
- `USER_REVIEW`: engineering evidence is ready but an explicit owner decision is
  required.

## Artifacts

| File | Owner | Required content |
|---|---|---|
| `program-state.json` | manager | Stage status/evidence, artifact paths/hashes, risks, approvals, invalidation log |
| `product-brief.yaml` | planner | Behavior, states, interfaces, power, mechanics, quantity, cost, unknowns |
| `architecture.md` | planner | Functional blocks, data/control/power flow, states, ownership |
| `sourcing-lock.csv` | sourcing | Requested and selected exact MPN, supplier/package/pinout/CAD/lifecycle/stock/cost, alternate approval evidence |
| `circuit-review.md` | circuit reviewer | Operating principle, component roles, power, timing, findings, constraints |
| `schematic-visual-audit.json` | humanizer | Adapter, rendered pages/crops, overlap and apparent-connectivity results |
| `layout-review.json` | layout reviewer | Placement, layers, critical nets, raw/classified DRC, power, visuals, DFM |
| `layout-experiments.jsonl` | layout reviewer | Measured candidate before/after metrics, score, decision, evidence |
| `release-manifest.json` | release | Revision, constraints, verification, approvals, every artifact SHA-256 |
| `assembly-placement-review.json` | order operator | Source CPL hash, import calibration, every-row reconciliation, visual results, user approval |

## Connectivity schema

`schematic-connectivity-v1` represents component identity and every named net's
exact `(reference, pin)` membership. Sort order is irrelevant; identity, net,
reference, and pin strings are exact. See the humanizer
[adapter reference](../.agents/skills/schematic-humanizer/references/adapters.md).

## Physical footprint schema

`pcba-footprint-geometry-v1` contains each component's reference, supplier part,
placement, side, rotation, pin-1 physical instance, and every physical pad with
a unique instance identifier. Multiple physical tabs may share one electrical
pad name but may never be averaged. See the JLCPCB skill's
[schema reference](../.agents/skills/operate-jlcpcb-order/references/pcba-footprint-geometry-v1.md).

## Invalidation

| Change | Repeat at least |
|---|---|
| Product behavior, power source, interface, or mechanics | product definition and all affected stages |
| Netlist or circuit | circuit, schematic visual proof, placement, routing, release, order |
| MPN or package | sourcing through order |
| Footprint or placement | placement through order |
| Routing or zone | routing, release, assembly placement, order |
| BOM | sourcing, release, assembly placement, order |
| CPL | release, assembly placement, order |
| Browser X/Y/rotation | source CPL correction, release, complete placement review, order |
| Stock or price only, same selected part | sourcing and final order approval |

## Approval separation

The program records `design_critical_substitution`, `assembly_placement`,
`final_price`, and `payment` as `PENDING`, `APPROVED`, or `REJECTED`. Approval
for one field cannot be copied to another. A manual browser placement edit makes
assembly placement ineligible for PASS until reproduced in the hashed CPL.
