# Choose a skill

[日本語](choose-a-skill.ja.md) · [Back to README](../README.md)

Install only the specialist whose output you need. Install all eight when work
must continue across stage boundaries without losing evidence or invalidation
state.

| Your input or request | Start with | It can work alone when |
|---|---|---|
| An idea, feature description, or unclear requirements | `plan-electronic-product` | You only need a product brief and architecture. |
| A BOM, expensive part, unavailable part, or package question | `qualify-pcba-sourcing` | Circuit requirements and production quantity are available. |
| A schematic/netlist and “is this circuit right?” | `design-and-review-circuit` | Product behavior and exact component evidence are available. |
| A label-heavy, overlapping, or visually floating schematic | `schematic-humanizer` | You need presentation correction without electrical redesign. |
| A PCB placement, routed board, derivative connector/enclosure variant, layer question, opens, or DRC | `pcb-layout-review` | Circuit/layout constraints, target mechanics, and native board files are available. |
| Gerber, drill, BOM, CPL, or an order-ready archive | `release-pcba-fabrication` | Upstream design and layout gates already pass. |
| A released package and live JLCPCB quote/order page | `operate-jlcpcb-order` | The immutable release and user approval gates are available. |
| Several of the above or “take this from description to order” | `manage-pcba-program` plus all required leaves | The manager can see every required specialist. |

## Common combinations

- **Unreadable schematic only:** `schematic-humanizer`.
- **Unreadable and possibly wrong circuit:** `schematic-humanizer` plus
  `design-and-review-circuit`; keep their results separate.
- **Existing design before layout:** sourcing, circuit review, humanizer, then
  layout review.
- **Existing PCB before ordering:** layout review, fabrication release, then
  JLCPCB operator.
- **Complete new product:** manager plus all seven specialists.

The manager never substitutes for an uninstalled specialist. A leaf skill never
requires the manager, and writes its artifact directly under `.pcba-workflow/`.

## Do not skip these boundaries

- Readable schematic is not electrical approval.
- Exact MPN/package sourcing precedes placement freeze.
- Zero opens is not release approval without real DRC, power, and visual gates.
- Generated Gerber/BOM/CPL must share one revision.
- JLCPCB placement preview requires machine and visual review.
- Placement, final price, and payment are independent user approvals.
