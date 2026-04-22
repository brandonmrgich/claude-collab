# Loose ends at pause — 2026-04-20

Today's work was supposed to be "fix the teleport bug in replay."
It expanded outward through several invariant revelations, and
now we have a compounded ledger of open threads. Setting them
down in one place so the next session can pick any of them
without blind spots.

## The immediate cause of today's rabbit hole

We discovered late that *tricks must preserve the board-clean
invariant by construction*. Every primitive sequence a trick
emits must leave every stack classifiable as a complete set,
pure run, or red-black run. Python's emitters were violating
this in at least two tricks (peel_for_run's gap-pair, pair_peel's
wrong merge order). The same class of bug is almost certainly
latent in the Elm and Go implementations because they shared the
same mental model. We rewrote Python with the invariant baked in,
added an assertion-style harness (`test_hints_invariant.py`, 12
cases), and ripped the Go hint system entirely.

## What's fixed and committed

- Python `hints.py`: invariant-respecting emitters for all 6
  tricks.
- Python `test_hints_invariant.py`: 12/12 passing, loud dev-time
  gate.
- Go `games/lynrummy/tricks/` package: ripped, along with
  `TrickResultAction` wire type, `/hint` endpoint, `decompose.py`,
  `cross_check.py`, `client.get_hint`.
- `auto_player` runs end-to-end against the new emitters without
  referee rejection on trick emissions.

## Loose ends surfaced by today's discovery

**Elm hint emitters are untested for the invariant.**
`HintTest.elm` only checks priority ordering and rank
monotonicity. None of the ~2k LOC under `src/LynRummy/Tricks/`
has per-trick "apply primitives → board classifies clean"
coverage. Same hole Go had. Until we run the equivalent harness,
we should treat the Elm hints as probably-buggy in the same ways.

**The conformance-test bridge is one-sided.** `cmd/fixturegen`
still compiles, still emits Elm fixtures, but its Go output path
points to a directory we just deleted. The `referee.dsl`
scenarios (9 of them) used to cross-check Go's Referee against
Elm's Referee — now nothing forces them to agree. This is
enumerate-and-bridge with the bridge severed.

**Fixture sharing between Elm and Python is not yet built.**
Decided today: extend the DSL rather than introduce parallel
JSON. Not started. Cost is honest — new DSL vocabulary for trick
emission scenarios, a new generator target (Elm tests + Python
fixtures), and both sides' harnesses teach themselves to read it.

## The threads we parked BEFORE the hints detour

**Geometry is still broken.** Overlapping stacks observed in
today's replay browse. The `settle()` loop in `auto_player.py`
papers over some of it, but the underlying spatial placement
isn't producing non-overlapping locs. This was a known issue
before the invariant discovery; it hasn't moved.

**Telemetry synthesis never got written.** Drag capture and
replay work on the Elm side (2026-04-19). Python-originated
primitives write no `gesture_metadata`, so agent moves teleport
in replay — not because the wire is lossy, but because Python
hasn't filled in what the wire model gave it a slot for.
Synthesizing a linear drag from an average velocity is the parked
Phase 3.

**Agent stuck-state recovery.** When the agent's board reaches
a state where no trick fires, `auto_player` just ends the turn.
Undo-as-play — using undo as a rearrangement primitive for
exploration — was floated and parked.

**URL hashchange in the Elm client.** Minor annoyance, parked.

## The compounding pattern

These threads compound in a specific way: bugs in the hint
emitters produce invariant-violating boards, which produce
geometry violations, which get papered over by `settle()`, which
hides the fact that the agent's drag paths would have landed in
impossible positions anyway because the telemetry was never
synthesized. Fixing one layer surfaces the next. The discipline
is not fixing them in one pass — it's picking one, fixing it
properly, and letting the next one stand clearly visible.

## What not to do

Rush. The time already spent is sunk. The remaining hours are
better spent on the next *disciplined* step than on two hasty
ones.

## Natural next pulls, unsorted

- Mirror the Python invariant harness in Elm (either via shared
  DSL or via direct Elm-only test file as a stopgap).
- Extend DSL + fixturegen: new trick-emission scenario shape,
  emit both Python fixtures and Elm tests, re-wire the Go
  referee consumer for `referee.dsl`.
- Geometry: actual placement logic, not `settle`-papering.
- Telemetry synthesis: Python emits `gesture_metadata` for each
  primitive so the agent's drags replay at real speed.

None of these is urgent tonight. Each wants its own session with
a fresh head.
