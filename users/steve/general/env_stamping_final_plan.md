# Replay-fidelity plan — final

Chosen design: **intra-board captures in board frame; hand-
origin always synthesizes at replay time.** No env stamping.

## What ships on the wire after this

| Action kind | Sender | Gesture path on wire? | `path_frame` |
|---|---|---|---|
| `split` / `merge_stack` / `move_stack` | Python | required (eased) | `"board"` |
| `split` / `merge_stack` / `move_stack` | Elm | required (captured, translated) | `"board"` |
| `merge_hand` / `place_hand` | Python | never | n/a |
| `merge_hand` / `place_hand` | Elm | never | n/a |
| `complete_turn` / `undo` | either | never | n/a |

Symmetric: both senders ship the same shapes for the same
action kinds. Server's `requiresGestureMetadata` already
accepts this (intra-board ⇒ path required; hand-origin ⇒ path
optional; we just stop using the option on the Elm side).

## Steps

1. **Elm captures intra-board drags in board frame.**
   - In `Main/Gesture.elm`, on `mousedown` when source is
     `FromBoardStack`: fire `Browser.Dom.getElement
     State.boardDomId` and stash the rect on `DragInfo` as
     `captureBoardRect`.
   - For each subsequent `MouseMove`, when
     `captureBoardRect` is present, subtract its x/y from the
     sample before appending to `gesturePath`.
   - Effect: by the time `handleMouseUp` runs, the path is in
     board-frame coords for intra-board drags.

2. **Elm drops captured paths for hand-origin drags at send.**
   - In `Main/Gesture.elm`'s `handleMouseUp`, when the
     resolved action is `MergeHand` or `PlaceHand`, pass
     `Nothing` to `Wire.sendAction` instead of the captured
     `fullPath`.
   - Effect: hand-origin Elm actions ship pathless, matching
     Python.

3. **Elm emits the correct `path_frame`.**
   - Change `encodeEnvelope` to take a `PathFrame` alongside
     the path, or widen `sendAction` to accept the frame. For
     intra-board drags, pass `BoardFrame`; the envelope now
     emits `"board"`.
   - Currently `encodeEnvelope` hard-codes `"viewport"` (from
     step 1 of the previous plan). Update to thread through.

4. **Replay-side: no code change.**
   - `prepareReplayStep` already branches correctly:
     faithful-path for intra-board (now always board-frame),
     async-DOM for hand-origin (now always pathless). The
     code written for the REPLAY_PYTHON_ACTIONS milestone
     handles this cleanly.

5. **Doc updates.**
   - `WIRE.md` § Gesture metadata: state that hand-origin
     actions NEVER ship a path; remove the implication that
     Elm-captured human hand-origin drags might.
   - `Main/Gesture.claude`: new rules for frame-at-capture +
     drop-at-send.
   - `Main/Wire.claude`: envelope encoder now takes frame.

## Verification

- `./ops/check` passes (Go + Elm + Python conformance).
- Manual: fresh DB → `auto_player.py` → replay. Every drag
  reads smoothly; no teleports; console shows
  `branch: "faithful (captured path)"` for intra-board and
  `branch: "hand-origin async DOM measure"` for hand-origin.
- Manual: fresh DB → human plays a hand through Elm, drags a
  hand card onto the board. Reload. Replay shows the
  hand-origin drag via DOM synthesis, not a captured path.

## What we're NOT doing

- No `window.innerWidth/Height` capture.
- No `devicePixelRatio` capture.
- No env-match decision in replay.
- No un-rip of `Space.synthesizedReplayAnimation`.
- No JS ports for environmental measurement.

All of those were on the table in v1/v2 and are now
unnecessary because the board's internal geometry is
invariant and hand-origin always synthesizes from live DOM.
