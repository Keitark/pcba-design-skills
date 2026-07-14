# Proven reusable layout lessons

- Freeze placement from architecture and physical connector pin order before
  optimizing wire length or launching an autorouter.
- Route shared spines and scarce corridors early. Late common-bus routing can
  strand endpoints even when block placement is reasonable.
- Reserve routing capacity for power fanout before dense signal routing. Never
  treat different power nets as one category during collision checks.
- Avoid via-in-pad on fine-pitch parts unless the footprint and fabrication
  process explicitly support it. Use collision-checked offset fanout.
- A new through-via must be checked on every traversed layer and verified to
  retain its requested net after save and any selective zone refill.
- Refill only affected zones after local edits; global refill can change
  connectivity under rule or setting drift.
- Reject a zero-open candidate that adds clearance, short, power-island, return-
  path, or manufacturing defects. Connectivity and physical legality are
  independent metrics.
- Treat live quote surcharges as feedback. Resize only verified legal features,
  preserve density-critical exceptions, regenerate all checks and release
  artifacts, and compare the new quote.
- Supplier placement preview is not PCB placement validation. It is a separate
  post-release interpretation requiring machine and visual review.
- Treat a connector, enclosure, platform, or regional derivative as an
  electrical-and-mechanical constraint remap, not a cropped parent layout.
- Preserve the mating-edge datum, fingers, tongue, and insertion keepouts. Add
  board area only in a direction verified against the host and enclosure.
- Reuse functional topology and physical pin-bank orientation rather than
  absolute donor coordinates; repeat every placement and reference-path gate.
- Import coupled corridor repairs atomically. Never cherry-pick the headline
  net from a donor that also displaced neighboring lanes.
- When an autorouter omits a target route, inspect target pins, fixed/movable
  scopes, and result occurrences before changing normalization or retry flags.
- Compare derivative boards at one orthographic physical scale. Independently
  fitted renders cannot prove relative dimensions or mechanical fit.
- Close layout review with normalized silkscreen checks and both-side visual
  evidence. Preserve polarity/pin-1 meaning and classify intentional connector
  overhang separately from fabrication defects.
