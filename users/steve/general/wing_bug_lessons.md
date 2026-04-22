# Lessons from the wing-hit bug

Elm's board-to-board merge silently dropped on drop. It was
intermittent, visibly correct ("I saw the wing!"), and it
resisted one whole evening's worth of speculation about CSS
layering, `pointer-events`, and z-index. The fix wasn't to
make the DOM-event path reliable — it was to stop using the
DOM event path at all. Three lessons worth keeping.

## 1. When you're the one rendering it, stop asking the DOM about it

We rendered the floater. We rendered the wings. We knew both
rects. But we delegated "is the cursor over the wing?" to
`onMouseEnter` / `onMouseLeave` — asking the browser to tell
us something we already knew, and then suffering when the
browser's delivery was unreliable. The diagnostic that broke
the impasse wasn't "make the DOM events fire more
consistently"; it was "write `floaterOverWing` in Elm and
make *that* the authoritative answer." The DOM machinery
became a needless extra moving part the moment Elm owned
enough state to compute the answer itself.

Connection: `feedback_own_the_whole_system.md`. When the
answer is derivable from state you control, deriving it is
almost always better than asking a different system to tell
you.

## 2. Two competing models of the same thing is the worst kind of drift

We had the board's stacks identified two ways: by content
(CardStack refs, on the wire) and by position (array indices,
in Drag state + WingId + Msg payloads). Nothing forced the
two to agree, and when investigating the wing bug the
positional representation made every question ambiguous ("is
`FromBoardStack 5` stable across this whole operation?
What if the list reorders?"). Collapsing to a single
content-based representation didn't fix the wing bug directly,
but it removed enough fog that the remaining bug was easy to
see.

Connection: `feedback_no_indices_no_floats_in_drag.md`. Pick
one model per concept and enforce it everywhere.

## 3. Strict equality beats fuzzy equality

Yesterday I wrote `stacksEqual` as multiset comparison (cards
in any order). Felt forgiving. Today's clarity: no, that was
fuzzy thinking papering over a different problem. If the
system has a canonical representation of every stack — same
cards, same order, same integer-exact location — then strict
equality is cheaper AND safer. "Two clients might form the
same logical group in different orders" turns out to be a
non-problem once the wire format demands one canonical form.
Every layer agrees on the stack's identity or it's not the
same stack.

Connection: the corollary of the no-competing-models rule.
Equality is the place where drift crystallizes into silent
bugs.

## 4. Pure tests that "prove the bug isn't here" are still worth writing

We wrote tests for the WingOracle, the wing-rect computation,
and `resolveGesture`. All 16 passed — which didn't fix the
bug, since the bug lived in the step those tests couldn't
cover (DOM event delivery). But passing meant the bug *wasn't*
in steps 1/2/4, which was a huge diagnostic narrowing. The
refactor that followed was confident in a way it couldn't
have been without those tests, because we knew the surrounding
logic was pristine.

Tests don't have to catch the bug to earn their keep. They
can localize it.

## Meta-lesson: simplification also fixed the UI

The refactor that killed the bug ALSO delivered the live wing
highlight + status bar prompt the player needed. We hadn't
had those before because the wire-up to do them from DOM
events was fiddly. Doing them from Elm state is trivial.
When the right model arrives, the "nice to have" features
often fall out as a bonus. That's a signal the model is in
the right shape.

---

Commits in the thread (order of landing):

- `5bfe02a` — drop indices from drag state; adopt content
  refs; strict `stacksEqual`.
- `f2bd86e` — keep the diagnostic Debug.logs while debugging.
- `5f04a60` — compute wing hover in Elm; rip DOM event path;
  live status-bar feedback.
