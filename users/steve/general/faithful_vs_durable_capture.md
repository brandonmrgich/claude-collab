# Faithful capture vs. durable facts

When Elm witnesses a hand-to-board move in real time, it owns
the whole truth of the gesture. Two layers of that truth must
be preserved in the replayable transcript, and they play
different roles.

## The durable layer — survives any future environment

- **The logical move.** Which hand card was played, which
  board stack it joined, which side. A plain wire action.
- **The board-frame landing coord.** Where the card ended
  up, expressed with the board's top-left as `(0, 0)`. This
  is geometry in the game's own frame, independent of
  viewport, window, device, or browser. Always reconstructable.

These are FACTS. They will not change meaning if the window is
resized, the browser is swapped, or the DB is read three days
later.

## The rich layer — faithful but environment-bound

- **The raw pointer path.** Every `(t, x, y)` sample the mouse
  produced during the drag, in viewport coords, timestamped at
  capture.
- **The environmental context.** A snapshot of the viewport's
  dimensions and pixel density AT THE MOMENT OF CAPTURE.

These are RICH FACTS with a lifespan. If future-Elm's
environment matches what's stamped alongside the path, the
playback is pixel-faithful — every jitter, hesitation, and
mid-drag correction replays exactly. If the environment has
changed (window resized, different device), the stored path is
no longer geometrically valid for this screen, and future-Elm
falls back to synthesizing a drag from the durable facts.

The environmental stamp isn't decoration; it's the provenance
that tells future-Elm "you may trust me" or "I'm stale."

## What the browser gives us for free

Everything we need to implement this discipline is already in
the browser API, no wrapping required:

- **`window.innerWidth` / `window.innerHeight`** — current
  viewport dimensions, for both the capture-time stamp and the
  replay-time comparison.
- **`window.devicePixelRatio`** — current DPR; same uses.
- **`Element.getBoundingClientRect()`** (Elm:
  `Browser.Dom.getElement`) — the live viewport offset of any
  DOM element. We use this at capture to convert the board
  div's current viewport position into a board-frame landing
  (`landing_viewport − board_rect_top_left`). And at replay to
  learn where the board sits now, so we can translate board-
  frame → current viewport for rendering.
- **`pointerEvent.clientX` / `clientY`** — viewport coords
  directly from the pointer. No manual translation needed to
  record the raw path.
- **`pointerEvent.timeStamp`** — high-resolution monotonic
  timing for each sample, without wall-clock fragility.
- **`Browser.Events.onResize`** (Elm) — a subscription for
  when the environment changes mid-session. If we cared, we
  could mark older captures as "environment has drifted since"
  in-memory without requiring a reload.

Because the browser hands us both the viewport metadata and
the DOM element's live rect, we don't have to agree in advance
about the board's viewport offset — we can always ASK at
capture time. The capture records the answer; the replay reads
the current answer; if they match, faithful playback; if not,
simulate.

That's a significant simplification over the "pin the viewport
coords with shared constants across languages" mental model I
was in earlier today. For Elm-authored captures, the browser
itself is the source of truth for viewport geometry at any
moment — no cross-language agreement needed. The cross-
language agreement only matters when a NON-browser source (the
Python agent) needs to speak about board geometry — and for
that, board-frame coords suffice because the board's top-left
is (0, 0) by definition.

## Summary

| Layer                        | Frame         | Durability                         | Who needs it                                    |
|------------------------------|---------------|------------------------------------|-------------------------------------------------|
| Logical move                 | none          | forever                            | server, replay, agents                          |
| Board-frame landing          | board (0,0)   | forever                            | server, replay, agents                          |
| Raw pointer path             | viewport px   | only until environment changes     | Elm replay (faithful playback)                  |
| Environmental context stamp  | N/A           | forever (tells you when path ages) | Elm replay (decides faithful vs. simulate)      |

The split removes the agonizing about "what viewport do both
sides share." There IS no shared viewport for hand-to-board;
there's a shared BOARD FRAME for everything intra-board and
for the landing half of hand-to-board. The viewport belongs
to the capture environment, which the browser will tell us
about at any moment.
