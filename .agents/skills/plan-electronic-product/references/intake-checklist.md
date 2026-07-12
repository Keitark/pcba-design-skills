# Electronic-product intake checklist

## Product and environment

- User problem, success behavior, prohibited behavior, and intended operator.
- Indoor/outdoor, temperature, humidity, vibration, ingress, cable length, and
  expected lifetime.
- Prototype quantity, production quantity, target board and assembled cost,
  schedule, repairability, and component-lifecycle expectations.

## Electrical architecture

- Every power source, connector, nominal range, transient condition, source
  capability, reverse-polarity or back-power risk, and required isolation.
- Rails and modes: off, startup, programming, normal, sleep, reset, fault, and
  partial-power states.
- External and internal interfaces with direction, voltage domain, data rate,
  likely edge rate, topology, loading, hot-plug behavior, and protection.
- Shared buses or memories with one explicit owner per state and hardware-safe
  defaults before firmware starts.

## Physical architecture

- Board outline, mounting, enclosure, connector location, controls, indicators,
  antenna, thermal paths, keepouts, clearances, and assembly side limits.
- Programming, boundary/test access, debug connectors, measurement points, and
  replaceable or field-serviceable elements.

## Evidence classes

- `SPEC`: authoritative requirement, standard, official datasheet, or approved
  measured result.
- `TARGET`: project allocation chosen with stated margin.
- `ASSUMPTION`: temporary premise that must be confirmed before its gate.
- `TBD_MEASURE`: quantity that must be measured on the physical system.

Every unresolved item needs an owner, affected stage, and the evidence that
will close it.
