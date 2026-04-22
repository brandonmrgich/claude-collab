# A physical walkthrough of `split_for_set:both_edges`

The scenario. Hand has one card: `5H`. Board has two stacks:

- Stack A: `[5D, 6D, 7D, 8D]` at `(top=40, left=40)`
- Stack B: `[5S, 6S, 7S, 8S]` at `(top=40, left=300)`

Goal: form the 5-set `{5H, 5D, 5S}`.

## The human's physical sequence

A person would do this:

1. Peel `5D` off stack A. Stack A becomes `[6D, 7D, 8D]`. The
   `5D` is now alone, somewhere on the table.
2. Peel `5S` off stack B. Stack B becomes `[6S, 7S, 8S]`. The
   `5S` is now alone, somewhere else.
3. Pick up the `5S` card and place it onto the `5D` card →
   `[5D, 5S]` pair, somewhere.
4. Pick up `5H` from hand, place it onto the pair →
   `[5D, 5S, 5H]` set, the trick's anchor.

Four physical atoms. Each one "picks up a thing and puts it down
somewhere."

## Invariant (your framing)

Every time a stack or card is set down, the place it lands must
be empty.

There are **four landings** in this trick:

1. `5D` lands (after peel).
2. `5S` lands (after peel).
3. `5S` lands onto `5D` (the merge — the pair lands at `5D`'s
   current loc, shifted by Go's left-merge rule).
4. `5H` lands onto `[5D, 5S]` (merge — set lands at pair's
   current loc, shifted).

The 3rd and 4th landings inherit loc from the earlier peeled
card's resting place. If 1 and 2 landed in empty places, and no
one else has used that space, 3 and 4 inherit a legal loc by
transitivity.

So *structurally*, only landings 1 and 2 require a loc decision.
The rest are consequential.

## How the code expresses this today

In `hints.py::_emit_extract_and_merge_one_hand`:

```python
# Peel A.
peeled_a, sim = _emit_peel(sim, target_a, ci_a)
prims.extend(peeled_a)

# Drag A to an open spot big enough for the final 3-group.
a_idx = _find_stack(sim, target_a)
new_loc = find_open_loc(sim, card_count=3)
prims.append({"action": "move_stack", "stack_index": a_idx,
              "new_loc": new_loc})
sim = _apply_move(sim, a_idx, new_loc)

# Peel B.
peeled_b, sim = _emit_peel(sim, target_b, ci_b)
prims.extend(peeled_b)

# Merge B onto A.
prims.append({"action": "merge_stack", ...})
sim = _apply_merge_stack(sim, src, dst, side)

# Merge hand card onto the pair.
prims.append({"action": "merge_hand", ...})
sim = _apply_merge_hand(sim, dst, hand_card, hand_side)

_fix_geometry(sim, prims)
return prims
```

Notice: landing 1 is expressed as *"peel plus immediately drag
to an open spot."* That is the one-line-hook-ish part of the
code. It says: "after peeling, I immediately move to
find_open_loc."

But landing 2 isn't expressed that way. It's just a peel, no
move. The peeled `5S` inherits its loc from `_apply_split`'s
split-offsets. There's no explicit "find_open_loc for 5S."

**That is the complexity divergence.** Landing 1 and landing 2
— both are "pick up a thing, put it down empty" — are expressed
with different machinery. Landing 1 uses an explicit
`find_open_loc`. Landing 2 relies on `_apply_split`'s baked-in
offsets to keep the peeled card roughly near the source —
which in this scenario works because the pair merge absorbs
`5S` immediately, so it doesn't matter where `5S` briefly lands.

## And `_fix_geometry` is a safety net for a different bug

`_fix_geometry` at the end handles cases where *grown* stacks
(merges that widened) overlap neighbors that were fine before
the growth. It's not about peels/placements — it's about width
expansion.

Two separate concerns, two separate mechanisms.

## What the walkthrough reveals

Your "one function" is really answering: *every time a stack
lands, where?*

Today that decision is:

- **Peels** → via `_apply_split`'s Go-matching offsets (near
  source). Sometimes OK, sometimes not.
- **Planned moves** → via `find_open_loc(sim, card_count=N)`
  where N is picked by the emitter.
- **Merges** → inherited from target.
- **Growth overlap cleanup** → via `_fix_geometry` post-pass.

Four decision paths. The one-function version would be: every
landing is `find_open_loc(sim, card_count=N)` with N = the
final size of the thing being put down. If it's a transient
(about to be merged), the merge target might be the "empty"
answer. But "inherit from source" is the broken default case
because it permits transient overlap.

That's where I think the mismatch is. Is there still something
I'm misreading about the invariant?
