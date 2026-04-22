# Board-frame drag floater — four questions before code

You called me out: I was about to introduce needless Elm-side
translation when the browser's layout engine should handle
board→viewport positioning for free via CSS. The right picture
as I now understand it:

- Intra-board drag floater is a DOM child of the board div,
  positioned in board frame via CSS. Browser does the math;
  Elm never does.
- Hand-origin drag floater must be viewport-positioned,
  because its source (hand card) and target (board stack)
  live in different DOM subtrees.

Before I touch any code, four questions. Reply inline at any
paragraph — I'll read them and code against your answers.

---

## Q1 — One floater that reparents, or two slots?

**Option A:** a single `draggedOverlay` chooses its parent
(board div vs. viewport root) based on action kind.

**Option B:** two floater slots at different levels in the
tree, only one active at a time.

B is simpler to reason about in Elm's declarative view model
— each slot has a fixed parent, the view just decides which
is populated — but it adds a second place the floater can
live. A is more unified but the reparenting is a state the
view has to track.

I lean B. Your call?

---

## Q2 — Capture-time translation for live intra-board drags?

Currently `MouseMove` stores `cursor` in viewport frame (mouse
events are viewport by nature).

Do you want Elm to subtract `boardRect.x/y` once at MouseMove
time so the stored `cursor` in `DragInfo` is already board-
frame for intra-board drags? Then rendering becomes trivially
`style "top" (String.fromInt cursor.y) ++ "px"` with no math.
It costs one subtraction per mouse event and it enforces the
board-frame invariant at the storage boundary.

The alternative is to capture in viewport and translate at
render time. That's cheap too, but it keeps the two frames
coexisting inside `DragInfo` and invites exactly the class of
bug you're trying to eliminate.

I lean toward translating at capture time.

---

## Q3 — What frame does `syntheticEndpoints` emit?

This is Elm's fallback synthesis path for intra-board actions
when there's no captured `gesture_metadata`. Right now it
emits viewport coords.

If the floater is a board-div child for intra-board, this
function should emit board-frame coords too — matching the
frame Python now uses and aligning with the floater's
positioning parent.

I think this is a straightforward yes, but flagging it
because it's a behavior change to a function you might not
be thinking about.

---

## Q4 — `model.replayBoardRect` becomes vestigial?

After this refactor, intra-board replay no longer needs
`model.replayBoardRect`: CSS positioning handles the
board→viewport math implicitly via the DOM tree.

The only remaining consumer would be hand-origin synthesis
— where the floater is viewport-positioned, and the target
stack's viewport coord is needed for the replay drag's
endpoint.

If you agree, `replayBoardRect` keeps its role but its scope
narrows significantly. If you disagree and you see other uses
I'm missing, name them.

---

## My default answers if you just say "proceed"

- Q1: **B** (two floater slots)
- Q2: **Translate at capture time** (store board-frame in
  DragInfo for intra-board drags)
- Q3: **Yes, board-frame**
- Q4: **Yes, replayBoardRect narrows to hand-origin synthesis
  only**

Say "proceed" and I'll execute on those. Or correct any one
inline.
