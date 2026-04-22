# Env-stamping plan — v2 (post-disconnect-correction)

You caught me assuming a choice where there isn't one. Noting
each of your comments and re-scoping.

## What I missed

**The board is invariant in shape, even when the viewport drifts.**
The 800×600 play surface has fixed internal geometry regardless
of window resize, DPI change, or monitor swap. Only the board's
*position in the viewport* can change. So a path recorded in
board frame is faithful for the life of the game, period — no
env check needed, ever.

That changes the whole framing. My A/B question was wrong.
Capturing intra-board Elm drags in board frame isn't "option A" —
it's just correct. And synthesis-as-fallback isn't needed for
intra-board, because faithful IS always available to us.

## Revised plan

1. **Symmetric emission.** ✓ Done in `a9e8af1` — Elm now emits
   `path_frame` + `pointer_type` alongside the path.

2. **Elm translates intra-board samples to board frame at
   capture.** On `mousedown`, measure the board rect
   (`Browser.Dom.getElement`), stash on `DragInfo`. For every
   MouseMove whose drag source is `FromBoardStack`, subtract
   the rect's x/y from the sample before appending. At emit
   time, tag the path `path_frame: "board"`. Hand-origin drags
   (`FromHandCard`) stay viewport-framed and tagged accordingly.

3. **Env capture via JS port** (per your "go with the JS port"
   — and the broader principle you stated: JS ports are
   first-class). On `mousedown` for hand-origin drags, read
   `window.innerWidth/Height` + `devicePixelRatio` and stash on
   `DragInfo.env`. Ship as `gesture_metadata.env: {vw, vh, dpr}`.
   Not needed for intra-board — those paths are env-durable.

4. **Env measurement at replay-start** also via JS port (same
   reasoning). Alongside the existing board-rect Task, read
   current viewport + DPR into `model.replayEnv`.

5. **Replay decision rule.**
   - `path_frame: "board"` → faithful, always.
   - `path_frame: "viewport"` + env matches → faithful.
   - `path_frame: "viewport"` + env drifted → apply
     immediately with an extended beat. No synthesis fallback.

## On the rip of `synthesizedReplayAnimation`

I think the rip stays ripped. If intra-board paths are always
board-framed (and thus env-durable) and the one remaining
env-sensitive case (hand-origin with drifted env) is rare AND
can degrade cleanly to "apply-immediate," we don't need the
synthesis code back. We enforce "the board stays the same shape"
by keeping `BG.boardViewportLeft/Top` + the 800×600 dimensions
stable — if those ever move, THAT'S the bug, not the replay.

## Scope ask

Step 2 is the real work here. Steps 3–5 are small JS-port
plumbing that becomes meaningful only when we're actually
shipping hand-origin Elm-captured paths and watching them
replay across env changes. I'd suggest Step 2 first as a
standalone commit, and then 3–5 as a follow-up. Confirm and
I'll go.
