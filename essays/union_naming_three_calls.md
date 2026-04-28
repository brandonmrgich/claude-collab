# Union-type naming policy — three binary calls

author: Claude
collaborator: Steve

**Status:** confirmed 2026-04-28. All three rules
approved as written.

Companion to the function-naming policy
(`naming_policy_five_calls.md`) and the type-naming
policy (`type_naming_five_calls.md`). Both of those treat
type names individually; this essay covers the special
case of **union types** (Elm `type Foo = A | B | C`),
where the question isn't "is each constructor named
well" but "are the siblings *consistent with each
other*."

Same format — each paragraph is one decision, real
example, my recommended pick + the alternative.
Annotate each independently.

## 1. Word-class consistency: all verbs, or all nouns?

Within a single union, should every constructor share a
word class? My pick: **yes — pick verbs OR nouns OR
adjectives, don't mix.** A `Status = Pending | Validated
| Stuck` reads cleanly because all three are adjectives.
A `Status = Pending | RunValidation | Stuck` reads as a
type leak — `RunValidation` is a verb-noun and the
others are adjectives, so the constructors are at
different abstraction altitudes. Same logic for nouns:
`WireAction = Split | MergeStack | MoveStack |
PlaceHand` is consistent (all imperative verbs); adding
`UndoState` (noun) breaks the pattern. Alternative:
allow mixing when the union deliberately represents
multiple kinds — but flag with a comment so the reader
sees the intent.

## 2. Payload-shape consistency: all positional, or all record?

Sibling constructors of the same family should carry
their data in the same shape. Real example from
`Main/Msg.elm`:
`MouseDownOnBoardCard { stack, cardIndex } Point Float`
mixes a record payload with two positional values, while
`MouseDownOnHandCard Card Point Float` is all
positional. They're siblings (both are mousedown
events); the shape disagrees. My pick: **siblings share
shape.** Either both records (`MouseDownOnBoardCard
{ stack, cardIndex, point, time }` +
`MouseDownOnHandCard { card, point, time }`) or both
positional. The mixed form makes pattern-match call
sites asymmetric for no semantic reason. Alternative:
allow per-constructor shape choice when the data
justifies (record when the constructor carries 3+
named fields with no natural order; positional when
the order is canonical).

## 3. Prefix consistency: `MouseDownOn*` vs `MouseUp` bare

If two siblings share a prefix that names a
sub-pattern (`MouseDownOnBoardCard`,
`MouseDownOnHandCard`), the third sibling shouldn't
silently break the prefix scheme. My pick: **if 2+
constructors share a prefix that encodes a
sub-pattern, every sibling that fits the sub-pattern
should follow the prefix, OR the prefix should be
dropped entirely on those that don't fit, with a
comment.** `MouseUp Point Float` next to
`MouseDownOnBoardCard` and `MouseDownOnHandCard` is
ambiguous: is `MouseUp` a sibling of the
`MouseDownOn*` pattern (in which case it should be
`MouseUpOnBoard`/`MouseUpOnHand`), or does mouseup not
need the per-target distinction (in which case the
prefix scheme is lying about how the family is
organized)? Alternative: prefixes are documentation,
not enforcement — let constructors evolve organically
and re-name when the inconsistency causes real
confusion.

---

After yes/flips, the rule-checker tool gets extended
to detect within-union inconsistencies (3 new rules:
U1 word-class, U2 payload-shape, U3 prefix). The
existing 11 violations in `Main/` would also expand
slightly — `Msg.elm`'s mousedown-vs-mouseup
inconsistency is the obvious U2 + U3 candidate.
