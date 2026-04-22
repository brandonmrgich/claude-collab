# What the Trick Invariant Test Needs to Verify

Today's bugs all share one signature: a trick emitter — the code
that turns a recognized trick into a primitive sequence — shipped
a sequence whose final board contained an incomplete stack. Not a
subtle rules violation; not an edge case; a straightforward "this
trick wrecked the board" outcome. Caught only during full-game
integration.

The test we're about to write exists so that class of bug can't
reach integration again. This essay is me stating precisely what
it should verify, before code gets written.

## The invariant

Every trick emitter in `hints.py` promises the following: if it
returns a primitive sequence for a given (hand, board) input,
then applying that sequence to the input must produce a board
where every stack is a valid complete group — a Set, a Pure Run,
or a Red-Black Run. No singletons. No 2-card pairs. No gap pairs
like `[9C, JC]`. No `Bogus`, `Dup`, or `Incomplete` stacks
anywhere in the result.

Stated as a contract: **tricks mutate legally and leave the
board clean.** If an emitter can't satisfy that on some input, it
must return `None` rather than emit a broken sequence.

## What the test feeds in

We don't enumerate every possible state. We curate
representative inputs — one per shape the emitter must handle —
and rely on the curation to cover the corners that have burned
us today or that naturally will.

Per trick, interesting inputs include:

- **Edge peels.** Target at position 0 or size-1 of a 4+ stack.
  One split suffices; remnant is exactly size-1.
- **Middle peels.** Target at an interior position where
  CanExtract allows (run with ≥3 on both sides, or 4+ set).
  Two splits required; both remnants must be valid.
- **Hand-composition variants.** For `pair_peel`, both set-pair
  and run-pair inputs. For `hand_stacks`, sets, pure runs, and
  rb runs. For `rb_swap`, kick-home candidates that are sets
  and pure runs.
- **Trick-specific constraints.** For `split_for_set`, hand-card
  color must match no board target suit. For `peel_for_run`,
  the trio value-sequence must be ascending.

The set doesn't need to be huge. Today's bug would have been
caught by one `peel_for_run` input. Tomorrow's will probably
surface from the next trick we audit.

## What the test checks

For each input:

1. Call the trick emitter with `(hand, board)`.
2. If it returns `None`, skip — the emitter legitimately refused
   (outside supported shapes, no valid play, etc.). That's not a
   failure.
3. If it returns a primitive sequence, **apply that sequence in
   order to the input state**. Use Go's remove-and-reappend
   semantics, same as the mini-sim already in `hints.py`.
4. For every stack in the final board: call `_classify`. Assert
   the type is one of `set`, `pure_run`, `rb_run`. If any stack
   classifies as `other` (i.e., Bogus / Dup / Incomplete /
   size < 3 that isn't part of a valid group), the test fails
   with a diagnostic: which trick, which input, which
   intermediate stack, and the full primitive sequence for
   inspection.

We don't check priority ordering. We don't check whether the
trick *should* have fired on that input (the cross-check against
Go already proved recognizers agree). We don't check physical-
fidelity versus human play. The single focus is the invariant:
**the board after the trick is clean.**

## What the test is not

Not a framework — no pytest, no unittest, no fixtures. Plain
Python with `assert` or explicit `raise AssertionError` on
failure. One file; reads as a script; runs in a second. This
keeps the test within the orbit of the code it checks and
prevents it from growing into infrastructure.

Not a filter. The test exists as a pre-merge gate for code
changes, not as a runtime guard around buggy emitters. If the
test fails, we fix the emitter. We don't paper over the failure
with a production-side silence.

Not exhaustive. A carefully chosen small set of inputs per trick
is the right size. If a new bug shape emerges that existing
inputs don't catch, we add one input and the test grows by one
entry.

## Why this scope, now

The bugs today were caught late because nothing was checking the
invariant between "emitter produced sequence" and "game ran the
sequence." A short assertion-style test sitting between those two
events catches them in isolation, where fixes are cheap and the
signal is clean. Full-game integration can still serve as the
final sanity check, but it shouldn't be where we first learn
that an emitter violates its contract.

The test we're writing is the piece we should have written
before the first trick emitter was written. Adding it now pays
back the tax we accumulated today — and prevents us from
accumulating it again as more tricks land.
