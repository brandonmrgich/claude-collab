# Environment-stamping for replay — what the doc is asking for

You asked me to flesh out the "durable vs. rich facts" section
of `games/lynrummy/ARCHITECTURE.md`. Here's my reading of what
the doc intends, reality-checked against the shipped code, and
the concrete work it implies.

## The principle

A move-as-recorded has two layers:

- **Durable.** Logical intent (which card, which target stack,
  which side) + board-frame coords of anything landing on the
  board. Board frame is env-independent by construction — a
  stack at `(300, 200)` means the same thing on any browser,
  any monitor, any window size.
- **Rich.** Raw pointer path in viewport pixels, timestamped
  per sample, plus the environmental context captured at the
  moment of drag: viewport width/height, device-pixel-ratio.
  Pixel-faithful while the environment matches; stale after a
  window resize, DPI change, or different monitor.

The rule the doc proposes: **play back the rich path when the
captured env ≈ current env; otherwise synthesize from the
durable layer.**

## Reality check — what's shipped vs. what the doc implies

The doc overstates the current state in two places. Here's what
the code actually does today (2026-04-22):

| | Emits env stamp? | Replay consumes stamp? |
|---|---|---|
| Python synth | No. Just `path_frame:"board"` + `pointer_type:"synthetic"`. Board frame is env-independent, so this is implicitly "no stamp needed" — a happy accident, not a decision. | N/A |
| Elm live drag | **No.** `encodeEnvelope` in `Main/Wire.elm` ships only `{path: [...]}`. No `path_frame`, no `pointer_type`, no viewport, no DPR. | N/A |
| Elm replay | N/A — branches purely on path *presence*. | No stamp-reader exists. |

The schema comment on `lynrummy_elm_actions.gesture_metadata`
already names "viewport at drag start, devicePixelRatio" — but
neither emitter writes those fields today. That comment
reflects the plan, not the shipped state.

## Concrete work, in dependency order

1. **Symmetric emission.** Elm live drag emits
   `path_frame: "viewport"` + `pointer_type: "mouse"` for parity
   with Python's shape. Cheap baseline step; nothing depends on
   it but it reduces special cases everywhere downstream.

2. **Elm captures env at drag-start.** On `mousedown`, read
   `window.innerWidth/Height` + `devicePixelRatio`, stash into
   `DragInfo.env`. Ship as `gesture_metadata.env: {vw, vh, dpr}`.
   Needs either a JS port (cleanest) or a decoder on the
   `MouseEvent` (brittle — not all env fields are on the event).

3. **Elm measures env at replay-start.** Alongside the existing
   `boardRect` Task, fire a Task to read current viewport + DPR.
   Stash on `model.replayEnv`.

4. **Replay decision rule.** In `prepareReplayStep`:
   - `path_frame == "board"` → always faithful (Python paths,
     and Elm paths under option A below).
   - `path_frame == "viewport"` + env matches → faithful.
   - `path_frame == "viewport"` + env drifted → fallback
     synthesis from the durable layer.

5. **Partial un-rip of synthesis.** The
   `synthesizedReplayAnimation` I deleted last night comes back,
   but guarded by env-drift — it's no longer the default. Python
   paths are always faithful; only human-captured hand-origin
   drags on a resized window ever hit the fallback.

## The architectural choice to settle first

Today Elm-captured intra-board drags ship with no `path_frame`
tag (defaults to viewport in the decoder). The doc says
intra-board drags belong in board frame. Two options:

**(A) Elm translates intra-board samples to board frame at
capture.** Subtract the live board rect from each sample as
it's recorded. Those paths become env-independent like
Python's. Only hand-origin drags stay viewport-framed (they
have to — they cross the board widget boundary). Result: the
env-drift fallback is only ever reachable for hand-origin
human-captured drags on a resized window.

**(B) Elm keeps viewport-frame samples for all drags.** Every
Elm path needs an env stamp. Every replay of an Elm path
consults the stamp. More uniform, but more code paths depend
on env-stamp correctness.

My gut is (A) — in the spirit of "durable always." It keeps
the happy path simple and confines env-stamp complexity to the
one case it actually serves (hand-origin viewport paths). You
might disagree — (B) is more explicit about what the path is,
which has its own appeal.

## Why this matters

Without the stamp-reader, a window-resize between capture and
replay produces faithful-looking playback aimed at **stale
viewport coords**. The cards visibly drift to wrong positions
— the exact kind of "playback lies to the viewer" bug that
would undermine the motor-fidelity milestone we just shipped.
Today this is latent; nobody resizes mid-session. But the bug
is real and the instrument for detecting it is the stamp.

Pick A or B and I'll scope the build.
