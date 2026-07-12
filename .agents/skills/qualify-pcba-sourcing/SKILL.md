---
name: qualify-pcba-sourcing
description: Verify a PCBA BOM and proposed components before circuit or placement freeze, including exact manufacturer part numbers, pin semantics, packages, footprints, CAD and 3D models, lifecycle, live stock, MOQ, assembly class, price, and approved substitutes. Use for sourcing locks, unavailable or expensive parts, JLCPCB/LCSC matching, BOM risk, or cost-aware substitution decisions.
---

# PCBA Sourcing Qualifier

Create `.pcba-workflow/sourcing-lock.csv` from
[assets/sourcing-lock.csv](assets/sourcing-lock.csv). Stock and price are
time-sensitive: browse current primary manufacturer and supplier sources rather
than relying on model memory.

## Workflow

1. Read the product brief, architecture, schematic/netlist, BOM, layout, and
   production quantity. Derive the actual requirement before comparing parts.
2. For every populated reference, record the exact manufacturer, orderable MPN,
   supplier part number, package drawing, footprint, physical pin semantics,
   voltage/current/timing requirements, lifecycle, CAD, and 3D-model status.
3. Record supplier stock, timestamp, MOQ, price break used, Basic/Extended or
   equivalent assembly class, per-board and assembled quantities, order
   quantity, parts cost, setup/extended charges, and reconciled line/total
   assembled-order cost.
4. Treat memories, programmable devices, modules, regulators, translators,
   connectors, sensors, protection, and timing-critical parts as design-critical
   unless project evidence says otherwise.
5. For an alternate, read
   [references/substitution-gate.md](references/substitution-gate.md). Compare
   every physical pin and package dimension; similar family names or pin counts
   are not evidence. Record both the requested and selected MPN; a different
   selected MPN must be listed, explicitly approved, and tied to approval
   evidence in the sourcing lock.
6. Classify each line `PASS`, `BLOCKED`, or `USER_REVIEW`. A critical alternate
   always requires explicit design-owner approval.
7. Run `scripts/validate_sourcing_lock.py` with a suitable live-data age limit.

## Gate

Do not freeze the circuit or placement while a critical MPN, pinout, package,
footprint, CAD model, lifecycle, or current availability remains unresolved.
Any selected MPN/package change invalidates the circuit and all downstream
artifacts. A stock/price-only refresh invalidates sourcing and order approval;
it does not invalidate the circuit when the selected part is unchanged.

Report dated evidence, line and total cost, risk, substitution class, and every
unresolved item. Never silently change a released BOM or website match.
