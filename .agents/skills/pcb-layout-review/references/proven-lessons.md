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
