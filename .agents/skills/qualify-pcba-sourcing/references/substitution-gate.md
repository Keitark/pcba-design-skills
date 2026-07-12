# Cost-aware substitution gate

## Establish the requirement

Record function, capacity actually used, supply and I/O voltages, logic
thresholds, current, power-up state, timing, loading, temperature, lifecycle,
programming, package, height, thermal needs, and mechanical keepouts. Do not
assume every capability of the fitted part is required, and do not relax a
requirement without owner approval.

## Use exact evidence

Use the official datasheet for the exact orderable suffix. Record manufacturer
status and live supplier stock, price break, MOQ, assembly class, timestamp, and
evidence URL. Optimize total assembled-order cost, not catalog unit price.

## Prove electrical and physical compatibility

- Compare every physical pin: role, direction, active level, voltage domain,
  internal pulls, unused-pin rule, and power-up behavior.
- Prove every existing static tie remains defined and safe. Check contention,
  enable polarity, leakage, retained bank or address selection, and all readers
  and writers.
- Compare exact package drawing, pitch, body, lead span, lead dimensions,
  exposed pads, height, pin 1, courtyard, and connector/contact direction.
- A matching manufacturer package diagram proves physical-package equivalence,
  not supplier CPL origin or zero-angle equivalence. Retain the visual placement
  gate.

## Classify

- `exact-drop-in`: required pin semantics and physical fit are identical.
- `bounded-design-change`: a reviewed local tie, passive, footprint, or firmware
  change is required.
- `redesign-required`: broader circuit, layout, power, timing, or mechanical
  work is required.
- `reject`: a required property, evidence, availability, or safety gate fails.

Any selected alternate changes the sourcing lock and BOM. Bounded or larger
design changes invalidate the circuit, layout, and manufacturing release.
