# Where the Contract Broke: a split_for_set Post-Mortem

The failing game we watched this afternoon — 29 primitives,
stuck at `complete_turn` because of a stranded `[TD, TS]`
pair — wasn't an edge case or an agent-strategy gap. It was a
concrete contract violation between Go and Python, happening
in a layer neither of us looked at closely: the Python
inference that unpacked a `trick_result` into primitives.

This essay walks through the scenario with live data: the
board state, the hint that went over the wire, what Go had
already enforced by the time it sent that hint, and what
Python mangled when it tried to decompose.

## The board state going into the trick

I reproduced the scenario just now in a fresh puzzle session.
The board:

```
stack[0]  (loc 40,40)     [TD, JD, QD, KD]    diamonds run, 4 cards
stack[1]  (loc 40,280)    [TS, JS, QS, KS]    spades run, 4 cards
stack[2]  (loc 200,40)    [2C, 3C, 4C]        clubs run, context
```

The agent's hand:

```
[TH/d1]   — a single ten of hearts
```

`/hint` is called on this state. The top suggestion is
`split_for_set` — the three tens would form a clean 3-set on
the board:
`[TH (from hand), TD (from stack 0), TS (from stack 1)]`.

## What Go sent over the wire

The actual JSON from `/hint`'s top suggestion:

```
{
  "action": "trick_result",
  "trick_id": "split_for_set",
  "stacks_to_remove": [
    [TD, JD, QD, KD],      stack 0 before extraction
    [TS, JS, QS, KS]       stack 1 before extraction
  ],
  "stacks_to_add": [
    [JD, QD, KD],          stack 0's remnant (3-card run)
    [JS, QS, KS],          stack 1's remnant (3-card run)
    [TH, TD, TS]           the new 3-set, with hand's TH
  ],
  "hand_cards_released": [
    TH/d1
  ]
}
```

Three things to notice about this payload:

1. **Two source stacks** are being mutated —
   `stacks_to_remove` has two entries, not one.
2. **One hand card** is being consumed —
   `hand_cards_released` has one entry, not two.
3. **Three stacks_to_add**: two remnants (each still valid
   as 3-card runs) plus the new 3-set.

That shape is distinctive. It matches `split_for_set`'s
semantics: one hand card + two board cards of the same value
→ one new 3-set. It is structurally different from
`pair_peel`, whose shape is the reverse: two hand cards + one
board card → one new 3-set.

## Is Go enforcing its end of the contract?

Yes. Go's `split_for_set` recognizer in
`games/lynrummy/tricks/split_for_set.go` does four checks
before emitting this suggestion:

- **Each extraction is legal.** `findExtractableSameValue`
  iterates the board, and for each candidate card calls
  `CanExtract(cardIdx)`. That method (in
  `games/lynrummy/card_stack.go`) encodes the invariant
  directly: sets need size ≥ 4 to give up a card, runs need
  size ≥ 4 and end-position OR ≥ 3 cards on both sides of a
  middle split. In this board both TD and TS sit at the
  left-edge of 4-card runs, so both are extractable and the
  remnants will be 3-card runs — legal stacks at turn-end.
- **Two distinct suits.** `pickTwoDistinctSuits` guarantees
  the two board cards chosen have different suits and
  neither matches the hand card's suit.
- **The resulting trio is a Set.** Line 45 of the recognizer
  calls `lynrummy.GetStackType(trio) != lynrummy.Set` as a
  hard filter. If the three cards don't form a valid 3-set,
  the play is rejected.
- **`Apply` carries it out atomically.** It extracts both
  board cards, pushes the new 3-set, and the post-Apply
  board has only complete stacks.

In short: by the time the `trick_result` leaves Go and lands
on Python's doorstep, every invariant you'd want has already
been checked. Go is holding up its end.

## What Python did with it

The auto_player receives the suggestion and calls
`decompose.decompose_trick_result(action, state)` to convert
the compound `trick_result` into a primitive sequence. Here's
what my decomposer produced for this exact input:

```
Click-split TDJD/QDKD
Click-split TD/JD
Drag JD -> open
```

That is wrong in multiple ways:

- It's splitting the diamonds run, but at the **middle**
  (`ci=2`, then `ci=1`) — a split that `CanExtract` would
  refuse because it leaves `[TD]` alone and `[QD, KD]` as a
  pair. The Go trick never would have suggested this.
- It isolates and moves the **jack of diamonds (JD)**, not
  the ten. The actual target was `TD`.
- It emits **zero** `merge_hand` actions, so the hand's `TH`
  is never played. The hand card released by the trick is
  ignored.

By the time this primitive sequence lands, the board has
incomplete stacks everywhere, the hand is unchanged, and the
agent's "next action" is a `/hint` call against a mangled
board — which predictably spirals further.

## Where the contract broke

The contract is clean on Go's side. The wire is carrying a
self-consistent, invariant-respecting trick_result. What
broke is **Python's inference step** — the act of
reverse-engineering decomposer parameters from the
trick_result's compound form.

Two concrete bugs, both in
`tools/lynrummy_elm_player/decompose.py`:

1. **Wrong target identification.** The helper
   `_extract_non_hand_card` scans `stacks_to_add` for the
   first card that isn't a hand-released card. For
   `pair_peel` — whose `stacks_to_add` is `[source_remnant,
   new_3_set]` — this happens to return a card from the new
   3-set, which is the right target. For `split_for_set`
   — whose `stacks_to_add` is `[remnant_A, remnant_B,
   new_3_set]` — the first non-hand card is inside the first
   remnant, not the new set. The function returns JD (the
   head of the diamond remnant) as the "target," and
   everything downstream runs on that wrong value.

2. **Wrong hand-card count.** Even if the target were
   right, the decomposer filters the hand by value and
   emits one `merge_hand` per match. For `split_for_set`
   there is exactly one hand card of the target value — so
   one merge would land, leaving the isolated board card
   plus that one hand card as a pair. This is exactly the
   `[TD, TS]` we saw in session 22: the decomposer extracted
   one board card, merged one hand card, never extracted
   the second board card at all.

`pair_peel` and `split_for_set` have mirrored shapes (2+1 vs
1+2 cards). The decomposer I wrote is shaped for the pair_peel
case. Against pair_peel inputs it works. Against split_for_set
inputs it produces garbage. The comparator showed green on my
pair_peel puzzles because the puzzles had pair_peel inputs;
no split_for_set-shaped puzzle had been exercised by the
harness until a real game ran one.

## Where this points

The immediate fix is narrow:
`decompose.decompose_trick_result` should branch on `trick_id`
and use the right extraction logic per trick. For
`split_for_set`, that means finding **both** board cards to
extract (they are the non-hand-card members of the new 3-set,
identified by looking inside `stacks_to_add` — specifically
the stack containing the released hand card — and pulling
out the two non-hand cards). The decomposer then emits two
isolate-and-move sequences and one merge_hand, not one and
one.

The deeper point is the one you named: this is inference in
the wrong place. Go already knows the trick's full structure.
Python having to reverse-engineer it from
stacks_to_remove / stacks_to_add is exactly the misplaced-work
anti-pattern. The wire carried a compound form; Python had to
guess what it meant. It guessed wrong on one case for a long
time and we only saw it today because a real game exercised
the path.

The proper fix — move the decomposition to the producer, or
move tricks client-side entirely — remains the direction, and
it's the same direction we agreed on earlier. This
post-mortem is a data point for why it matters, not a reason
to change the plan.

## What "Go is enforcing its end" really means here

Precisely: **Go enforces the invariants of the compound form it
ships.** The `trick_result` payload is valid, legal, and
self-consistent. Every card referenced exists; every
extraction passes `CanExtract`; every resulting stack would
pass the turn-complete referee.

Go does **not** enforce that the consumer unpacks the
`trick_result` correctly. There's no way it could — once the
envelope leaves Go, Go has no say in how Python interprets it.
The contract says: "here is a trick; apply it to the state
and you will get a clean board." Python broke the contract by
applying a different trick than the one described.

If we want the consumer's correctness to be structurally
guaranteed, the contract shape has to change — primitives on
the wire, not compound diffs. Then "unpacking" isn't a step;
there's nothing to unpack.
