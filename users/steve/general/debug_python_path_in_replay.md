# Debugging "does Elm honor Python's eased path at replay?"

The question: when an agent session ships a `move_stack` with a
20-sample cosine-eased path, and Steve clicks Instant Replay,
does Elm interpolate along those captured samples, or does it
fall back to its own linear synthesis?

There are five places this can go wrong, and the same five
places are where it can go right. I'll walk each one,
stating what I THINK the code should do and WHY before
showing the snippet.

The log line I added at the top of `prepareReplayStep` will
tell us which branch fires. But before we look at that, let's
check the reasoning by reading the code.

---

## 1. Python builds the path with ease and ships it

**What I think it does, and why:** `gesture_synth.synthesize`
should produce 20 samples where `t` steps uniformly but `x`/`y`
follow a quintic smootherstep ease curve. Uniform time + eased
position means Elm's linear-between-samples interpolation
produces slow-start / fast-middle / slow-end motion. The path
is stamped `path_frame: "board"` so Elm renders inside the
board div without a viewport translation.

```python
# games/lynrummy/python/gesture_synth.py
def synthesize(start, end, *, samples=20, path_frame="board",
               ms_per_pixel=None):
    pace = ms_per_pixel if ms_per_pixel is not None else DRAG_MS_PER_PIXEL
    duration_ms = max(100, _distance(start, end) * pace)
    t0_ms = time.time() * 1000
    path = []
    for i in range(samples):
        frac = i / (samples - 1)
        pos = _ease_in_out(frac)   # quintic: 6f^5 - 15f^4 + 10f^3
        path.append({
            "t": t0_ms + frac * duration_ms,
            "x": round(start[0] + (end[0] - start[0]) * pos),
            "y": round(start[1] + (end[1] - start[1]) * pos),
        })
    return {
        "path": path,
        "path_frame": path_frame,
        "pointer_type": "synthetic",
    }
```

`auto_player` calls this for intra-board actions and passes the
result in the envelope:

```python
# games/lynrummy/python/auto_player.py
endpoints = gesture_synth.drag_endpoints(prim, local)
meta = (gesture_synth.synthesize(*endpoints)
        if endpoints is not None else None)
wire = _to_wire_shape(prim, local)
c.send_action(session_id, wire, gesture_metadata=meta)
```

`ms_per_pixel` defaults to the module-level `DRAG_MS_PER_PIXEL
= 5`. For a 100 px in-game move that means 500 ms total —
which is short enough that the eased curve LOOKS close to
linear at normal watching speed. That's a real thing to keep
in mind: the ease is always there in the data, but our eye
notices it more over longer distances. This alone might
account for Steve's "I can't perceive acceleration" on in-game
moves.

---

## 2. The server persists gesture_metadata verbatim

**What I think it does, and why:** the Go POST handler should
accept the envelope, decode the `action` field strictly
(validating its shape), but pass `gesture_metadata` through as
an opaque JSON blob stored in the `lynrummy_elm_actions.gesture_metadata`
column. The server never inspects the path; Elm owns that.

I'll skip the Go snippet — I've verified this in the DB (seq
by seq the stored blob matches what Python sent). If the
bytes in the DB look right, bytes in transit were right.

```json
// one row from lynrummy_elm_actions.gesture_metadata:
{
  "path": [
    {"t": 1700000000050.0, "x": 136, "y": 40},
    {"t": 1700000000134.0, "x": 137, "y": 40},
    ...
    {"t": 1700000006131.0, "x": 566, "y": 470}
  ],
  "path_frame": "board",
  "pointer_type": "synthetic"
}
```

If this row is intact (it is), nothing further on the server
side matters for our question.

---

## 3. Elm decodes the ActionLogEntry with the path

**What I think it does, and why:** the `/actions` fetch
produces an `ActionLogBundle` with a list of `ActionLogEntry`.
Each entry has `action`, optional `gesturePath`, and a
`pathFrame`. Crucially: `pathFrame` decodes from the nested
`gesture_metadata.path_frame` field, defaulting to
`ViewportFrame` if absent. If this default kicks in for a
Python-originated move_stack, the BoardFrame-intended path
gets routed through the viewport-frame floater and the numbers
don't match the rendered board — so drag coords go to screen
pixels that don't line up with the stacks. That would be a
real bug to look for.

```elm
-- games/lynrummy/elm/src/Main/Wire.elm
actionLogEntryDecoder : Decoder ActionLogEntry
actionLogEntryDecoder =
    Decode.map3 ActionLogEntry
        (Decode.field "action" WA.decoder)
        (Decode.maybe
            (Decode.at [ "gesture_metadata", "path" ] (Decode.list gesturePointDecoder))
        )
        (Decode.oneOf
            [ Decode.at [ "gesture_metadata", "path_frame" ] pathFrameDecoder
            , Decode.succeed ViewportFrame
            ]
        )
```

**Suspicion hook:** if `pathFrameDecoder` chokes on the value
(unlikely — it accepts `"board" | "viewport"`), the `oneOf`
falls through to `ViewportFrame` silently. Same if the field
goes missing. Worth checking: does every row in the DB actually
have `path_frame: "board"`? (Python emits it; I'd bet yes.)

---

## 4. `prepareReplayStep` picks faithful over synthesis

**What I think it does, and why:** this is the load-bearing
decision point. If `maybePath` has `Just (p :: rest)`, Elm
builds an `AnimationInfo` using the captured path verbatim and
goes into Animating. Otherwise it tries DOM-measured hand-
origin synthesis or sync intra-board synthesis or
apply-immediate.

For a Python-originated in-game move_stack: the captured path
IS present, so we expect to land in the first branch.

```elm
-- games/lynrummy/elm/src/Main/Replay/Time.elm
case maybePath of
    Just (p :: rest) ->
        case Space.buildReplayAnimation action maybePath frame model nowMs of
            Just anim ->
                startAnimating anim

            Nothing ->
                applyImmediate

    _ ->
        ... hand-origin / sync-synth / applyImmediate ...
```

**Suspicion hook:** `buildReplayAnimation` itself can return
Nothing if `dragSourceForAction` fails to find the source
stack. Let's look at that.

```elm
-- games/lynrummy/elm/src/Main/Replay/Space.elm
buildReplayAnimation action maybePath frame model nowMs =
    let
        faithful path =
            case dragSourceForAction action model of
                Nothing ->
                    Nothing

                Just ( source, grabOffset ) ->
                    Just
                        { startMs = nowMs
                        , path = path
                        , source = source
                        , grabOffset = grabOffset
                        , pathFrame = frame
                        , pendingAction = action
                        }
    in
    case maybePath of
        Just (p :: rest) ->
            faithful (p :: rest)

        _ ->
            synthesizedReplayAnimation action model nowMs
```

`dragSourceForAction` is the real resolver — it has to pick
out the stack index the floater renders from:

```elm
dragSourceForAction action model =
    case action of
        WA.Split p ->
            boardStackSource p.stack model

        WA.MergeStack p ->
            boardStackSource p.source model

        WA.MoveStack p ->
            boardStackSource p.stack model

        WA.MergeHand p ->
            handCardSource p.handCard model

        ...
```

`boardStackSource` uses `findStackIndex` which runs
`CardStack.stacksEqual` against the current board. For the
replay to find the source correctly, the **current Model board
at replay time** must contain a stack that matches the
wire-sent CardStack via multiset + loc. If the replay state
got out of sync with the wire's historical state (e.g., a
previous action applied at a different-than-expected loc),
`findStackIndex` returns Nothing and `dragSourceForAction`
returns Nothing — and the path gets dropped.

**This is the most plausible culprit.** Python's prims may
reference a `target` whose contents or loc differ from what
the Elm reducer produced for the prior action. The path is
captured fine; it's just that the SOURCE of the drag
(`boardStackSource`) can't be resolved. When `buildReplayAnimation`
returns `Nothing`, we fall through to `applyImmediate` — which
looks exactly like "the drag didn't happen, the board just
jumped."

---

## 5. `interpPath` walks the captured samples

**What I think it does, and why:** given the captured path
and an elapsed time, return the interpolated cursor position.
Because each sample has an absolute `tMs`, elapsed-ms is added
to the FIRST sample's tMs to get the target timestamp.
`interpPathHelp` walks the list and interpolates linearly
between adjacent samples whose times bracket the target.

```elm
-- games/lynrummy/elm/src/Main/Replay/Space.elm
interpPath path elapsedMs =
    case path of
        [] -> { x = 0, y = 0 }
        first :: _ ->
            let targetTs = first.tMs + elapsedMs
            in interpPathHelp first path targetTs


interpPathHelp prev remaining targetTs =
    case remaining of
        [] -> { x = prev.x, y = prev.y }
        curr :: rest ->
            if curr.tMs >= targetTs then
                ... linearly interp prev → curr ...
            else
                interpPathHelp curr rest targetTs
```

This path is untouched by the CardStack refactor and has been
tested end to end. If the ease appears linear, it's likely NOT
here — the math is right, and linear-between-samples over 20
eased samples reads smoothly eased to the eye. But worth
noting that the duration measured in the log is
`last.tMs - first.tMs` from the captured path, which is also
what drives when Animating → Beating. If Steve wants to verify,
the browser console already shows `pathDurationMs` per step.

---

## 6. The floater renders at the right place

**What I think it does, and why:** the drag floater's
container is chosen by the DragInfo's `pathFrame`. BoardFrame
drags render as a DOM child of the board div with
`position: absolute` + board-frame coords. ViewportFrame drags
render at the top level with `position: fixed` + viewport
coords. The cursor coordinate passed to the renderer is
whatever `interpPath` produced from the captured path —
meaning it's in the SAME frame the captured path claimed.

```elm
-- games/lynrummy/elm/src/Main/View.elm
draggedOverlay model =
    case model.drag of
        Dragging info ->
            case info.pathFrame of
                ViewportFrame ->
                    renderDraggedFloater model info [ style "position" "fixed" ]

                BoardFrame ->
                    Html.text ""   -- rendered as a board-div child instead

        NotDragging ->
            Html.text ""
```

**Suspicion hook:** if the incoming path is tagged BoardFrame
but the source-stack resolution fails (section 4), the
floater for THIS action doesn't appear at all — `draggedOverlay`
becomes `Html.text ""` and there's no fallback. The card just
reappears at its new loc after `applyImmediate`. To the
viewer, that reads as "the board jumped" — not "the replay
ignored the eased path."

---

## My top two suspicions, ranked

1. **Source-stack lookup fails at replay time.** The captured
   CardStack's loc doesn't match what the replay-state board
   has. `dragSourceForAction → boardStackSource → findStackIndex`
   returns Nothing, `buildReplayAnimation` returns Nothing,
   `prepareReplayStep` falls through to `applyImmediate`. No
   animation. This is the one to verify first — the Debug.log
   I just added will tell us: if Python-originated in-game
   move_stacks log `branch: "applyImmediate (no path, no
   synthesis)"`, that's this bug. (Actually, the current
   branch classifier would still say "faithful" because it
   only looks at `maybePath`, not at whether
   `buildReplayAnimation` succeeded. I can sharpen the log to
   distinguish.)

2. **Short in-game moves compress the ease too tight.** The
   data is correct; the eye can't see it. Cosmetic openers at
   10 ms/px over 500+ px read obviously eased; in-game
   10–200 px moves at 5 ms/px are <1 s total and the ease is
   mathematically there but visually subtle. This is solvable
   by bumping the in-game pace to match or by running a much
   longer test drag during normal play.

The Debug.log I just added is coarse — it logs the branch
decision before `buildReplayAnimation` runs. If you see
`faithful` in the console but still no ease visible, we're in
case #2. If you see `applyImmediate` for Python-emitted
intra-board actions, we're in case #1, and my next pass
should tighten the log to distinguish those two subcases.

---

Reply inline on any paragraph or give the word and I'll
sharpen the log / fix whatever stands out.
