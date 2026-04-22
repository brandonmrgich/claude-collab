# Resume notes — Plan A, mid-slice

## Status

Committed as `bd35631` (WIP). Python side done & tested. Elm
side partially changed; **Elm compile not yet verified on
this commit.** Resume by running `ops/check` first.

## What's done

- Board pinned at viewport `(280, 100)` via
  `BoardGeometry.boardViewportLeft/Top`. Python has matching
  constants in `geometry.py`.
- `stackEdgeInViewport` helper in BoardGeometry gives the
  replay side a target point from a stack's loc + side.
- `Main/View.elm` top-level layout rewritten: board in an
  absolute-positioned div at the pinned coords; hand column
  in the 280-wide left gutter.
- New `LynRummy.HandLayout` module: `cardCenterInViewport`
  pure function that computes any hand card's viewport center
  from the hand's contents + card identity. Sidecar included.
- Python `gesture_synth`: merge_hand / place_hand return None
  (hand origin unknowable to Python). move_stack emits
  viewport coords. Duration scales with distance at
  `DRAG_MS_PER_PIXEL = 80`.
- `test_gesture_synth.py`: 5/5 updated and passing.

## What's left for Plan A

1. **Verify Elm compiles.** `(cd games/lynrummy/elm-port-docs
   && ./check.sh)`. If broken, first priority is fixing —
   likely the Main/View.elm layout rewrite has imports or
   syntax issues I didn't get to test.
2. **Rewrite `viewHand`** in `LynRummy.View.elm` to render
   each hand card at its `HandLayout.cardCenterInViewport`
   coords via `position: absolute`. This makes the pinned
   layout an actual rendering truth, not just a helper claim.
3. **Wire replay synthesis** in `Main.elm`. In
   `buildReplayAnimation`, when `maybePath` is `Nothing` for
   a `MergeHand` action:
   - origin = `HandLayout.cardCenterInViewport handCard
     hand.handCards`
   - target = `BoardGeometry.stackEdgeInViewport { loc, size }
     side`
   - synthesize a linear path with duration = distance ×
     80ms, ~12 samples
   - build the Animating state
4. **Pacing tweak.** `PreRoll` currently 1500ms; target is
   1000ms per the "order of a second between major events"
   guidance. Between-action beat already 1000ms.
5. **End-to-end test.** Fresh Python auto_player session with
   just one direct_play. Open the replay. Expect: 1s pre-roll
   showing initial board → the 7H animates from hand → lands
   on the 7-set.

## Open questions to raise when blocked

- For `move_stack` actions where Python DOES send viewport
  coords, does Elm currently honor them correctly on replay?
  Haven't exercised that path yet — might surface once
  multi-trick sessions run.
- The 7H's starting position in the pinned hand layout
  depends on `Card.allSuits` ordering (Heart first) and the
  other hand cards sharing its suit. Worth sanity-checking
  by inspecting the rendered hand before replay.

## Reminders for the next session

- Plan A is a THIN SLICE: one move, every axis. Don't scope-
  creep into fixing other tricks or tuning parameters until
  the 7H animation works end-to-end.
- "Record facts, decide later" — Elm's replay decides
  Faithful vs Simulated from path presence, not from a
  recorded tag. `maybePath == Nothing` → synthesize.
- Commit as soon as the slice is green end-to-end. Then Steve
  watches the replay and critiques before any expansion.

## File map

- `games/lynrummy/elm-port-docs/src/LynRummy/BoardGeometry.elm`
- `games/lynrummy/elm-port-docs/src/LynRummy/HandLayout.elm` *(new)*
- `games/lynrummy/elm-port-docs/src/LynRummy/View.elm` *(viewHand — needs rewrite)*
- `games/lynrummy/elm-port-docs/src/Main.elm` *(buildReplayAnimation — needs branching)*
- `games/lynrummy/elm-port-docs/src/Main/View.elm` *(pinned layout — done, verify compiles)*
- `tools/lynrummy_elm_player/geometry.py`
- `tools/lynrummy_elm_player/gesture_synth.py`
- `tools/lynrummy_elm_player/test_gesture_synth.py`
