---
name: TOP_DOWN_SWEEP — breadth-first doc audit from a named root
description: Protocol for keeping top-level docs current — start at the root, walk links breadth-first, prune aggressively, let the code be truth while docs hedge honestly
type: feedback
originSessionId: 5a09deb5-8bd3-411c-844c-e6aa9a9b0122
---
**TOP_DOWN_SWEEP** (Steve, coined 2026-04-21). A named process
for keeping the MOST-READ docs current. Dual to bottom-up
CODE_CLEANUP: cleanup notices drift while doing other work;
TOP_DOWN_SWEEP starts from the canonical account and pulls
drift toward the surface.

## Why top-down

Top-level docs (ARCHITECTURE.md, BRIDGES.md, READMEs) are the
ones people trust most and read first — so drift there is the
most expensive. Walking from the top guarantees we catch things
in the order they matter.

Staleness spreads outward from the code; sweeping back inward
from the doc root is the efficient pincer.

## Protocol

1. **Pick a root doc.** Steve names it: "TOP_DOWN_SWEEP from
   games/lynrummy/ARCHITECTURE.md".
2. **Read the root in full.** Resist the urge to skim.
3. **Truth-test every factual claim** against the code:
   - Files/paths the doc links or names: do they exist?
   - APIs / Msg variants / schema tables / memory pointers
     cited: do they exist?
   - "X does Y" behavioral claims: does grep + spot-read
     confirm?
4. **Update the doc per the truth rules (below).**
5. **Walk links breadth-first.** Don't rabbit-hole into the
   first subsystem — survey width first, depth second.
6. **Prune when obviously fresh.** A doc that was edited
   today, or a claim that's self-evidently current, doesn't
   need re-verification.
7. **Flag bigger drifts as their own sweep.** If a linked
   doc has substantial drift (>~20 min to fix), write it
   down as "flagged for next sweep from here" and keep this
   one scoped. Don't let one sweep metastasize.

## Truth-test rules

- **The code is the source of truth, in a stronger sense than
  docs.** When they disagree, the doc is wrong.
- **A doc is load-bearing when it's honest about what it
  claims.** Hedge labels keep a doc true even when the code
  hasn't caught up:
  - **PLANNED** — intended, not built.
  - **UNCERTAIN** — not sure which way this lands yet.
  - Explicit "current state (date):" followed by what actually
    happens today.
- **Harmful drift = address immediately.** A doc that names
  nonexistent APIs or sends readers at dead paths isn't hedged
  — it's wrong. Fix in the sweep, don't flag.
- **Prose vs. identifier distinction still applies.** See
  `feedback_lyn_rummy_spacing.md` for the soft version:
  prose names ("Lyn Rummy") lean toward the human form,
  module/package/URL tokens stay as identifiers.

## Complement to CODE_CLEANUP

CODE_CLEANUP is bottom-up: notice a zombie helper or stale
sidecar while doing other work, fix it. TOP_DOWN_SWEEP is the
dual. Run both periodically; neither alone keeps the tree in
shape.

## First run (2026-04-21)

Root: `games/lynrummy/ARCHITECTURE.md`. Outcomes:

- Hedged "stamp tells replay which case" claim with PLANNED +
  explicit current-state note.
- Retired stale parking bullets about READMEs that now exist.
- BRIDGES.md gained the DSL conformance harness and memory-
  index entries in "Full bridges."
- Flagged `elm/USER_FLOWS.md` for its own sweep (attributes
  flow steps to Msg variants that don't exist).

Total: one sweep, four files updated, one bigger drift
queued. ≈ 30 min.
