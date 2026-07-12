---
name: pcb-layout-review
description: Audit or finish PCB placement and routing using circuit intent, mechanical constraints, sourcing evidence, native DRC/connectivity, rendered views, and manufacturing feedback. Use before routing, after autorouting, before fabrication release, or when reviewing layers, GND references, power distribution, decoupling, buses, controlled interfaces, RF keepouts, vias, cost-driving features, opens, or DRC findings.
---

# PCB Layout Reviewer

Use the humanized architecture and circuit constraints as placement policy, not
reference-number order or one global wire-length score. Read
[references/layout-review-checklist.md](references/layout-review-checklist.md)
and [references/proven-lessons.md](references/proven-lessons.md). Record the
gate with [references/layout-review-record.md](references/layout-review-record.md)
and select an evidence path from
[references/eda-adapters.md](references/eda-adapters.md).

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

## Experiment safely

Use named candidate states and paired project files. Make one coherent change,
then measure raw disconnects, real DRC, power disconnects, layout gates, and
manufacturing defects. Record it with `scripts/score_experiment.py`; write new
project-specific lessons with `scripts/record_lesson.py`. Both default to
`.pcba-workflow/` and never mutate the installed skill.

Prefer high-scoring applicable methods. Do not repeat a negative method unless
conditions materially changed. An accepted candidate must be a measured net
improvement and may not add opens, real DRC, power disconnects, or verified
manufacturing defects.

## Release gate

Require zero unexplained raw disconnects, zero real DRC errors, zero power
disconnects, all project layout checks passing, verified planes/critical nets,
and visual/mechanical PASS in the same saved board/project state. Document only
narrow, evidence-backed waivers in `.pcba-workflow/layout-review.json`. Hand the result to
`$release-pcba-fabrication`; supplier CPL interpretation remains a separate
`$operate-jlcpcb-order` gate.
