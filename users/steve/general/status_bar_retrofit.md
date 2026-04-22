# STATUS_BAR retrofit plan — lift from TS, wire into Elm

You were right: these messages were carefully crafted. Not
reinventing. Here's what exists in `angry-cat/src/lyn_rummy/
game/game.ts` and the shape of the retrofit.

## The per-action mapping, verbatim from TS

From `game.ts:2044–2076` (plus the geometry-transition hook in
`process_and_push_player_action`):

| Action | Condition | Text | Kind |
|---|---|---|---|
| `Split` | always | "Be careful with splitting! Splits only pay off when you get more cards on the board or make prettier piles." | Scold |
| `PlaceHand` | always | "On the board!" | Inform |
| `MoveStack` | always | "Moved!" | Inform |
| `MergeStack` / `MergeHand` | merged size ≥ 3, clean board | "Combined! Clean board!" (via `clean_board_message`) | Celebrate |
| `MergeStack` / `MergeHand` | merged size ≥ 3, not clean | "Combined!" | Celebrate |
| `MergeStack` / `MergeHand` | merged size < 3 | "Nice, but where's the third card?" | Scold |

Plus a post-action geometry-transition overlay (fires AFTER the
per-action message, potentially overwriting it):

| Pre | Post | Text | Kind |
|---|---|---|---|
| CROWDED | CLEANLY_SPACED | "Nice and tidy!" | Celebrate |
| any | CROWDED | "Board is getting tight — try spacing stacks out!" | Scold |

And the turn-boundary inform (game.ts:1979):

- On turn start: `"${ActivePlayer.name}, you may begin your turn."` Inform.

## Why Elm makes this more indirect

TS just imperatively calls `StatusBar.celebrate("foo")` at the
point where the action resolves — trivial. In Elm, the physics
pipeline goes `handleMouseUp → resolveGesture → applyAction →
returns new Model`. None of those steps currently threads a
status message through. The fix needs ONE status-computing
function that knows (action, pre-board, post-board) and writes
the result into the Model in `handleMouseUp`.

## Retrofit shape

One pure helper, one call-site change:

```elm
-- Main/StatusMessages.elm (new module, or tacked into Gesture.elm)
forAction : WireAction -> BoardBefore -> BoardAfter -> StatusMessage
```

Inputs it needs:
- The WireAction (for the Split/MoveStack/etc. branch)
- Pre-action board (for geometry classification + merged-stack
  size lookup)
- Post-action board (same)
- Score before/after (optional — TS also has "banked N points"
  in some branches; we can defer that)

Logic:
1. Primary message: switch on WireAction shape. For merges,
   inspect the post-board's newly-appended stack for size.
2. Geometry overlay: classify pre and post via
   `BoardGeometry.classifyBoardGeometry`. If the transition is
   CROWDED→CLEANLY_SPACED, overwrite with "Nice and tidy!"
   Celebrate. If post is CROWDED, overwrite with "Board is
   getting tight…" Scold.

Clean-board detection for "Combined! Clean board!": post-board
is CLEANLY_SPACED AND every stack classifies as a valid
group (set / pure_run / rb_run). Game has a classifier already;
lift into the helper.

## Where to wire

In `Main/Gesture.elm`'s `handleMouseUp`, after `applyAction`
runs and we have `modelAfterAction`:

```elm
let
    status =
        StatusMessages.forAction action
            modelAfterDragClear.board     -- pre
            modelAfterAction.board        -- post
in
{ modelAfterAction | status = status }
```

Replay bypasses `handleMouseUp`, so the status bar stays quiet
during Instant Replay — that's the right default per your
framing.

## Scope split (bite-sized)

1. Primary per-action messages (no geometry overlay, no clean-
   board detection). Ships the 7-row table above minus the
   transition rows. ~20 LOC + the wiring.
2. Geometry transitions ("Nice and tidy!", "Board getting
   tight"). Needs pre/post classification. Another ~15 LOC.
3. Clean-board-context for Combined. ~10 LOC.
4. Turn-start inform ("${name}, you may begin your turn.").
   Tiny — wire into `applyCompleteTurn` alongside the existing
   "Turn N — Player M to play." (or replace it).

Ship 1–2 first, land, then 3–4 as follow-ups. Each is a tight
commit.

## What I need from you

- Confirm the messages in the table are what you want ported
  verbatim (or call out tweaks).
- Pick the location for `StatusMessages`: standalone module
  (`Main/StatusMessages.elm`) or tucked inside
  `Main/Gesture.elm`? My gut is standalone — the messages
  themselves are enough content to warrant a file, and a
  sidecar lets future-Claude find them at a glance.
- Go/no-go on the scope split.
