# Walkthrough: can a board-to-board merge be unit-tested end-to-end?

You asked whether the "does the mouse land on the wing?" logic
is simple enough to be testable. Short answer: **the pure
pieces are testable; the hit-test itself currently isn't,
because we delegate it to the DOM.** That's actually a
refactoring opportunity — making the hit-test pure unlocks a
unit test AND is likely the reason board-to-board is broken
today.

Walking each piece in order, stating what I think it should do
and WHY before showing the code.

## 1. The WingOracle decides which wings exist

**What I think it does, and why.** Given a dragged source stack
and the current board, enumerate every (target, side) pair
whose merge is mechanically valid. The function probes
`BoardActions.tryStackMerge` for each candidate — if that
returns `Just`, a wing is offered; otherwise not.

This piece is pure, already testable, and almost certainly
**not** the bug — you saw the wing visually, meaning the
oracle DID offer one.

```elm
-- games/lynrummy/elm/src/Game/WingOracle.elm
stackWingsForTarget sourceIndex source ( targetIndex, target ) =
    let
        leftWing =
            case BoardActions.tryStackMerge target source Left of
                Just _  -> [ { stackIndex = targetIndex, side = Left } ]
                Nothing -> []

        rightWing =
            case BoardActions.tryStackMerge target source Right of
                Just _  -> [ { stackIndex = targetIndex, side = Right } ]
                Nothing -> []
    in
    leftWing ++ rightWing
```

**Unit-testable today** with no refactor. Given your 234 + 567
scenario, a test could assert `wingsForStack sourceIdx board`
returns the expected wing on 234's right side.

## 2. The wing's rendered position — pure

**What I think it does, and why.** `viewWingAt` takes a
`WingId` (which encodes target stack + side) and computes the
wing's rendered rect in board-frame coordinates from
`target.loc`. Pure computation; no DOM involvement yet.

```elm
-- games/lynrummy/elm/src/Main/View.elm
viewWingAt model info wing =
    case listAt wing.stackIndex model.board of
        Just target ->
            let
                wingLeft =
                    case wing.side of
                        Left  -> target.loc.left - pitch
                        Right -> target.loc.left + stackDisplayWidth target
                -- rect is (wingLeft, target.loc.top, pitch, cardHeight)
```

Also pure and testable. Given a board, we can assert "the wing
for this WingId would be rendered at these exact board-frame
coords."

## 3. The hit-test — currently delegated to the DOM

**What I think it does, and why.** When the cursor enters the
wing's DOM rect, the browser fires a `mouseenter` event. Elm's
`onMouseEnter` handler dispatches a `WingEntered` Msg, which
the update function uses to set `info.hoveredWing = Just wing`.

```elm
-- games/lynrummy/elm/src/Main/View.elm, inside viewWingAt
View.viewWing
    { ...
    , extraAttrs =
        [ Events.onMouseEnter (WingEntered wing)
        , Events.onMouseLeave (WingLeft wing)
        ]
    }
```

**This is the piece that isn't unit-testable.** We don't run a
hit-test ourselves; we rely on the browser's native event
dispatch against the wing's DOM bounding box. `elm-test` can't
simulate that without a DOM, and we don't have a headless
browser in the harness.

**This is also almost certainly where the bug lives.** Hand-
to-board works → the hit-test mechanism is generally fine. The
difference with board-to-board drags is probably one of:
- The floater or some other element intercepts the
  mouseenter event before it reaches the wing.
- The wing's DOM rect isn't where we think it is (a frame-of-
  reference slip between how we compute it and how the
  browser positions it).

## 4. The gesture resolver uses the hoveredWing — pure

**What I think it does, and why.** At mouseup, `resolveGesture`
reads `info.hoveredWing`. If it's `Just`, the gesture becomes a
MergeStack (or MergeHand for hand-source drags); if `Nothing`,
fall through to MoveStack or PlaceHand.

```elm
-- games/lynrummy/elm/src/Main/Gesture.elm
case ( info.hoveredWing, info.source ) of
    ( Just wing, FromBoardStack sourceIdx ) ->
        case ( listAt sourceIdx model.board, listAt wing.stackIndex model.board ) of
            ( Just source, Just target ) ->
                Just (WA.MergeStack { source = source, target = target, side = wing.side })
```

Pure and testable. The Debug.log I just added reads
`info.hoveredWing` at mouseup — so we'll see directly whether
it was `Just` or `Nothing`. My strong hypothesis is `Nothing`,
which would confirm the bug is at step 3.

## What's testable without refactoring

- Wing oracle correctness (step 1).
- Wing-rect computation (step 2).
- Gesture resolution (step 4) — given a hand-constructed
  `DragInfo` with `hoveredWing = Just wing`, assert the right
  `WireAction` comes out.

We can write those tests today. They'd catch regressions in 1,
2, 4 — but **not** the class of bug you're hitting, which lives
entirely in step 3 (DOM hit-test).

## The refactor that makes step 3 testable

Replace DOM-delegated hit-testing with **computed hit-testing
on every MouseMove**. The pieces to make it pure:

- **Input:** the wings list (already on `DragInfo`), each
  wing's rendered rect (computed from target's loc + side,
  same math as `viewWingAt`), and the current cursor
  (already on `DragInfo`).
- **Function:** `hoveredWingAt : List WingId -> List CardStack -> Point -> Maybe WingId`.
  Walks the wings, computes each rect, returns the first
  containing the cursor.
- **Wiring:** on each MouseMove, update `info.hoveredWing`
  from this function's result. Drop the
  `onMouseEnter`/`onMouseLeave` handlers.

This is ~30 LOC of Elm. It replaces browser-native hit-testing
with our own, and crucially makes the entire merge-landing
pipeline pure and testable. The unit test becomes trivially:

```elm
test "board-to-board merge lands when cursor is on the wing rect" <|
    \_ ->
        let
            board = [ stack234 atLoc 100 200, stack567 atLoc 300 200 ]
            wing = { stackIndex = 0, side = Right }  -- right of 234
            cursor = pointInsideWingRect wing board
            info = dragInfoOf 567 sourceIdx cursor [ wing ]
        in
        resolveGesture info model
            |> Expect.equal (Just (WA.MergeStack { ... }))
```

## Likely secondary benefit: fixes the current bug

If the current bug is a DOM-event quirk (floater blocking the
wing, element ordering, pointer-events inheritance), moving the
hit-test into Elm sidesteps it entirely. The cursor is viewport
coords; the wing rect is board frame; we have the board rect
from `Browser.Dom.getElement`; we can translate cleanly and
test the containment ourselves.

That's the same discipline we've been applying everywhere else
today: **own the whole system**, don't delegate load-bearing
decisions to opaque machinery when you can compute them
yourself and test them.

## Scope

- Write the three pure tests at steps 1, 2, 4 first (today's
  code, no refactor). They're cheap regression anchors.
- Then do the DOM-delegation refactor. Drop the mouseenter
  wiring, add `hoveredWingAt` to `GestureArbitration.elm` or a
  sibling, wire into MouseMove. Add the end-to-end test that
  asserts "cursor at the wing's rect → merge fires on mouseup."
- Sidecar pass.

Green-light the refactor and I'll go. If you'd rather keep the
DOM hit-testing and just diagnose what's blocking it, we can
do that too — I have the Debug.log in place and the next test
will tell us.
