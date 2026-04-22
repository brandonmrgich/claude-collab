# Replay module boundaries — proposal

## The observation, sharpened

You're right that replay logic is scattered. Here's the current
reality of where replay-specific (or replay-adjacent) code
lives:

- **`LynRummy.Replay`** — a small pure module. One thing:
  `applyAction : WireAction -> State -> State`, the log reducer.
  Confusingly named: the reducer is used by BOTH live play AND
  replay. Its name implies a bigger scope than it has.

- **`Main.elm`** — a lot. `replayFrame`, `prepareReplayStep`,
  `buildReplayAnimation`, `synthesizedReplayAnimation`,
  `syntheticEndpoints`, `pointInLiveViewport`,
  `stackEdgeInLiveViewport`, `linearPath`, `pathDuration`,
  `interpPath`, `interpPathHelp`, `dragMsPerPixel`,
  `dragSourceForAction`, `boardStackSource`, `handCardSource`,
  `handCardIndex`, `animatedDragState`, `beatAfter`,
  `actionAndGestureAt`, plus Msg handlers for
  `ClickInstantReplay`, `ReplayFrame`, `HandCardRectReceived`,
  `ClickReplayPauseToggle`, and half of `BoardRectReceived`.

- **`Main/State.elm`** — `ReplayAnimation` sum type,
  `ReplayProgress` record, several `replay*` fields on Model.

- **`Main/Gesture.elm`** — records the `gesturePath` during a
  live drag (capture-side of replay's inputs).

- **`Main/Apply.elm`** — `applyWireAction`, used every replay
  step AND every live gesture completion.

- **`Main/View.elm`** — the `draggedOverlay` shared by live and
  replay drags.

So about 20 functions that are clearly replay-machinery live in
Main.elm, mixed with unrelated update logic. The name
`Replay.elm` is taken by a much narrower concern. The boundary
between replay and not-replay is invisible from any one file.

## What belongs together, naturally

Walking the replay data-flow end-to-end:

1. User clicks Instant Replay → model rewinds, state machine
   starts, DOM queries fire.
2. Every animation frame, the FSM ticks: PreRoll → NotAnimating
   → (Faithful/Synthesized/Apply-immediately) → Animating →
   Beating → NotAnimating (next step).
3. For synthesized drags, endpoints are resolved via DOM
   measurement (board rect live, hand card live), and a linear
   path is generated at dragMsPerPixel.
4. The pure reducer (`LynRummy.Replay.applyAction`) advances
   game state at the end of each animated step.
5. The drag floater (shared with live play) renders from the
   `Dragging` info the FSM puts into `model.drag`.

Two conceptually different responsibilities show up:

- **Clock work.** What step are we on? What phase? Has the
  beat elapsed? When does the next step fire? This is the FSM.
- **Spatial work.** Where does the drag start and end in the
  current viewport? What's the path through time? This is the
  synthesis pipeline (DOM measurement, endpoint resolution,
  linear path).

Everything else is either shared (reducer, Apply, View) or
capture-side (Gesture).

## Proposal

### Modules directly supporting replay

**`LynRummy.Replay`** — KEEP, but flag its narrow role in the
sidecar. It's the shared pure reducer. Nothing new moves in.
(Alternative: rename to `LynRummy.Reducer` to clear the name
`Replay` for a higher-level module. I lean against the rename
— the existing name has legitimate meaning and changing it
churns every consumer.)

**`Main.Replay.Clock`** (new) — the replay FSM and its clock-
driven Msg handlers. Houses:

- `replayFrame` (the tick dispatcher)
- `prepareReplayStep`
- `beatAfter`
- `actionAndGestureAt`
- Msg handlers for: `ClickInstantReplay`, `ReplayFrame`,
  `ClickReplayPauseToggle`
- (Imports the `ReplayAnimation` / `ReplayProgress` types from
  Main/State; those stay where they are because they're part
  of Model.)

**`Main.Replay.Synth`** (new) — the spatial synthesis
pipeline. Houses:

- `buildReplayAnimation`
- `synthesizedReplayAnimation`
- `syntheticEndpoints`
- `pointInLiveViewport`
- `stackEdgeInLiveViewport`
- `linearPath`, `pathDuration`, `interpPath`, `interpPathHelp`
- `dragMsPerPixel`
- `dragSourceForAction`, `boardStackSource`, `handCardSource`,
  `handCardIndex`
- `animatedDragState`
- Msg handlers for: `BoardRectReceived` (the replay branch),
  `HandCardRectReceived`

### What stays outside

- **`Main/Apply.elm`** — shared with live play. Not moving.
- **`Main/View.elm`** — drag overlay shared. Not moving.
- **`Main/Gesture.elm`** — capture-side, not replay-side.
  Lives with live-drag logic. Not moving.
- **`Main/State.elm`** — types stay in the Model's
  neighborhood. Not moving.
- **`Main.elm`** — shrinks. `update` still dispatches on Msg,
  but most replay-related branches delegate to
  `Main.Replay.Clock` / `Main.Replay.Synth` handlers.

### Smaller alternative: one `Main.Replay` module

If two modules feels like over-splitting for the amount of
code involved, collapse Clock + Synth into one
`Main.Replay` module with clearly-labeled sections. That's
fewer files but loses the "why" of the internal boundary.

## Naming

- `Main.Replay.Clock` + `Main.Replay.Synth` reads as "replay's
  two concerns." Clean namespacing.
- Single `Main.Replay` reads as "all replay machinery" — less
  granular but findable.

Both beat the current status quo where the central replay
module is tiny and the machinery sprawls across `Main.elm`.

## Binary

**A — Two modules.** `Main.Replay.Clock` + `Main.Replay.Synth`.
Internal boundary is a design claim (clock vs. spatial).

- Pro: each module is small; the clock/synth split matches
  how we've been thinking about replay (pacing vs. drawing).
- Con: more files; `Clock` and `Synth` will import each
  other and `Main.elm` has to import both.

**B — One module.** `Main.Replay` containing both concerns
with labeled sections.

- Pro: simpler; one place to grep; easier to land.
- Con: the module gets larger; the clock vs. synth seam is
  implicit rather than enforced.

I lean B for today, with a future split to A if `Main.Replay`
crosses a size threshold (~500 LOC) or if clock and synth
start to have genuinely independent reviewers.

Pick one.
