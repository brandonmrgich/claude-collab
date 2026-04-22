# Memory consolidation — 2026-04-21 AM

## What I looked at

Three recent memories, written in rapid succession:

1. **Simplify before patching** (late 2026-04-20) — when you
   name an invariant, collapse the code toward it; don't add
   another layer that handles the currently-failing case.
2. **Own the whole system** (this morning) — I control the
   wire; the contract is mine to shape. At decision points:
   "enough data? if not, intrinsic, or wire-fixable?"
3. **Record facts, decide later** (this morning) — wire and
   model record what happened + provenance. Decisions live at
   execution time, never in the recording layer.

## What I noticed

These three aren't redundant, but they're not independent
either. They form one cluster that describes the right shape
for abstractions. Each answers a different question:

- **Own the whole system** answers "what am I allowed to
  change?" — license.
- **Record facts, decide later** answers "what should I put in
  the wire / model?" — restraint.
- **Simplify before patching** answers "how do I respond when
  Steve teaches me an invariant?" — response mode.

They're complementary: the license says you CAN reshape the
wire; the restraint says don't put more there than facts; the
response mode says when Steve points at a simple shape, use
the license and restraint to collapse toward it.

The natural failure mode (which I hit yesterday) is applying
one without the others. I could reshape the wire freely
(license) but put speculation on it (no restraint). I could
reshape with restraint but layer more code on top of the
existing shape instead of collapsing (wrong response mode).
All three have to fire together.

## What I did

Minimal consolidation — no merges, no rewrites. Just:

- Added an "architectural-shape cluster" section to each of
  the three memories, pointing to the other two with a
  one-line role summary (license / restraint / response mode).
  So future-Claude reading any one of them sees the cluster
  immediately.
- Demoted the pre-existing "Related" lists to "Also related"
  so the cluster is visually distinct from the general
  cross-links to older memories (`wire_model_not_lossy`,
  `inference_is_misplaced_work`, etc.).
- Left MEMORY.md order intact. The three entries are already
  adjacent in the index, which is enough.

## What I didn't do

- Didn't merge any of the three. Each has a distinct center
  of gravity; merging would lose nuance.
- Didn't reorganize MEMORY.md into thematic sections. The
  chronological-ish current order works, and restructuring
  the index is a larger project I don't want to spike on.
- Didn't edit the older related memories
  (`wire_model_not_lossy`, `inference_is_misplaced_work`,
  `no_phantom_concepts`, `bug_cost_slows_down`). They still
  make sense as they are; the cluster links out to them but
  doesn't rewrite them.

## Brief overview of the cluster, for reference

```
architectural-shape cluster
├── simplify_before_patching   — response mode
├── own_the_whole_system       — license
└── record_facts_decide_later  — restraint
```

Read together, they describe the move we should have made
yesterday and the one we're aiming to make today on the
replay geometry: when the shape feels wrong, reshape it (not
patch it), using the wire as a tool (not a constraint), and
putting only facts in the recording layer (never instructions).
