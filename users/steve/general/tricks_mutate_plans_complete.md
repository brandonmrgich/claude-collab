# Tricks Mutate; Plans Complete

A surprise landed today: the agent played 29 primitives of a
full game and got stuck at `complete_turn`, with two 2-card
pairs stranded on the board. The natural reaction — yours,
and my first one — was *"a trick that creates an incomplete
pair is not a trick, it's a wrecking move. How did we ever
decide that was a good trick?"*

The answer turns out to be more interesting than "we shipped
a bug." The trick system IS protecting the invariant. The
pairs came in through a different door entirely. The whole
episode points at a vocabulary ambiguity that's been hiding
in plain sight.

## What the trick code promises

Here is the rule that controls whether a card can be peeled
out of a board stack (`games/lynrummy/card_stack.go`,
method `CanExtract`):

```go
func (s CardStack) CanExtract(cardIdx int) bool {
    size := s.Size()
    st := s.Type()

    if st == Set {
        return size >= 4
    }
    if st != PureRun && st != RedBlackRun {
        return false
    }
    if size >= 4 && (cardIdx == 0 || cardIdx == size-1) {
        return true
    }
    if cardIdx >= 3 && (size-cardIdx-1) >= 3 {
        return true
    }
    return false
}
```

Read in plain English:

- A SET is extractable only when it has **4+ cards**. A 3-set
  is sealed — you can't peel from it.
- A run is extractable from its **ends** only when it has 4+
  cards.
- A run is extractable from the **middle** only when both
  halves post-split would have 3+ cards.

Every trick that peels cards from the board (`split_for_set`,
`pair_peel`, `peel_for_run`, `rb_swap`) routes through
`CanExtract`. The invariant it encodes: **no extraction can
ever leave a pair (2-card stack) behind.** If taking this card
out would leave a pair, the extraction isn't offered.

So the trick system IS guarding the invariant. A `split_for_set`
on a 3-set of tens would leave a pair of tens — and the rule
refuses it. No split_for_set hint ever fires on a 3-set.

## So where did the pair come from?

I simulated session 22's action log step by step, watching for
the first moment `[TD, TS]` (the ten-diamond + ten-spade pair
that wedged the game) appeared as a 2-card stack. It showed up
after a `merge_hand`:

```
*** TD+TS pair appeared at stack[7] after:
    merge_hand {"hand_card": {"value": 10, "suit": 2,
                              "origin_deck": 1},
                "target_stack": 7, "side": "right"}
```

The pair was **built**, not left behind. A previous action had
isolated a 10 on the board (legitimately, following CanExtract),
and this merge added a second 10 from the hand onto it. Two
tens. Mid-turn, this is fine. At turn-end, it's incomplete.

The intent was probably: isolate a 10, merge a 10 from hand,
then add a third 10 and complete the set. Steps one and two
happened; step three didn't. The hand ran out of relevant
cards; no follow-up hint fired; the agent called
`complete_turn` too early.

So the trick system isn't at fault. The individual moves were
all legal. The failure mode is **a sequence of legal moves
that doesn't add up to a completable turn** — and the greedy
"take the first hint" strategy doesn't look ahead far enough
to avoid it.

## The vocabulary ambiguity

This is where your meta-point lands. The word "trick" has been
carrying two different meanings, and most of our confusion
today traces to conflating them.

**Definition A (strong, invariant-completing).** A trick is a
sequence of moves that leaves the board in a turn-completable
state: valid stacks only, no pairs, no singletons.

**Definition B (weak, legal-mutation).** A trick is a quick
way to mutate the board — a shape-named operation — in the
hope that later mutations will bring things home. Each trick
is legal in isolation but doesn't promise anything about the
final board shape.

LynRummy's current implementation is firmly Definition B.
`CanExtract` keeps each trick legal. Nothing keeps the
*sequence of tricks* from ending at an uncompletable state.
The turn-complete check is the only referee layer that sees
the final board, and it runs *after* you've decided you're
done.

Both definitions are legitimate. If we want Definition A,
tricks would need to be *conditional* — fire only when there's
a known path to completion. That's a bigger planner. If we
stick with Definition B, we need a planner outside the trick
system that asks "if I take this trick now, can I still
finish the turn?"

Human play uses the Definition B system **with undo as a
first-class play mode.** People don't actually look ahead
perfectly before every move. They rearrange cards in the hope
of finding a play — and when the hoped-for play doesn't
materialize, they put the cards back. Undo isn't an emergency
exit; it's part of how a turn gets explored. The referee only
judges the board at `complete_turn`, so any sequence of moves
that gets undone before that point costs nothing.

The agent doesn't do this. Its strategy is *take the first
hint, execute it, call complete_turn when hints run out.* No
undo, no exploration. When it builds a pair on the board in
hope of completing a set, and no third card shows up, it's
stuck with the pair. A human would have returned the built
pair to its previous shape and tried something else.

## Where the fix belongs

Given Definition B semantics and the way humans actually play,
the fix is agent-side: **make undo a first-class strategy.**
The loop becomes:

1. Get hints.
2. If hints exist, take the first, execute its primitives.
3. Loop.
4. If no hints and `complete_turn` is legal, end the turn.
5. If no hints and `complete_turn` is NOT legal (incomplete
   stacks on the board), **undo back to the last decision
   point and try a different hint.**

This mirrors what a human player does without any lookahead at
all. It doesn't require the agent to predict the future; it
only requires the agent to react correctly when the future
arrives empty-handed. Undo is already a first-class wire
action. The wire captures it faithfully. The referee collapses
it at complete_turn. Using it at play time is using the
mechanism the system already provides.

Alternative shapes (lookahead, hint-side reachability filtering,
etc.) are all heavier, and they all try to predict what undo
handles reactively. The human model is lighter.

## What this means for the overall architecture

The discussion from earlier today (hints go client-side)
survives this unchanged. The vocabulary adjustment is: the
agent's responsibility now explicitly includes **not just
executing tricks, but exploring-and-undoing until a
completable turn is found.** The trick library is a legal-
moves oracle; the agent is the explorer.

This also restores intelligence to the word "agent." The
current auto_player is, strictly, *an agent without the undo
reflex* — a consumer of ranked suggestions with no ability
to recover from dead ends. A competent LynRummy player has
the undo reflex built in.

## The takeaway

Nothing in the trick system is wrong. The surprise came from a
mismatch between what "trick" sounded like it promised and
what it actually guarantees. Named precisely: tricks mutate
legally; undo restores; turns complete only when the board
supports it.

The smallest fix: teach the auto_player to undo when it hits a
dead end. That's not a new mechanism, it's the one humans
already use, and the wire already supports it.
