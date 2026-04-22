# Path to agent-games-viewable-via-Elm-replay

## The goal (restated)

Steve runs a Python agent game end-to-end, clicks Instant
Replay in the Elm UI, and watches the game unfold — with
drags that look like drags, not teleports, landing on the
right cards in the right order at human-perceivable tempo.

## What we have now

- **Python agent plays full games.** 15+ turns, multiple
  trick types (direct_play, pair_peel, split_for_set, etc.),
  no referee rejections. Solid.
- **Elm replay state machine.** PreRoll / Animating / Beating
  / NotAnimating. Works for Elm-authored Faithful paths.
- **MergeHand replay synthesis.** Wired today via
  `HandLayout.cardCenterInViewport` → `stackEdgeInViewport`.
  Works in principle but lands in wrong viewport positions
  because of layout drift.
- **Pinned-viewport layout attempt.** Partially done;
  contains three known drifts (hand gutter off by 10px,
  board heading shifts the rect down ~50px, hand-grid
  container is position:relative inside flow).
- **Pacing.** PreRoll 1s, between-event beat 1s, drag at
  80ms/px. Reasonable defaults; needs real-world feel check.

## What's between us and the goal

Three categories of gap, in roughly decreasing blast radius:

1. **Geometry truth.** Whatever Python says or Elm computes
   as viewport coords has to match where things actually
   render. The layout pivot this morning tried to enforce
   this and produced the three drifts we identified. Until
   this is solid, every replay drag goes to the wrong place.
2. **Replay synthesis coverage.** We have it for MergeHand
   only. A real agent game uses MoveStack, Split, MergeStack,
   PlaceHand. Each needs its own synthesis path or will
   teleport. This is incremental and bounded.
3. **Real-world pacing & polish.** The current constants are
   guesses. Once we see a real agent game end-to-end, Steve
   will react to what feels off (drag too slow, beat too
   short, etc.) and we dial. This comes LAST because it's
   post-visual.

## The binary choice

Two paths to geometry truth. Each implies a different
organizing principle for the system.

### Option A — Pin the layout; agreement is the spec

Rewrite Main/View.elm so the rendered elements with claimed
viewport coords (the 800×600 board rect, the hand-card grid)
are DIRECT absolute children at those coords, with no flow
content between them. Headings, buttons, player-row content
get relocated or eliminated. The shared constants
(`boardViewportTop`, `handLeft`, etc.) become the spec; the
layout is enforced to match.

- **Pro:** one source of truth; simple mental model; Python
  and Elm agree by construction; no DOM round-trip at
  replay.
- **Con:** more invasive Elm layout rewrite; we have to
  relocate/skip displaced UI (the "Instant Replay" button
  needs a home); fragile if content wants to grow later.

### Option B — Let Elm ask the DOM; measurement is the truth

Keep the current flow-based Elm layout. At replay time, Elm
uses `Browser.Dom.getElement` to measure the board rect's
live viewport position and (when needed) a hand card's live
rect. Python stops emitting viewport coords entirely —
Python only emits board-frame coords plus card identity.
Elm translates board-frame → current viewport at render
time using the DOM-measured board offset.

- **Pro:** robust to any Elm layout (flow, pinned,
  responsive, future additions); "constraints must be real"
  — the browser's DOM rect IS real; fewer shared constants
  to keep in sync; matches Steve's "Elm owns its view"
  principle; Python stops pretending to know viewport.
- **Con:** replay synthesis needs Task-based DOM queries
  (async, slightly more Elm code); the hand-origin case
  still requires Elm to locate specific hand cards
  (doable — hand cards can get stable DOM ids — but another
  moving piece).

## My lean

Option B. It matches several principles we've already
articulated (Elm owns its view, constraints must be real,
own the whole system by measuring not assuming, Python
doesn't know viewport), AND it dissolves the drift-chasing
game we've been playing today. Pinning is seductive because
it sounds disciplined, but the discipline it enforces is
"don't have any other UI content" — which is a real cost
Steve will feel once we want buttons back.

---

# Zoom-in: under Option B, how big a sweep?

Option B says "Elm measures from the DOM at replay time;
Python emits only board-frame coords + card identity."
That's the direction. The next question is how much of it to
do today.

## Option B1 — Narrow + additive

Do just enough to make the 7H → 7-set replay land correctly,
then iterate outward later.

- Give the 800×600 board shell a stable DOM id. Elm's
  existing MergeHand synthesis uses `Browser.Dom.getElement`
  to fetch the live board rect and adds that offset to
  `stack.loc` to get the viewport target.
- Leave other primitives (MoveStack, Split, MergeStack,
  PlaceHand) untouched — their synthesis isn't wired yet;
  when we wire it, we'll use the same pattern.
- Leave `boardViewportTop/Left` in place as documentation /
  Python-expectation constants. Don't delete them yet.
- Revert `gesture_synth`'s `move_stack` endpoints back to
  board-frame (we pushed them to viewport this morning;
  that was wrong given the pivot).
- Test path: fresh Python agent session, one direct_play,
  click Instant Replay, verify the 7H flies from hand area
  to the 7-set's right edge.

**Pro:** small diff; one thing visibly working at end of day;
sets the pattern for broader sweep later.
**Con:** leaves inconsistency in the codebase — some paths
still reference viewport constants that aren't authoritative;
future-Claude may pick up the constants thinking they're
load-bearing.

## Option B2 — Broad + subtractive

Sweep all the drag-synthesis paths at once. Make the system
consistent today.

- Give the board shell AND every rendered hand card stable
  DOM ids.
- Rewrite Elm's replay synthesis for ALL primitives
  (MergeHand, MoveStack, Split, MergeStack, PlaceHand) to
  use DOM measurement for any board-referenced coord.
- Delete `boardViewportTop/Left` from shared constants; they
  were never true and shouldn't be confusing future-Claude.
  Python stops emitting viewport altogether — only board-
  frame + card identity.
- `gesture_synth.drag_endpoints` shrinks dramatically; may
  collapse to just board-frame endpoint emission or get
  retired outright.
- Test path: fresh Python agent session, FULL GAME, click
  Instant Replay, verify the whole game replays with visible
  drags for every move type.

**Pro:** consistency across the codebase; no half-finished
pattern for future-Claude to inherit; Python's role becomes
cleaner (facts only, no viewport speculation); full agent
game replay right now.
**Con:** bigger diff; more risk of breaking unrelated things;
likely not finishable in one sitting; we lose the tight
verification loop of B1.

## My lean

B1. Narrow + additive. Specifically because today has
already had a lot of architectural churn and Steve needs to
SEE the agent game replay before we broaden. One working
end-to-end slice beats a larger diff that might surface new
surprises. The subtractive cleanup is a natural follow-up;
we can do it fresh tomorrow with a known-good reference
point.

Pick one.
