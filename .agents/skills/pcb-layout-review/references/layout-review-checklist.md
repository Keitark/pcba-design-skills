# PCB layout review checklist

## Placement freeze

- For a derivative board, donor hashes and an explicit electrical/mechanical
  delta exist before placement reuse.
- Connector pitch, mating datum, fingers/tongue, insertion envelope, shell
  features, and allowed growth direction are independently verified.
- Exact connector MPN and drawing agree with body, contacts, locating features,
  pin 1, origin, footprint, mating card, insertion depth, and retention. When
  the sample is unavailable, its conservative envelope remains in review.
- Connector pin order and functional corridors match architecture.
- Protection, translators, buffers, memory, processing, and outputs do not
  backtrack unnecessarily.
- Every IC supply pin has appropriate local decoupling in its current path;
  bulk capacitors serve entries and load steps.
- Regulators, crystals, feedback, switching loops, ESD, terminations, pulls,
  reset/boot, and current sense are placed at their function.
- Antennas and RF modules follow the exact manufacturer's component and copper
  keepouts on every relevant layer.
- Large/critical components have verified MPN, package, footprint, pin 1, and
  licensed 3D model. Connectors and controls are mechanically accessible.
- Logical/constraint and visual/mechanical passes are recorded independently.
- Every dense connector/module power and GND pad has a legal dogbone, direct
  via, same-layer path to a stitched region, or approved process exception
  before signal routing begins.

## Routing and return paths

- Layer count and stackup are justified by signal density, reference needs,
  interface geometry, power, mechanics, and live fabrication capability.
- Critical signals never cross a plane split or void without a nearby return
  transition. Via counts and layer changes are controlled where meaningful.
- Differential pairs use the final stackup-derived geometry, continuous
  reference, defined tolerance, no stubs, and measured mismatch.
- Parallel buses use topology and skew budgets derived from timing, not visual
  symmetry. Avoid unnecessary meanders.
- Power widths, pours, neck-downs, vias, voltage drop, thermal rise, and source
  capability support the measured or conservatively allocated current.
- No copper, via, component, or mask feature violates outlines, cutouts,
  fingers, contacts, antennas, mounting, or enclosure keepouts.

## Connectivity and DRC

- Inspect every raw unconnected item. Treat signal and power representatives as
  real until independently proven otherwise.
- Zero pad opens is insufficient when track/track, track/via, or zone/plane
  components remain separated.
- Same-net zone fragments are each proven to reach the canonical rail; blanket
  stitches or island deletion are not accepted as connectivity proof.
- Classify intentional fabrication geometry narrowly; do not hide unrelated
  errors with broad waivers.
- DRC rules match the chosen manufacturing capability and quote, not values
  selected merely to make the report green.

## Manufacturing and visual evidence

- Export via/drill histogram and flag every feature below the current standard-
  cost threshold.
- Inspect assembly side, paste, silkscreen, fiducials, tooling/depanel needs,
  edge treatments, finish, thickness, and controlled options.
- Render top, bottom, isometric, and critical closeups after every footprint,
  model, rotation, or position change.
- Missing or offset bodies, wrong pin 1/polarity, unsupported connectors, or
  mechanical collisions block release even when copper DRC is clean.
- Intentional body or mating-mouth overhang is distinguished from unsupported
  copper pads, plated features, solder joints, or missing board substrate.
- Donor/variant size comparisons use one orthographic scale with explicit
  dimensions; independently fitted screenshots are rejected.
- Multi-board assemblies use real native renders or STEP at one scale plus an
  orthographic dimension view. Every dimension is classified as measured,
  drawing-derived, inferred, or TBD, and every proxy is disclosed.
- Stackup, outline, via-process, and routing experiments start from frozen
  inputs and are compared with the current best safe candidate. Board growth
  counts only when it creates a measurable corridor or clearance.
- Silk-over-silk, silk-over-copper, and edge-clearance findings are normalized
  and visually classified. Critical markings remain readable, and unresolved
  dense labels are `USER_REVIEW`, not silently deleted.
