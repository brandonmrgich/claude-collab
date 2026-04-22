# Agent-plays-watchable: the axes of difficulty

## The mission, zoomed out

The Python player plays full games. The human watches them
through Elm's Instant Replay. The agent's games look like
games, not like wire logs. That's the product.

## The axes

**Legal move generation.** Python decides which primitives to
emit. The referee never rejects. Trick logic respects
CanExtract, invariants, priority order. Mostly solid.

**Physical execution discipline.** The board stays clean
throughout the trick: no stacks on stacks, no overlap, final
geometry honored. Yesterday's fix collapsed this to one
destination per trick. Working, with the "stay put vs move
first" rule.

**Wire fidelity.** The action log captures facts. Primitives
only — no compound wire types, no hints about how the receiver
should interpret events. Recently cleaned up.

**Shared geometry.** Python and Elm agree on where the board
lives in the viewport, at pinned coordinates declared in one
place both sides honor. Not yet done. Hand-card coordinates
are deliberately NOT in the agreement — those are Elm's
concern at replay time via DOM lookup.

**Replay synthesis.** Elm decides at replay time how to
animate each action. If it has a trustworthy gesture path that
obeys geometry, honor it (Faithful). If not, synthesize from
card identity + pinned board coords (Simulated). Not yet
implemented.

**Human-perceivable pacing.** Pre-roll ~1s, between-action
beat ~1s, drag duration proportional to distance at human
velocity (currently placeholder 80ms/px). Only partially
tuned.

**Testing discipline.** Invariants checked automatically on
every commit — geometry, stack-type, DSL conformance. Solid.

## How they interact

None of these axes is hard alone. The trouble is that a
weakness in one hides as a symptom in another. Broken geometry
looks like a pacing issue. A wire format that speculates makes
replay look buggy. A pre-roll that's too short makes a correct
drag look like a teleport. A faithful-looking path in the
wrong coordinate frame lands nowhere Steve can see, which
looks like "the drag doesn't work."

Debugging one axis in isolation keeps producing fixes that
don't hold because the actual cause was on a different axis.
Progress comes from making a thin vertical slice work across
ALL the axes at once, even if narrow, and expanding from there.

## Two plans

**Plan A — thinnest possible vertical slice.**

Scope: the opening move only (7H → 7-set). Hit every axis,
but only for that single action.

- Pin board-in-viewport geometry, declared in a shared source.
  Elm layout renders the board at that position.
- Python emits the `merge_hand` primitive with no hand-origin
  coord (Python stops pretending to know).
- Elm's replay, for that one action, runs Simulated
  synthesis: finds 7H in the current DOM, finds the pinned
  7-set target, animates a drag between them at 80ms/px,
  bracketed by a 1s pre-roll.
- Testable: fresh session, one primitive, hit Instant Replay,
  confirm Steve sees the expected flight.
- Expansion path: once the thin slice works, extend to more
  moves; nothing about the other axes changes, they just
  get exercised on more cases.

**Plan B — pacing first, on Faithful only.**

Scope: improve replay pacing on human-played sessions. No
Python agent in the loop. Tests the time axis independent of
the geometry axis.

- Steve plays a short game manually in Elm. Actions log
  with real Faithful gesture paths.
- Tune the replay state machine: pre-roll duration,
  between-action beat, and — for the Faithful path —
  whether drag duration is honored from the captured path
  or recomputed to 80ms/px. (Captured-path duration is the
  natural "Faithful" answer; recomputing would override
  the human's actual tempo, which may or may not be what
  Steve wants.)
- Testable: replay Steve's own recent game; confirm the
  timing feels right.
- Expansion path: once Faithful pacing is dialed in,
  Simulated synthesis inherits the same time constants.
  Then Plan A becomes easier.

Both are tractable in an afternoon. Plan A proves the
end-to-end for one move; Plan B proves the pacing in
isolation. They're complementary, but only one is a good next
step.

Pick one?
