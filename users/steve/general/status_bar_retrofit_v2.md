# STATUS_BAR retrofit — v2 (colocated via return type)

You're right. Post-hoc classification ("diff the pre and post
boards to figure out what happened") is exactly the kind of
indirection that makes Elm feel heavier than TS here — and it's
a fake constraint. Elm's type system has the flexibility to do
what the TS code did naturally: **the function that performed
the action tells us what the message should be, as a first-class
output.**

## The pivot

Today `Apply.applyAction : WireAction -> Model -> Model`. The
caller gets a new model but no knowledge of what happened.

Change the return type so the message is part of what
`applyAction` produces:

```elm
type alias ActionOutcome =
    { model : Model
    , status : StatusMessage
    }

applyAction : WireAction -> Model -> ActionOutcome
```

Each branch inside `applyAction` already knows exactly what
physics ran. The branch for `MergeHand` sees the full merge
happen (pre-state from `model`, post-state from
`Reducer.applyAction`), knows the resulting stack's size, knows
whether the board is clean. It can produce "Combined!" or
"Nice, but where's the third card?" *right there*, next to the
mutation. No separate classifier function that has to squint at
before/after boards to infer what the mutation was — it already
knows.

This is as close to the TS `process_merge()` shape as Elm
allows: mutation and status generation, colocated.

## Caller changes

Three spots call `applyAction`:

1. **`Gesture.handleMouseUp`** — human action. Use
   `outcome.status` to overwrite `model.status`. Every human
   action writes, which is exactly the natural-clearing
   mechanism you wanted.

2. **`Main.CompleteTurnResponded`** — wire response fires
   `applyAction WA.CompleteTurn`. Use `outcome.status` (the
   existing "Turn N — Player M to play." can become that
   outcome's message, or we refine it to match the TS
   "${name}, you may begin your turn.").

3. **`Replay/Time.replayFrame`** — replay walker applies each
   action as the animation ends. *Discard* `outcome.status` —
   replay owns its own status lifecycle ("Replaying…" /
   "Replay complete."). Just use `outcome.model`.

## Where each message lives

In `Apply.elm`, alongside the branch that causes it:

```elm
case action of
    WA.Split _ ->
        let model2 = applyPhysics action model
        in { model = model2
           , status = { text = "Be careful with splitting! …"
                      , kind = Scold }
           }

    WA.MergeHand _ ->
        let model2 = applyPhysics action model
        in { model = model2
           , status = mergeStatus model model2 }

    WA.MergeStack _ ->
        let model2 = applyPhysics action model
        in { model = model2
           , status = mergeStatus model model2 }

    WA.MoveStack _ ->
        ...
```

`mergeStatus pre post` is a small helper in `Apply.elm` that
reads the post-board's newly-merged stack size and the clean-
board flag. It's still "looking at pre and post," but it's
colocated with the mutation and fired by the same branch that
produced the change — not a separate general-purpose
classifier trying to reverse-engineer intent.

For the geometry-transition overlay ("Nice and tidy!", "Board
getting tight…"), same idea: a small `tidynessOverlay pre post`
helper called from within the applyAction branches that want
it, layering on top of the primary message. Each branch picks
whether it cares about the overlay. That stays colocated; the
TS original had that as a post-hook but in Elm we can just
chain it:

```elm
WA.MoveStack _ ->
    let model2 = applyPhysics action model
        primary = { text = "Moved!", kind = Inform }
    in { model = model2
       , status = withTidynessOverlay model model2 primary
       }
```

Each call to `withTidynessOverlay` is one line per branch; the
helper itself is pure and tiny.

## Scope

One commit for the type change + all 5 per-action messages.
Follow-up commit for the tidyness overlay + clean-board flavor.
The essay-v1 idea of a standalone `Main/StatusMessages.elm`
module goes away — the messages live in the apply branches,
which is the whole point.

## Budget

As bite-sized as the pivot makes it. The refactor is mechanical
(one type change, threaded through three callers, ~5 one-liner
branches), the messages are lifted verbatim from
`angry-cat/src/lyn_rummy/game/game.ts:2044-2076`, and nothing
about it is architecturally novel. Go when you confirm.
