# Hints, Tricks, and the Wire: Where the Lines Go

The LynRummy hint/trick surface looks simple from outside —
"recognize a move, recommend it, play it" — but it crosses
three codebases with different jobs, and most of the bugs
we've stepped on today trace back to the same root: unclear
lines between those jobs. This essay enumerates the problems
I now see, names the invariants that resolve them, and draws
the responsibility lines that should have been drawn from the
start.

## The three codebases

Steve named the split clearly: **Elm is for the human. Python
is for the agent. Go is for the wire.** Each has slightly
different concerns, and each gets into trouble when it tries
to carry the others' concerns.

- **Elm** is where a human's hands meet pixels. Its primary
  customer is a human player; its secondary job is making
  sure every physical gesture that human produces lands on
  the server faithfully.
- **Python** is the agent's executor. Its primary customer is
  the server (it sends what a human would send). Its job is to
  produce primitive wire actions that the server can't tell
  apart from human-produced ones.
- **Go** owns the wire protocol and the referee. Its primary
  customer is future-Go-reading-its-own-log: the wire must
  reconstruct every game deterministically from a series of
  primitive actions.

These are not the same customers. Conflating them is the root
trouble.

## The distinction that matters: trick vs primitive

A **trick** is a semantic unit. "I'm doing a pair-peel." "I'm
doing rb_swap." The trick is how a human *thinks* about a move.
It carries intent.

A **primitive** is a physical unit. "I clicked card X in
stack Y." "I dragged hand card Z onto stack W." The primitive
is what the hand did. It carries execution.

These are not the same kind of thing. A trick is one-of-seven
(in our current recognizer set). A primitive is one-of-six
(`split`, `merge_hand`, `merge_stack`, `place_hand`,
`move_stack`, plus `complete_turn` / `undo`). A single trick
decomposes into between one and five primitives depending on
which trick and which board geometry.

The critical consequence: **the wire cannot carry tricks.** A
trick is not something a human *does*; it's something a human
*did, summarized*. Recording summaries on the wire is lossy
and asymmetric — no sequence of physical events produces a
single "trick_result" atom, so recording one means the wire is
carrying fiction.

`trick_result` was a relic of the early import design, when
the server was expanding higher-level recommendations into
diffs server-side. It should have been deleted the moment the
decomposition moved to the client. It wasn't, and so the
compound form has been leaking through the wire and forcing
clients to reverse-engineer it — exactly the "inference is
misplaced work" anti-pattern.

## Many paths, same outcome

For any given trick-intent, there are many primitive sequences
that realize it. This isn't sloppy play; it's the structure
of physical execution.

**Card-placement order is arbitrary for set-style tricks.** If
you have 4H + 4S + 4D in hand and you want to form a 4-set on
the board, the first card you place can be any of the three;
the remaining two can land in either order. Human choice is
driven by field of vision, mouse starting position, habitual
top-to-bottom scanning — none of which are algorithmic signal.

**Split direction is arbitrary.** Isolating a middle card can
be done right-first (peel off the tail, then peel off the
target) or left-first (peel off the head, then peel off the
target). Either produces the same final state.

**Merge `side` is arbitrary for sets, deterministic for runs.**
Adding a 4H onto a 4-set: left or right is equivalent. Adding
a 7H onto an 8-9 run: it has to go on the left. The wire must
faithfully record which side was used; the equivalence-checker
must know that for sets, the choice was free.

**Pre-placement is optional.** Sometimes after a split, the
isolated card is already in a usable spot; the human merges
onto it without first moving it. Sometimes the card is cramped
and a pre-move is needed. A comparator that demands "always one
move_stack" is wrong; it has to accept 0 or 1.

**Loc coordinates are imprecise.** When a human drops a stack,
they land it *somewhere* on an open region. Two humans — or
the same human two runs later — land it at different pixel
coordinates. The wire records the actual landing; equivalence
treats any geometrically-valid landing as the same.

**Geometry can force route changes.** If the direct path from
"split this card" to "land it here" is blocked by another
stack, a human will route around with pre-clearing moves. The
decomposition depends on the current board, not just the
trick.

These arbitrariness axes are real, plural, and entangled. No
single canonical primitive sequence exists for most tricks.
Any system that demands canonicity will either constrain the
human unnaturally or fail to recognize valid alternatives.

## The wire: primitives only

The resolution to "trick vs primitive" and to the lossless-wire
principle is the same sentence: **the wire carries only
primitives.** A wire action corresponds to exactly one
physical event the user produced, and its `gesture_metadata`
captures the raw pointer samples or click timestamps that
generated it.

This is what makes Instant Replay work, what makes behaviorist
drag-study work, what makes the log auditable. Remove
primitives, and you lose the ability to reconstruct the game.
Add non-primitives, and you lose the ability to trust what you
see — was that a single atomic "trick_result" or did a human
actually do something that looked like it?

Therefore: `TrickResultAction` should not exist in
`wire_action.go`. It should not exist in Elm's `WireAction.elm`.
It should be deleted from `ApplyAction` and its Elm
counterpart. The type existed because of an older architecture
where server-side trick-expansion was a thing; that
architecture is gone. The type is a relic and it's forcing
bad downstream code.

## Elm's job

Elm is where physical gestures originate. When a human clicks
or drags, Elm captures every pointer sample, packages a
primitive `WireAction`, attaches the `gesture_metadata` path,
and posts it. The wire round-trips exactly what the hand did.

Elm **displays** hints — a description and a set of
highlighted hand cards — but does not execute them. The human
reads the hint and decides; the hands do the execution. If the
human follows the hint, their drags produce the same primitives
the agent would have produced (modulo arbitrariness).

Elm does not decompose anything, because the human is doing
the decomposition with their hands. Elm does not need to know
what a trick is at the wire level.

Elm's Instant Replay reads the primitive log and animates each
primitive's gesture. No compound actions, because there are
none.

## Python's job

Python is the agent. The agent's contract with the server is:
produce primitive wire actions, with plausible gesture
telemetry, such that the server cannot distinguish agent
plays from human plays by looking at the wire.

The agent receives suggestions from `/hint`. Each suggestion
should already be a primitive sequence (computed server-side
by the trick's Play). The agent sends each primitive, one at
a time, attaching a synthesized gesture path per primitive.

The agent does not decompose. The agent does not infer. The
agent does not turn one compound form into another. If the
suggestion is already primitive, there is nothing to unpack.
If it isn't, the problem is upstream.

The agent *does* synthesize telemetry — the Phase-3 work we
haven't done yet. That is not inference; it is execution
fidelity. An agent has no physical hands, so it simulates
what hands would produce.

## Go's job

Go holds the wire format, the referee, and the hint system.

**Referee**: validates `complete_turn` (geometry + semantics).
The referee doesn't care about tricks; it cares whether the
board is in a valid completed state.

**Wire format**: stores primitive `WireAction` rows, each with
optional `gesture_metadata`. A session is fully reconstructed
by applying its primitives in order to an initial state. No
compound forms.

**Hint system**: recognizes tricks from `(hand, board)`, and
for each, produces a primitive sequence that realizes the
trick on the current board. This is the one place where
trick-semantics and primitive-execution meet, and the
translation happens here because this is where both sides are
known. The output of `/hint` is a list of suggestions, each
containing the trick_id + description + highlighted hand
cards + the canonical primitive sequence.

Internally, each trick's `Play` has a `Primitives(board)`
method that produces its decomposition. The trick owns its
own physical manifestation; no inference layer stands between
the trick's semantics and its primitives.

## Where decomposition lives

With this split, decomposition lives where the producer is:
inside each trick's `Play` in Go. `split_for_set.go` knows
how `split_for_set` is physically executed. `rb_swap.go` knows
the same for its trick. The knowledge doesn't leak upward or
downward.

Python doesn't need a `decompose_trick_result`. Elm doesn't
need a `TrickResult` variant. Both exist today and both should
be deleted.

## Where geometry lives

Layout decisions ("where does this new stack go?") live with
whoever is placing. For humans in Elm: the human places by
dragging. For the agent in Python: the agent calls
`find_open_loc` or equivalent before posting a primitive. For
the hint system's *suggested* primitive sequence: Go computes
locs using its own `FindOpenLoc` over the current board so
the suggestion is immediately executable.

Different clients might choose different locs; the wire
records whichever one actually landed. The referee only cares
that whatever landed was legal.

## Testing equivalence

Once we accept that many primitive sequences realize one
trick, testing needs a notion of equivalence looser than
literal sequence equality.

The strongest notion is **outcome equivalence**: apply both
sequences to the same initial state; the resulting states
(board, hand, score) are equal. This handles every
arbitrariness axis uniformly, including ones we haven't
thought of, because it checks the endpoint rather than the
path.

A cheaper notion is **structural equivalence**: the multiset
of primitive kinds matches, the set of cards touched matches,
the order of structurally-constrained steps matches (e.g.,
splits come before merges). This is what our current
comparator does. It's fast and readable but requires
per-trick rules and won't catch valid alternatives we didn't
anticipate.

For regression tests, outcome equivalence is the safer
default. Structural equivalence is useful for diagnosing
which primitive broke, when one has broken.

## Pitfalls we've stepped on

Each of the bugs we hit today traces back to one of the
invariants above:

- **`trick_result` as a wire action** violates "wire is
  primitives only."
- **`decompose_trick_result` in Python** violates "inference
  is misplaced work" — the producer should emit what the
  consumer needs.
- **Missing split telemetry** violated the lossless-wire
  invariant — clicks are physical events too.
- **Replay-baseline mismatch for puzzle sessions** violated
  the same invariant from a different angle — the wire had
  the right data, but a downstream endpoint didn't consult
  it.
- **Strict side-matching in the comparator** violated the
  arbitrariness principle — for sets, side is free.
- **Strict-order multiset checks** violated the same — the
  order was part of the arbitrariness.

The pattern: every pitfall came from a responsibility being
carried in the wrong place, or from a rule being tighter than
reality warranted.

## The synthesis

Three codebases, three jobs. Elm for the human's physical
gestures. Python for agent execution. Go for the wire and the
ground truth.

The wire carries primitives only. The hint system emits
primitive sequences directly. The agent executes what it
receives without reinterpretation. The human drives their own
primitives. Equivalence-checking is a testing concern, not a
wire concern.

Anything that violates these lines — a compound on the wire,
inference in a client, a decomposer reaching across
codebase boundaries — is a design defect, and usually pays
for itself several times over in downstream bugs before we
catch it.

We are one refactor away from having these lines drawn
cleanly. The essay exists so that when we do the refactor,
we're working from a shared picture rather than inferring
each other's mental model move by move.
