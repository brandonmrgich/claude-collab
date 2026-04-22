# Pivot: layout-first geometry, then re-QA the autonomous game

## What changes

We stop trying to make Python's synthesized coordinates "match
whatever Elm happens to render" by reading or guessing. Instead,
we declare the viewport geometry as the specification and make
Elm's layout honor it. Absolute positioning inside a fixed-size
container, driven by shared constants.

Both sides consult the same spec. Python emits a drag endpoint
in viewport coords; Elm places the target stack at the same
viewport coords by construction. Agreement is enforced by the
layout itself, not by observation.

## Why this over "measure and hardcode"

Hardcoding current-measured values is a snapshot. Any change to
nav height, heading font, status bar copy, browser defaults
shifts the real layout out from under Python. The disagreement
is silent — the replay floater just starts landing nowhere and
nobody knows why.

Layout-first makes the numbers LOAD-BEARING. If you change the
layout, you change the constants. If you change the constants,
Python sees the new values next run. No silent drift.

## Why the focus shifts back to the autonomous game

Before this detour, the mission was: the Python agent plays
a full LynRummy game, and Steve watches it via the Elm UI
(live, or via Instant Replay). That's the actual product.
The "first move" scope was a reduction to isolate one bug.

Now that we have a path to fix the geometry properly, the
right next move is to validate it against the *real* mission
— play an entire autonomous game end-to-end, watch the replay
all the way through, and confirm:

- Every drag lands in the right place (geometry is honored).
- The replay is paced for human viewing (~1s between major
  events; drag duration ∝ distance at human velocity).
- Earlier moves — not just the very first one — all animate
  correctly. A move in turn 3 or turn 7 has the same fidelity
  as the first.

The "first move" isn't special; it was just the smallest
reproducer.

## What "re-QA earlier moves too" means

A full replay walks through N actions in sequence. Bugs can
hide anywhere: an emitter that produces funny coordinates in a
specific trick type, a between-action beat that's too short,
a drag duration that's visibly wrong for a particular
distance. Partial coverage (just watching turn 1) doesn't
catch these.

So the quality bar after the pivot is: Steve watches a full
autonomous game's replay and nothing jumps out as broken or
weird. That's the observable success criterion.

## What I expect to touch

- Elm's top-level layout (`Main/View.elm`): replace flex with
  absolute positioning inside a fixed container.
- A shared constants file (Python + Elm) defining the layout.
- `gesture_synth` (Python): use the shared constants;
  duration = distance * 80ms/pixel.
- Replay timings (Elm): pre-roll and beat at ~1s.

## Sequencing

1. Declare shared viewport constants.
2. Rewrite Elm layout to absolute-positioned from those
   constants. Visually confirm the app still looks right.
3. Update `gesture_synth` to use the shared constants and
   the new drag-velocity rule.
4. Bump PreRoll and between-action beat to ~1s.
5. Run a full autonomous game. Watch the replay. Flag
   anything that looks wrong.
6. Iterate on whatever (5) surfaces.

Steps 1–4 are mechanical. Step 5 is where we find out if the
mental model is correct. That's the QA loop.
