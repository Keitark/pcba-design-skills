# Derivative PCB variant porting

Use this workflow when a proven board is adapted to another connector,
enclosure, platform, regional standard, or mechanically related product. The
goal is controlled reuse: retain verified circuit/layout knowledge without
assuming the parent geometry still satisfies the target.

## 1. Write the delta before layout

Freeze the donor PCB/project and record its hashes. Create a target manifest
covering:

- connector pin order, pitch, contact geometry, mating datum, and insertion
  envelope;
- exact orderable connector MPN, body, locating features, footprint origin,
  mating-card thickness, insertion depth, retention, and sample status;
- removed, added, or reassigned circuit functions and safe-state behavior;
- power, ground, audio, protection, programming, and user-interface changes;
- board outline, thickness, slots, bosses, shell limits, antenna regions, and
  keepouts;
- assembly side, panel/depanel assumptions, finish, edge treatment, and current
  fabrication thresholds.

Do not begin from a cropped or scaled board. A matching pin count does not
prove matching pin semantics, mechanics, return paths, or assembly support.

## 2. Preserve the mating edge

Treat contacts, tongue, bevel, insertion keepouts, and the host datum as hard
geometry. If the target needs more area, extend only in a direction proven by
the host and enclosure. Require a 1:1 fit gate for every nonstandard outline;
a clean 3D PCB render is not enclosure proof.

For a socket, module, or board-to-board connector, distinguish intentional
body/mouth overhang from pads or support features that lack substrate. Keep a
conservative courtyard while the exact body or physical sample is unverified.

## 3. Reuse intent, not coordinates

Carry over functional blocks, physical pin-bank direction, decoupler/support
relationships, routing topology, and verified local constraints. Re-run the
humanized signal-flow, source/destination pin-side, power/reference, RF,
mechanical, and sourcing reviews on the target. Optimize family-level routing
metrics only after those checks.

Geometry-lock each candidate: compare outlines, slots, fixed connectors,
keepouts, footprint transforms, pad nets, zones, and the paired project file.
Record every allowed transform or route change.

## 4. Route transactionally

Prefanout power before dense buses and route scarce shared spines early. When a
trapped route requires neighboring lanes to move, preserve the smallest
coherent donor and integrate every changed net atomically. Prove all displaced
nets and compare non-whitelisted route fingerprints before promotion.

When an autorouter produces no target route, inspect the job rather than
guessing from its headline warning:

- confirm the target net and pins in the exported input;
- count fixed and movable wiring scopes;
- inspect the result for target-net route occurrences;
- verify that the minimum physical blocker was allowed to move.

Retry only after the movable window or board conditions materially change.
Board growth counts only if the new geometry creates a measurable corridor;
extra area elsewhere does not resolve a local connector fanout blocker.

## 5. Prove visuals and release together

Render donor and target with the same orthographic camera and physical scale;
show explicit dimensions. Inspect both sides, each signal layer, critical model
paths, connector support, antenna, contacts, tongue, slots, and enclosure
limits. Then run normalized silk-over-silk, silk-over-copper, and edge-clearance
checks. Preserve pin-1, polarity, and functional labels; classify intentional
connector-body overhang separately and leave unresolved labels at
`USER_REVIEW`.

For multi-board products, add every adapter, daughtercard, and mating connector
to a one-scale assembly view and provide a separate orthographic dimension
view. Mark dimensions as measured, drawing-derived, inferred, or TBD, and label
all proxy bodies. A plausible exploded render is not a mechanical release gate.

Release still requires one saved board/project state with zero unexplained raw
disconnects, zero real DRC, zero power disconnects, passing layout gates,
verified reference paths, and visual/mechanical/silkscreen approval.

## nescart NES-to-Famicom evidence

The nescart derivative changed a 72-pin NES cartridge into a 60-pin Famicom
variant. It removed the CIC subsystem, added the required Famicom audio loop,
preserved the target mating edge, and extended only away from the fingers. The
final nominal envelopes were about 99.7 x 63.9 mm for NES and 90.0 x 66.8 mm
for Famicom at 1.2 mm thickness.

The useful evidence was procedural, not the specific six-layer answer:

- all directional bus devices were re-audited by physical pin bank;
- one trapped address route required a four-net corridor exchange imported as
  one atomic set;
- one failed router job had the correct target pins but 2,153 fixed scopes,
  zero movable route scopes, and no target route in the result;
- the promoted board simultaneously reached raw disconnects 0, real DRC 0,
  power disconnects 0, layout failures 0, no tongue/tip copper, no signals on
  its plane layers, and 439 standard 0.50/0.30 mm vias;
- a conservative silkscreen candidate reduced 58 normalized findings to six
  without changing electrical gates; the remaining dense labels and intentional
  connector overhang stayed in review instead of being deleted blindly.

These values describe one CC BY-SA-attributed case study, not defaults. See the
repository's English/Japanese nescart case study and `ASSET-LICENSES.md` for
provenance; this workflow text remains MIT with the rest of the skill.
