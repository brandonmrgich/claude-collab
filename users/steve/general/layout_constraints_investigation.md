# Layout constraints: investigation, part 1

Before any more code changes, pinning down what the browser
actually forces on us vs. what I've been choosing. Short
reflection interspersed with the report.

## Part 1a — The positioning primitives

There are five positioning values for an HTML element:

### `static` (default)

The element participates in normal flow. Its position is
determined by its document order and the surrounding layout
algorithm (block / inline / flex / grid). `top`, `left`,
`right`, `bottom`, `z-index` are ignored. There is no explicit
reference frame; the element just sits where flow puts it.

Nearly every element in our current Elm UI is `static` by
default. That's why "Turn N" appearing in flow above `viewHand`
pushes `viewHand` down — `viewHand` is `static`; whatever came
before it in document order contributes to where it lands.

### `relative`

Still in flow — it keeps its static position as its baseline —
but `top/left/right/bottom` shift it visually without affecting
the flow of surrounding elements. Other content renders as
though the element stayed put.

More importantly: `position: relative` (and ALL non-static
positioning) **establishes a containing block** for descendant
`position: absolute` children. This is a load-bearing side
effect I'd forgotten — if a grandparent is `position: relative`,
an absolutely-positioned grandchild is measured from that
grandparent, not the viewport.

### `absolute`

Removed from flow. Positioned by `top/left/right/bottom`
relative to the **nearest positioned ancestor** — the nearest
ancestor whose `position` is anything other than `static`. If
no such ancestor exists, it's positioned relative to the
**initial containing block**, which is (for our purposes) the
viewport.

Because it's out of flow, its size does not contribute to its
parent's content height. A parent that has only absolute
children collapses to zero content height unless given an
explicit size.

### `fixed`

Removed from flow. Positioned relative to the **viewport** (the
browser's visible area), NOT the document. Does not scroll with
content. `top: 0; left: 0` of a `position: fixed` element is
always the top-left corner of the visible window.

**Gotcha (real browser constraint):** if any ancestor has
`transform`, `perspective`, `filter`, `backdrop-filter`,
`will-change: transform`, or some related properties, that
ancestor becomes the containing block for ALL `position: fixed`
descendants. In that case `fixed` behaves like `absolute`
relative to the transformed ancestor. This is one of the rare
cases where "fixed means viewport" is not universally true.

We have no transforms on our current ancestors, so `fixed` is
genuinely viewport-anchored.

### `sticky`

Acts like `relative` until its containing scrollable ancestor
crosses a user-defined threshold, then clamps like `fixed`
within that scroll region. Powerful but not relevant here.

## Part 1b — What this implies for pinning

The drag floater uses `position: fixed`. Its `top/left` is
read directly as viewport pixels. So any coordinate I intend
to agree on across Python and Elm must be **true viewport
pixels** at the moment the user sees them.

Three routes to ensure a stack or a hand card lives at
viewport `(x, y)`:

1. Make the stack/card itself `position: fixed` at `(x, y)`.
   No ancestor dependency. Viewport-absolute.
2. Make the stack/card `position: absolute`, and ensure there
   is NO intermediate `position: relative/absolute/fixed`
   ancestor between it and the viewport. Then it too is
   viewport-anchored.
3. Make the stack/card `position: absolute` inside a positioned
   ancestor, and carry the ancestor's viewport offset
   explicitly so you can add it when computing true viewport
   coords.

Route 3 is where I've been bleeding. Every `position: relative`
or `position: fixed` container I introduced became a new
reference frame for its descendants, and I treated the
container's claimed coord as if it were the descendants' coord.

Routes 1 and 2 are the clean options. Route 1 is more rigid but
has the simplest mental model. Route 2 requires discipline —
keep the ancestor chain unpositioned until the leaf.

## Part 2a — What forces flow?

**Nothing intrinsic to the browser forces any element to be in
flow.** Flow is the default. Any element can be
`position: absolute` or `position: fixed` and thereby removed
from flow entirely, occupying an explicit `(top, left)` without
pushing anything.

Specifically — nothing about the following forces them into
flow:

- Top bar / status bar.
- "Board" heading.
- "Turn N" label.
- Per-player score rows.
- Turn-controls button row.
- The board's 800×600 shell.
- The hand-card grid.

Each of these is in flow because I didn't specify otherwise —
a convention inherited from the port / prior code, not a
browser requirement.

**The constraint that felt real was imagined.** The constraint
that IS real is the containing-block chain: once I put
something in flow with a positioned ancestor, my claims about
where it sits get tangled.

## Part 2b — The convention vs. constraint split for our app

What genuinely needs flow (if anything):
- Probably nothing for this UI. Every element has a plausible
  (x, y). The game board is a fixed-size rectangle; the hand is
  a grid of known cells; status/nav bars are horizontal strips
  of known height.

What we get FOR FREE by accepting flow as a convention:
- Responsive layout — content reflows on window resize.
- Implicit stacking order.
- Easy "put this under that" without explicit coords.

What we give up by accepting flow as a convention:
- Agreement with Python on coordinates. The moment content
  reflows, Python's cached numbers are wrong.
- Predictable positions for replay synthesis.
- Simple mental model: "this card is at (x, y) in the viewport
  because we placed it there."

For a game-play surface specifically — where we're trying to
match a declared-up-front geometry — flow is actively hostile.
It's the thing I've been patching around, when I could have
just not used it.

## Reflection

I walked into this with "position: fixed on the outer
container" and thought I'd bought pinning. I hadn't. I bought
viewport-anchoring for the OUTER container only. Every
element inside still uses default positioning — that is,
flow — and flow adds up beneath each element to produce
content-dependent positions.

The pattern I missed: **viewport anchoring is transitive only
when you keep going.** A `position: fixed` ancestor with static
children gives you a fixed OUTER BOX but static INNER FLOW.
The inner flow then produces unpredictable per-element coords.

If I want a game area where every element's viewport position
is known in advance and matches a shared spec, the shape is:
**one positioned ancestor (fixed or absolute) + every coord-
owning element as an absolute child of it, with no further
positioned ancestors between.** One level of frame, no
intermediate frames.

In the current code, I have MULTIPLE levels of positioned
ancestors and flow mixed together (outer fixed + inner
relative + grandchildren static). That's why "pin the board
at 100" landed at 150 and "pin the hand at 30" landed at 20:
each intermediate frame added an offset I hadn't accounted for.

## Next

Investigation topics 3 and 4 still pending:

- What scroll vs. no-scroll rules do I need to internalize?
  (overflow:auto on a fixed container, how absolute children
  behave inside a scrolling fixed parent, etc.)
- Given the above, what's the minimum CSS structure that
  enforces the agreement we want — without nesting positioned
  ancestors?

Want me to keep going, or respond to this first?
