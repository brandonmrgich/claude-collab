# Lyn Rummy wire format (Python-emitter scope)

**As-of:** 2026-04-21.
**Scope:** every wire shape the Python agent currently sends.
Elm-only actions (today: `undo`) are out of scope here — see
`wire_action.go` for the complete union.
**Status:** `STILL_EVOLVING`. A refactor is in flight; see the
**⚠ Refactor in flight** callouts below for the fields about to
change. Everything else is stable.

Canonical Go-side source: `games/lynrummy/wire_action.go`. Elm
counterpart: `games/lynrummy/elm/src/Game/WireAction.elm`. This
document is the reader-friendly surface for both.

## Endpoint + envelope

All actions POST to the same endpoint:

```
POST /gopher/lynrummy-elm/actions?session=<SID>
Content-Type: application/json
```

The body is an **envelope**: a `"action"` sibling plus an
optional `"gesture_metadata"` sibling. Keeps the action's JSON
clean (no telemetry fields) and leaves room for more metadata
kinds later without touching action shapes.

```json
{
  "action": { "action": "move_stack", "...": "..." },
  "gesture_metadata": {
    "path": [ { "t": 1700000000000.0, "x": 136, "y": 40 } ],
    "path_frame": "board",
    "pointer_type": "synthetic"
  }
}
```

`gesture_metadata` is optional; it's omitted for actions that
have no pointer-path story (`complete_turn`, any action the
Python agent doesn't synthesize a drag for).

`complete_turn` has its own endpoint:

```
POST /gopher/lynrummy-elm/complete-turn?session=<SID>
```

Its body is the envelope above, with `action` set to
`complete_turn`.

## Shared shapes

### `Card`

Every card in the double deck is globally unique by
`(value, suit, origin_deck)`.

```json
{ "value": 7, "suit": 3, "origin_deck": 0 }
```

| Field         | Type | Meaning |
|---|---|---|
| `value`       | int 1–13 | 1 = Ace, 11 = Jack, 12 = Queen, 13 = King |
| `suit`        | int 0–3  | 0 = Club, 1 = Diamond, 2 = Spade, 3 = Heart |
| `origin_deck` | int 0–1  | Which half of the double deck this card came from |

### `Location`

Board-frame coordinate pair. Origin is the board's top-left.

```json
{ "top": 20, "left": 40 }
```

Accepts both integer and floating-point on decode (Cat's old
drag UI sent floats; referee truncates).

## Actions sent by the Python agent

For each action below: the JSON shape, an inline example, and
what the action does.

### `split`

Cleave one board stack in two at `card_index`.

```json
{
  "action": "split",
  "stack_index": 3,
  "card_index": 2
}
```

`stack_index` — positional index into the current board list.
`card_index` — position within the stack to split after; the
first `card_index` cards become the left half, the rest the
right.

**⚠ Refactor in flight (2026-04-21):** `stack_index` →
`cards` (the **full ordered list** of cards making up the
stack — the server resolves it against the current board at
apply time). `card_index` stays, since it's a position
*within* the stack, not a reference *to* one.

After the refactor:

```json
{
  "action": "split",
  "cards": [
    { "value": 13, "suit": 2, "origin_deck": 0 },
    { "value": 1,  "suit": 2, "origin_deck": 0 },
    { "value": 2,  "suit": 2, "origin_deck": 0 },
    { "value": 3,  "suit": 2, "origin_deck": 0 }
  ],
  "card_index": 2
}
```

### `merge_stack`

Merge one board stack into another on a given side.

```json
{
  "action": "merge_stack",
  "source_stack": 3,
  "target_stack": 0,
  "side": "right"
}
```

`source_stack`, `target_stack` — positional indices into the
current board list. `side` — `"left"` or `"right"`.

**⚠ Refactor in flight:** `source_stack` → `source_cards`;
`target_stack` → `target_cards`. Both carry the **full ordered
list** of cards making up the respective stack.

After the refactor:

```json
{
  "action": "merge_stack",
  "source_cards": [
    { "value": 7, "suit": 3, "origin_deck": 1 }
  ],
  "target_cards": [
    { "value": 7, "suit": 2, "origin_deck": 0 },
    { "value": 7, "suit": 1, "origin_deck": 0 },
    { "value": 7, "suit": 0, "origin_deck": 0 }
  ],
  "side": "right"
}
```

### `merge_hand`

Merge a hand card onto a board stack on a given side.

```json
{
  "action": "merge_hand",
  "hand_card": { "value": 7, "suit": 3, "origin_deck": 1 },
  "target_stack": 3,
  "side": "right"
}
```

`hand_card` — already content-addressed (good). `target_stack`
— positional index. `side` — `"left"` or `"right"`.

**⚠ Refactor in flight:** `target_stack` → `target_cards`
(full ordered card list of the target stack).

After the refactor:

```json
{
  "action": "merge_hand",
  "hand_card": { "value": 7, "suit": 3, "origin_deck": 1 },
  "target_cards": [
    { "value": 7, "suit": 2, "origin_deck": 0 },
    { "value": 7, "suit": 1, "origin_deck": 0 },
    { "value": 7, "suit": 0, "origin_deck": 0 }
  ],
  "side": "right"
}
```

### `place_hand`

Place a hand card on the board at a specified location as a new
one-card stack.

```json
{
  "action": "place_hand",
  "hand_card": { "value": 7, "suit": 3, "origin_deck": 1 },
  "loc": { "top": 400, "left": 500 }
}
```

`hand_card` — the card coming out of the hand. `loc` — where
the new stack's top-left should land, in board frame.

**Unchanged by the refactor.** No stack-by-index reference here.

### `move_stack`

Reposition one board stack. No card movement.

```json
{
  "action": "move_stack",
  "stack_index": 5,
  "new_loc": { "top": 20, "left": 310 }
}
```

`stack_index` — positional index. `new_loc` — target top-left
in board frame.

**⚠ Refactor in flight:** `stack_index` → `cards` (full
ordered card list of the stack being moved).

After the refactor:

```json
{
  "action": "move_stack",
  "cards": [
    { "value": 2, "suit": 0, "origin_deck": 0 },
    { "value": 3, "suit": 1, "origin_deck": 0 },
    { "value": 4, "suit": 0, "origin_deck": 0 },
    { "value": 5, "suit": 3, "origin_deck": 0 },
    { "value": 6, "suit": 2, "origin_deck": 0 },
    { "value": 7, "suit": 3, "origin_deck": 0 }
  ],
  "new_loc": { "top": 20, "left": 310 }
}
```

### `complete_turn`

End-of-turn signal. The envelope has no per-action fields
beyond the tag.

```json
{
  "action": "complete_turn"
}
```

**Unchanged by the refactor.**

## Gesture metadata (sibling of `action`)

Optional telemetry describing the drag that produced the
action. Emitted by Python for intra-board actions where Python
honestly knows both endpoints (`move_stack`, `merge_stack`);
omitted for hand-origin actions (`merge_hand`, `place_hand` —
Python doesn't know where hand cards sit in the viewport; Elm
synthesizes those at replay time from its own DOM).

```json
{
  "path": [
    { "t": 1776813872050.0, "x": 136, "y": 40 },
    { "t": 1776813872250.0, "x": 148, "y": 41 },
    { "t": 1776813873640.0, "x": 566, "y": 470 }
  ],
  "path_frame": "board",
  "pointer_type": "synthetic"
}
```

| Field         | Meaning |
|---|---|
| `path`        | Ordered samples. Each has `t` (unix-ms, float), `x`, `y` (ints). |
| `path_frame`  | `"board"` (origin at board top-left) or `"viewport"` (origin at browser top-left). Python emits `"board"` for intra-board drags. Elm-captured live drags emit `"viewport"`. Elm's replay renders a board-frame path as a DOM child of the board; CSS does the board→viewport math. Missing field ⇒ `"viewport"` by default (back-compat with pre-stamp rows). |
| `pointer_type`| `"synthetic"` (Python-generated) or `"mouse"` (Elm-captured human drag). Informational. |

**Unchanged by the refactor.**

## Coordinate frames — summary

- **Board frame.** Origin `(0, 0)` at the board's top-left. The
  wire's `Location` fields (`loc`, `new_loc`) are always
  board-frame. Python synthesizes gesture paths in board frame
  too.
- **Viewport frame.** Origin at the browser viewport top-left.
  Only relevant for Elm-captured live drags that cross the
  board widget boundary (hand→board). On the wire, that shows
  up as `path_frame: "viewport"` in `gesture_metadata`.

See `games/lynrummy/ARCHITECTURE.md` § "Frames of reference"
for the broader rule and the 2026-04-21 "pick the right frame,
don't maintain parallel coords" discussion.

## What this refactor changes — summary

Every `stack_index`, `source_stack`, `target_stack` field
becomes a **card list**: `cards`, `source_cards`,
`target_cards`. Each list is the full ordered contents of the
stack being referenced.

The server adds one helper, `findStackByCards(board, cards) →
*CardStack`, called at apply time to resolve the card list to
the current index.

Rationale, three benefits stacking:

1. **Stable across the reducer's reordering.** Stack list
   indices shift under split / merge / move (all of which
   remove-and-reappend), so every wire consumer had to
   re-fetch state and re-resolve indices before each action.
   Cards are globally unique in the double deck, so a card
   list is reorder-stable.

2. **Readable at a glance in the raw JSON.** Someone eyeballing
   the actions table can see which stack an action referred to
   without cross-referencing anything. A single representative
   card would be enough for uniqueness — the full list is
   chosen for the debugger.

3. **Built-in divergence check.** The server compares the
   client-sent card list against what it has on the board. A
   mismatch means the client was operating on stale state,
   and the action is rejected at the wire boundary — no
   silent corruption.
