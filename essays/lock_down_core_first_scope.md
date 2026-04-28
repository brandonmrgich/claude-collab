# Lock down the core — first-scope decisions

author: Claude
collaborator: Steve

**Status:** confirmed 2026-04-28. All five rules approved
as written.

The volatility-class memory (2026-04-28) identifies five
classes from stable to volatile: rules → primitives →
physics → UX cadence → layout. Class 1 + 2 (the truly
locked-down stuff: card successors, merge rules, stack
classification) is the natural first scope to actually
segregate. Below: five binary calls for the FIRST run.
Annotate yes/flip per paragraph.

## 1. Directory name: `Game/Rules/`

My pick: **`games/lynrummy/elm/src/Game/Rules/`.** Names
the volatility class directly: this is where rules live.
"Rules" carries domain meaning ("Lyn Rummy rules") AND
volatility meaning ("things that don't change"). `Lib`
is too generic — every project has a Lib; nothing about
the name says "this is the locked-down truth layer."
`Core` is CS jargon. Alternative: stay with `Lib`
because it's a familiar shape and lets us mix domain
+ utility modules under one roof.

## 2. First migration set: `Card`, `StackType`, plus successor + classifier helpers

My pick: **`Game.Card`, `Game.StackType`, plus the
small free-standing predicates that operate on them
(card successors, neighbors, isLegalStack, isPartialOk
where they live today).** Minimal beachhead. These are
the most clearly Class-1 modules; `Game.CardStack` is
adjacent but the BoardCard wrapper has presentation
state (`FreshlyPlayed`) which is closer to Class 3-4.
Alternative: include `Game.CardStack` for completeness —
a single CardStack module is conceptually one of the
foundation primitives even if its inner state has UI
flavor.

## 3. Lock-down test pass: audit + add property tests AS PART OF the move

My pick: **as part of the move, audit existing tests
and add property tests for the laws that should never
break.** Examples: "every card has exactly N
successors," "neighbors are a stable shape per
(value,suit)," "isLegalStack is invariant under stack
order for sets," "isPartialOk is monotonic in stack
length up to 3." This is the testability dividend the
volatility memory predicted; cashing it in at migration
time is cheaper than scheduling a follow-on plan.
Alternative: pure migration first, test-pass as a
separate follow-on plan — risks the test work never
happening.

## 4. Python parallel: Elm first; Python follows

My pick: **migrate Elm only in this first run; Python
follows once the shape proves out.** The Python side
has its own structure (`cards.py`, `buckets.py`, etc.)
with different idioms; trying to lock both languages'
core in one plan doubles the risk surface. Validate the
shape in Elm (Class 1 boundary, test discipline,
import-rewrite tooling), THEN repeat for Python with
the lessons learned. Alternative: do both languages at
once for true cross-language parity — the shapes might
diverge if migrated separately and have to converge
later.

## 5. Import shape: aliases, not full-qualification

My pick: **`import Game.Rules.Card as Card`** so
existing call sites read identically (`Card.value`,
`Card.successor`). Preserves the natural domain prose
in signatures and pattern matches; doesn't churn every
file when the only change is the import path. The
volatility-class principle is about WHERE code lives,
not how it READS at the call site. Alternative: fully
qualify (`Game.Rules.Card.value`) so reading any module
makes the volatility-class explicit at every call —
costs verbosity at every site, buys an always-visible
class hint.

---

Tooling already in place:
- `cmd/reorg` (Go) for the directory move + import
  rewrite — used 2026-04-27 in the Lab → Puzzles
  rename, proven shape.
- `elm/check.sh` enhanced today (test count + elm-review
  surfaced) is the validation gate.
- `check_naming.py` exemption mechanism + multi-file mode
  ready if naming policy comes into play during the move.

Plan-executor shape (after sign-off): probably 3 phases —
discovery (call-site map for the in-scope modules), move
(reorg + import rewrite), test-lock (audit + property
tests). All Tier A except the test-lock step which has
real design-of-properties choice (Tier B).
