# Next steps: replay geometry, done right

## Where we landed

The pivot to "layout-first" needed refinement. After the
walkthrough, here's the crisper version:

### Two kinds of coordinates, different treatments

**Board coordinates are pinned.** Every stack has a `{left,
top}` within the 800×600 board. Both Python and Elm agree on
this by construction. The board itself sits at a pinned
viewport offset, declared once as a shared constant. No guesses.

**Hand-card coordinates are not pinned.** Hand layout is
flow-based, content-dependent, and may wrap. Trying to make
Python compute per-card positions that match Elm's browser
layout is where yesterday's frustration came from. We stop
trying.

### Faithful vs Simulated — hand-to-board only

The only ambiguous origin is a hand card. Everything else
(stack on the board) has a pinned origin.

- **Faithful:** this Elm runtime captured the drag. The
  recorded path is the real cursor trace in this viewport.
  Replay plays the path back as-is.
- **Simulated:** the action came from somewhere else (a Python
  agent, the wire, a DB hydration, another Elm instance).
  Elm cannot trust any attached coordinates. Instead it
  synthesizes a drag at replay time: origin = the hand card's
  current DOM position (Elm knows it; Elm is rendering it),
  target = pinned board coords from the action payload.

The classifier is simple: paths captured by THIS runtime are
Faithful. Anything hydrated from elsewhere is Simulated. No
UUIDs, no wire flag — Elm knows, structurally, which bucket a
given in-memory action falls into.

### Intra-board moves: the distinction narrows

Faithful/Simulated only changes behavior for `MergeHand` /
`PlaceHand` — the hand-origin actions.

For `Split`, `MergeStack`, `MoveStack`: both endpoints are
board stacks with pinned `loc` fields. Source and target are
agreed by construction. Elm can always synthesize a correct
path between two pinned points regardless of who authored
the action. Faithful, if available, replays the human's
actual motion style — but it's an upgrade, not a correctness
requirement.

### This relieves the absolute-positioning burden

The original "layout-first" plan implied rewriting Elm's hand
area to absolute positioning so Python could compute per-card
coords. With Simulated synthesizing from Elm's DOM knowledge,
we don't need that. Elm can keep its flow-based hand layout;
Simulated replay just asks the DOM where the card is right now
and starts the drag there. The board still gets pinned, but
that's a much smaller change.

## What this means for the wire

We own the wire. So: whatever data Elm needs to make the best
decision, the wire carries it. Python's responsibilities to
the wire become:

- **Card identity for hand plays** (already on the wire —
  `hand_card: {value, suit, origin_deck}`). This is what
  Simulated mode uses to locate the card in the DOM.
- **Pinned board target** (already on the wire —
  `target_stack`, `side`). Combined with agreed board geometry,
  this gives the landing point.
- **Nothing else specific to hand origin.** Python doesn't
  know where the hand card is on Steve's screen, and under
  Simulated mode it doesn't need to. We DROP the attempt to
  synthesize hand-origin coords from Python entirely.
- **Gesture paths from Python are optional** and — under the
  new model — Elm ignores them at replay time (since Python-
  originated paths are always Simulated). We could remove them
  from Python synthesis altogether, OR keep them as diagnostic
  telemetry (the `telemetry.py` read-side already treats them
  as behavioral data).

## Pacing

Two time scales, both set for human perception:

- **Between major events: ~1s.** Pre-roll before the first
  action; beat between actions. Same "on the order of a
  second" both places.
- **During a drag: 80ms/pixel.** Exaggerated for now;
  Steve will measure real human velocity soon.

## Sequenced work

1. **Declare shared viewport geometry** — a single source for
   board-in-viewport offset plus anything else the wire format
   assumes. Python and Elm both consult it.
2. **Update Elm layout** to render the board at the declared
   offset. Hand layout stays as-is.
3. **Classify actions as Faithful or Simulated** as Elm
   acquires them. In-memory tag per action.
4. **Teach the replay state machine** to branch on the tag:
   Faithful plays back the captured path; Simulated synthesizes.
5. **Simulated synthesizer in Elm:** for hand-to-board, look up
   hand card DOM position, target via pinned board coords,
   duration = distance × 80ms/px. For intra-board, same but
   with pinned origin.
6. **Python simplifications:** `gesture_synth` stops caring
   about viewport coordinates for hand origins. Keep it for
   telemetry shape if useful; retire it if not.
7. **Pacing:** pre-roll and between-action beat to 1000ms.
8. **QA the whole autonomous game** — run a full agent game,
   watch the replay end-to-end. Flag anything that looks wrong.
   The first move isn't the bar; every move through endgame is.

## Open (deferred)

- Intelligent DB storage so reloaded sessions can be Faithful
  across browser runs. We control the DB; this is a later
  enhancement.
- Experimental measurement of Steve's actual drag velocity.
  80ms/pixel is a placeholder.
- Whether to keep Python-emitted gesture_metadata at all
  once Simulated synthesizes in Elm.
