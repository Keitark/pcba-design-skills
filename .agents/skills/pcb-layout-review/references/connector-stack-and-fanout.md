# Connector stacks and dense fanout

Use these gates for card-edge sockets, board-to-board connectors, modules,
daughtercards, adapter PCBs, and any dense connector whose mechanics or power
escape can determine the layout.

## Connector maturity gate

Record each connector at the highest level supported by evidence:

1. **Electrical mapping:** contact count, pitch, pin numbering, contact side,
   and every assigned net are known.
2. **Orderable part:** an exact MPN and manufacturer drawing confirm the
   package, pin 1, origin, body, contacts, tabs, and locating features.
3. **Footprint geometry:** pads, holes, body, courtyard, mating mouth, board
   edge, assembly side, and 3D model agree with the drawing.
4. **Mating system:** mating-card thickness and edge geometry, insertion depth,
   retention, extraction clearance, and enclosure stack are defined.
5. **Physical proof:** an actual sample or controlled mechanical article has
   been measured and test-fitted.

If the exact part or sample is missing, keep a conservative body/courtyard and
mark the dependent mechanical gate `USER_REVIEW` or `BLOCKED`. Never shrink an
unmeasured envelope merely to clear DRC or make nearby placement fit.

Connector-body or mating-mouth overhang may be intentional. Copper pads,
plated support features, solder joints, and required substrate may not hang in
free space. Transform every physical pad instance and support feature against
the real board polygon; an axis-aligned rectangular board check is insufficient
for notches, cutouts, and irregular edges.

## Multi-board dimensional proof

- Render native PCB/STEP sources at one physical scale. Do not compare
  independently fitted screenshots.
- Include the main board, every adapter or daughtercard, the mating connector,
  and a card or enclosure proxy only when its status is explicit.
- Provide an orthographic dimension view in addition to a perspective beauty
  render. Record overall dimensions and insertion depth as `MEASURED`,
  `DRAWING`, `INFERRED`, or `TBD`.
- A geometry-only estimate or plausible 3D model is presentation evidence, not
  a release dimension. List every proxy, missing body, and unverified stack.

## Dense power and GND escape

Classify each power and GND pad before signal routing. It needs at least one of:

- a legal standard-process dogbone or direct via escape;
- a same-layer copper path to a connected, stitchable region; or
- a documented premium process explicitly accepted for cost and reliability.

If the legal escape collides with neighboring pads, drills, keepouts, or board
support, move the local part or revise the connector corridor before routing.
Do not assume a later plane fill or blanket via grid will repair an impossible
fanout.

Same-net zone fragments and region-level opens are real connectivity defects.
Connect each fragment to the canonical rail with individually clearance-proven
stitches or a verified topology change. Blanket island deletion, blind
stitching, and brute-force repair are not evidence.

## Comparative experiments

Freeze the same input state before changing outline, stackup, via process,
rules, or routing method. Compare every experiment with the current best safe
candidate, not only with the original unrouted board. Use the full vector:
opens, real DRC, power connectivity, return paths, connector mechanics,
manufacturing thresholds, cost, and visual gates.

Board growth is useful only when it creates a measurable local corridor or
mechanical clearance. Extra area that leaves the blocking geometry unchanged
is not an improvement.
