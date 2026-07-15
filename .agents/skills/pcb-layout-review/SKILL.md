---
name: pcb-layout-review
description: Audit, finish, or port PCB placement and routing using circuit intent, mechanical constraints, sourcing evidence, native DRC/connectivity, rendered views, and manufacturing feedback. Use before routing, after autorouting, before fabrication release, when adapting a proven board to another connector, enclosure, platform, or regional variant, or when reviewing layers, GND references, power distribution, decoupling, buses, controlled interfaces, RF keepouts, vias, cost-driving features, opens, or DRC findings.
---

# PCB Layout Reviewer

Use the humanized architecture and circuit constraints as placement policy, not
reference-number order or one global wire-length score. Read
[references/layout-review-checklist.md](references/layout-review-checklist.md)
and [references/proven-lessons.md](references/proven-lessons.md). Record the
gate with [references/layout-review-record.md](references/layout-review-record.md)
and select an evidence path from
[references/eda-adapters.md](references/eda-adapters.md).
For a derivative board, also read
[references/variant-porting.md](references/variant-porting.md).

## Establish truth

1. Read repository rules, native board/project sources, product brief,
   architecture, sourcing lock, circuit review, schematic/netlist, mechanics,
   enclosure, manufacturer constraints, and project-local layout lessons.
2. Identify the board source of truth and supported adapter. KiCad may use
   native CLI/API tooling; other EDA tools require equivalent native exports.
   Gerber or images alone permit review, not safe editable round-trip.
3. Record board/project hashes, layer stack, net classes, rules, placement,
   connectivity, raw DRC, classified DRC, via/drill histogram, and top/bottom
   renders before changing anything.
4. Distinguish hard constraints from negotiable targets. Never trade a short,
   new open, corrupted return path, unsupported pad, keepout violation, unsafe
   ownership state, or fabrication violation for a better score.

## Port a derivative variant

1. Freeze and hash the proven donor. Write an explicit delta for connector pin
   order and pitch, removed/added functions, power and audio paths, outline,
   mating datum, tongue, shell features, keepouts, and assembly constraints.
2. Treat the port as a constraint remap, not a crop, scale, or pin-count swap.
   Preserve the mating edge and add area only in a mechanically verified
   direction.
3. Reuse functional blocks, pin-bank orientation, local support relationships,
   and proven topology rather than absolute coordinates. Re-run architecture,
   mechanics, power/reference, and placement gates on the variant.
4. Geometry-lock every candidate. Integrate a coupled corridor donor as one
   atomic net set and prove every displaced or non-whitelisted net.
5. Diagnose an autorouter from its actual input/output: verify target pins,
   fixed versus movable scopes, target-route occurrences, and whether the
   minimum blocker was allowed to move.
6. Compare donor and variant with one orthographic physical scale and explicit
   dimensions. Independently fitted screenshots are not size evidence.

## Review in order

1. **Architecture placement:** align external connector pin order with
   functional corridors; place protection, translation, processing, memory,
   and outputs along real flow. Keep ownership and reset controls direct.
2. **Critical locality:** decoupling in the supply-pin escape path, tight
   regulator loops, correct crystals/feedback, connector protection, antenna
   edge/keepout, user access, thermal paths, and enclosure clearance.
3. **Layer and reference strategy:** choose layer count from bus density,
   routing channels, return paths, RF, controlled interfaces, power current,
   board size, and fabrication cost. A solid reference plane is normally more
   valuable than a dedicated low-current power plane; never assume four or six
   layers without analysis.
4. **Routing:** preserve continuous return paths, short critical controls,
   sensible topology, no stubs where forbidden, appropriate width/spacing,
   matched pairs/groups only when budgets require them, and legal transitions.
5. **Power and zones:** prove every rail and GND pad reaches the intended
   network. Same net name, overlapping fill, or zero pad-opens is not proof.
6. **Manufacturing:** compare trace/space, annulus, mechanical drill, via type,
   finish, thickness, impedance, and other cost thresholds with the current
   fabricator quote. Treat premium features as measured DFM feedback, not an
   automatic reason to weaken electrical constraints.
7. **Independent visual pass:** inspect clean 2D views, each signal layer, and
   fresh top/bottom 3D renders. Verify bodies, pin 1, polarity, connector
   overhang, pad support, antenna, outline, keepouts, silkscreen, and mechanics.
   Run silk-over-silk, silk-over-copper, and edge-clearance checks before the
   visual pass; preserve pin-1, polarity, and functional meaning, and leave
   unresolved dense labels at `USER_REVIEW`.

## Experiment safely

Use named candidate states and paired project files. Make one coherent change,
then measure raw disconnects, real DRC, power disconnects, layout gates, and
manufacturing defects. Record it with `scripts/score_experiment.py`; write new
project-specific lessons with `scripts/record_lesson.py`. Both default to
`.pcba-workflow/` and never mutate the installed skill.

Prefer high-scoring applicable methods. Do not repeat a negative method unless
conditions materially changed. An accepted candidate must be a measured net
improvement and may not add opens, real DRC, power disconnects, or verified
manufacturing defects. A successful route for one trapped net is not promotable
when its coupled donor set is incomplete or another lane becomes stranded.

In a recorded workflow, preserve hash-bound frames for initial placement,
placement freeze, meaningful accepted/rejected experiments, final routing,
individual signal layers, DRC/connectivity proof, and top/bottom 3D. Record
actual regressions when they teach something, but never introduce a defect for
the video. Keep every frame tied to the paired native board/project state.

## Release gate

Require zero unexplained raw disconnects, zero real DRC errors, zero power
disconnects, all project layout checks passing, verified planes/critical nets,
and visual/mechanical/silkscreen PASS in the same saved board/project state.
Document only narrow, evidence-backed waivers in
`.pcba-workflow/layout-review.json`. Hand the result to
`$release-pcba-fabrication`; supplier CPL interpretation remains a separate
`$operate-jlcpcb-order` gate.
