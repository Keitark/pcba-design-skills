# Case study: nescart Rev A

[日本語](case-study-nescart.ja.md) · [Back to README](../README.md)

nescart is a WiFi development cartridge for the front-loader NES. An ESP32-S3
receives a homebrew ROM, holds the console in reset through CIC behavior, loads
SRAM, verifies it, then releases the console to read the SRAM as a cartridge.
This real project supplied the evidence behind the eight skills.

> The values below describe one board. They are case-study evidence, not
> universal PCB defaults.

## 1. From netlist-shaped page to traceable circuit

The original electrically connected page relied heavily on isolated labels.
The connector, ESP32, USB, SRAM, buffers, glue logic, reset, pulls, and power
looked visually unrelated.

| Before | Humanized |
|---|---|
| ![Original label-heavy nescart schematic](../assets/case-studies/nescart/schematic-before.png) | ![Humanized nescart schematic](../assets/case-studies/nescart/schematic-humanized.png) |

The correction introduced functional sheets, explicit local wires, real buses,
left-to-right flow, connector orientation, and whitespace. Every page and dense
crop was rendered, including a specific overlap correction where a bus passed
under a component. Connectivity was compared independently; visual success did
not become circuit approval.

## 2. Circuit and layout-facing architecture

The audit documented component roles, ROM-loading sequence, bus ownership,
hardware-safe defaults, power tree, reset gate, memory controls, and the
distinction between WiFi ROM delivery and USB service/flashing. Layout notes
used `[SPEC]`, `[TARGET]`, and `[TBD-MEASURE]` for bus cadence, current budgets,
reference planes, skew, antenna keepout, and manufacturer guidance.

![nescart operating architecture](../assets/case-studies/nescart/operating-architecture.svg)

This humanized architecture—not reference order or one HPWL score—became the
placement policy for console-side buffers, SRAM, MCU-side buffers, loader,
power/USB, and CIC/reset corridors.

## 3. Placement, layers, routing, and honest completion

The team compared four- and six-layer strategies, dedicated/combined power
planes, routing-channel count, return paths, and cost. A continuous GND
reference remained important even though the buses were not extremely fast and
the ESP32 radio was a module. The final released board used a justified
six-layer construction; the skill intentionally does not copy that answer to
other boards.

![Real nescart PCB render](../assets/case-studies/nescart/pcb-render.png)

Named routing experiments recorded before/after opens, real DRC, power
disconnects, layout checks, manufacturing defects, replayability, and evidence.
Successful changes scored positively; timeouts/no-change scored negatively;
physical regressions cost more than connectivity wins. This exposed a crucial
failure mode: one candidate reached zero opens while creating many real
clearance errors. Final completion required zero raw disconnects, zero real DRC,
zero signal splits, zero power disconnects, and zero automated layout failures
in the same saved board/project state.

## 4. Porting the design from NES to Famicom

The mature 72-pin NES design was reused to build a 60-pin Famicom-native
variant. This was not a cropped board: the connector pitch/order, audio loop,
removed CIC subsystem, shell geometry, tongue, and usable area were written as
an explicit electrical/mechanical delta first. The mating edge remained fixed;
extra height was added only away from the fingers after a separate fit gate was
defined.

Placement reused functional blocks and physical pin-bank direction rather than
absolute coordinates. A trapped address route required four neighboring nets
to be imported atomically, and an apparent autorouter normalization failure was
traced instead to 2,153 fixed routing scopes and zero movable scopes. Same-scale
renders showed the nominal NES and Famicom envelopes as approximately
99.7 x 63.9 mm and 90.0 x 66.8 mm respectively, both at 1.2 mm thickness.

The promoted Famicom board simultaneously reached zero raw disconnects, real
DRC errors, power disconnects, and layout failures. Silkscreen was then audited
as a separate release surface: a conservative candidate reduced 58 normalized
findings to six without changing the electrical gates, while dense labels and
intentional connector overhang remained explicit review items.

The reusable workflow is in the
[`pcb-layout-review` variant-porting reference](../.agents/skills/pcb-layout-review/references/variant-porting.md).
Its measured layer count, via geometry, and dimensions remain case-study facts,
not defaults for other derivative boards.

## 5. Fabrication cost and sourcing feedback

A live quote showed that small mechanical drills activated a costly capability
tier. The board was not globally weakened: only clearance-verified vias were
standardized, necessary dense escapes would have remained exceptions, and the
complete connectivity/DRC/plane/drill/Gerber/release cycle was repeated.

Sourcing also exposed that a memory choice and package information needed
review before ordering. The reusable rule is to lock exact MPN, pin semantics,
package drawing, footprint, CAD/3D model, availability, and total order impact
before placement freeze—not after routing.

## 6. CPL registration and visual placement

The supplier preview revealed both position and rotation interpretation issues.
SRAMs, logic packages, the ESP32 module, and regulator were inspected at useful
zoom. The workflow learned not to average duplicated electrical pad numbers:
physical terminals, exposed tabs, and supplier aliases must be mapped
individually. Browser adjustments were treated as diagnostics; corrections were
reproduced in the source CPL, hashed, re-uploaded, and fully rechecked.

![Sanitized JLCPCB placement-review source](../assets/case-studies/nescart/jlc-placement-source.png)

The final reviewed import reconciled the complete populated reference set and
used separate user approvals for component selection, placement, final price,
and payment. The order was prepared for five PCBs with three assembled boards;
payment was not implied by cart preparation.

## Reusable outcome

The session produced the current humanizer, circuit-review, layout, release,
and JLCPCB gates; multi-EDA adapter contracts; project-local experiment learning;
and the rule that every improvement must be backed by the surface it can
actually prove.

## License

These real nescart-derived images and diagrams are CC BY-SA 4.0. See
[asset attribution](../ASSET-LICENSES.md). Code and original skill
documentation remain MIT.
