# `pcba-footprint-geometry-v1`

The board adapter emits UTF-8 JSON:

```json
{
  "schema": "pcba-footprint-geometry-v1",
  "components": [{
    "reference": "U1",
    "supplier_part": "C123",
    "x_mm": 10.0,
    "y_mm": 20.0,
    "side": "Top",
    "rotation_deg": 0,
    "pin1_instance": "pad-1",
    "pads": [
      {"instance": "pad-1", "name": "1", "x_mm": -1.0, "y_mm": 0.0}
    ]
  }]
}
```

## Canonical coordinate contract

- Board `x_mm`/`y_mm` use one declared board origin, millimetres, +X right and
  +Y down in top-board view. Every CPL row must use that same origin.
- `side` is exactly `Top` or `Bottom`. The CPL side must match; a side mismatch
  is a blocker, never a rotation correction.
- `rotation_deg` is normalized to `[0, 360)` and increases clockwise when the
  placed component is viewed from its assembly side. EDA and vendor adapters
  must convert their native zero angle and bottom-side convention into this
  canonical convention before auditing.
- Pad `x_mm`/`y_mm` values are physical local coordinates before the component
  placement rotation, in the same +X-right/+Y-down handedness. Bottom-side EDA
  data must be de-mirrored by the adapter; do not pass raw mirrored pad points.
- A local origin correction is rotated by the component's placement rotation
  before it is added to global board X/Y. The geometry audit performs this
  transform.

`instance` is unique even when multiple physical pads share one electrical
`name`. The board origin and every adapter conversion must be recorded with the
audit evidence; guessing an origin, handedness, or bottom convention is invalid.

Supplier geometry uses schema `pcba-supplier-package-geometry-v1` with a
`packages` array. Each package has `supplier_part`, `pin1_instance`, and the
same physical-pad shape in the canonical component-side local frame.

When electrical names are unique and identical, the audit may map by name. If a
name is duplicated, missing, or aliased, supply mapping JSON:

```json
{
  "packages": {
    "C123": {
      "pad_map": {
        "board-pad-instance": "supplier-pad-instance"
      },
      "approved_registration_angle_deg": 270,
      "land_pattern_rms_limit_mm": 0.5,
      "evidence": "Exact manufacturer package diagram and visual pin-1 review"
    }
  }
}
```

The map must cover every physical pad on both sides exactly once. Never average
duplicate electrical pad names into one center. `approved_registration_angle_deg`
resolves a geometrically symmetric orientation only when package/pin-1 evidence
exists. `land_pattern_rms_limit_mm` is a package-specific approved toe/heel or
row-span variance; it requires non-empty evidence and must never become a global
tolerance increase.
