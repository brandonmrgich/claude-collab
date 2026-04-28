# Naming policy — five binary calls

author: Claude
collaborator: Steve

**Status:** confirmed 2026-04-28. All five rules approved
as written. This is the canonical naming policy for
function names; a future-Claude reading this can treat
each rule as binding for the renaming pipeline and for
any new code authored under this collaboration.

Each paragraph below is one decision — a real example,
my recommended pick, and a one-sentence framing of the
alternative. Originally posed as binary calls; Steve
confirmed all five.

## 1. Fallible operations: `tryParse` vs `parseMaybe`

Should a function that may fail be named with an adverb
prefix (`tryParse : String -> Maybe Int`) or with a
Maybe-suffix (`parseMaybe : String -> Maybe Int`)? My
pick: **`try-` prefix.** The adverb telegraphs "this may
fail" *before* the reader gets to the return type.
`parseMaybe` is more Elm-stdlib-idiomatic (matches `head`
→ `headMaybe`) but reads as "parse a Maybe" which is
backwards. Alternative: stay with Maybe-suffix for
consistency with Elm-stdlib expectations.

## 2. Boolean predicates: `isClean board` vs `clean board`

A function returning `Bool` — should it have an `is-`
prefix (`isClean : Board -> Bool`) or be bare-adjective
(`clean : Board -> Bool`)? My pick: **`is-` prefix on
every boolean predicate.** Bare adjective is ambiguous
(does `clean board` clean it, or check?); the prefix
reads as a question. Same rule covers `hasNeighbors`,
`canMerge`, `wasModified`. Alternative: bare adjective
is shorter and Elm-stdlib uses both forms (`isEmpty` vs
`member`).

## 3. Spatial/transfer ops: `extractFromHelper card helper` vs `extractCard card helper`

When a function moves something between two named places,
should the preposition be in the name? My pick:
**explicit preposition.** `extractFromHelper`,
`mergeOntoStack`, `pushIntoBoard` make the source/target
relationship readable at the call site without checking
parameter order. `extractCard helper card` flips the
parameter order silently and the call site has to remember.
Alternative: shorter names + parameter ordering as
documentation.

## 4. List accessors: `firstMove plan` vs `head plan`

When the type has domain meaning, should helpers use the
domain name (`firstMove`, `lastMove`) or the generic
stdlib name (`head`, `last`)? My pick: **domain-named when
context exists.** `firstMove plan` reads as English;
`head plan` reads as code-jargon. Save `head` / `tail` /
`init` for genuinely-generic util functions like
`Main.Util.listAt`. Alternative: stick with stdlib names
for parity across modules — costs domain readability,
buys consistency.

## 5. Stateful booleans: `wasModified record` vs `isModified record`

For booleans that describe whether a state-change *has
happened* (vs current truth), should the prefix be `was-`
or `is-`? My pick: **`was-` for past events,
`is-` for current truth.** `wasModified` (an event has
occurred) vs `isClean` (state right now). The English
verb tense disambiguates the time-shape of the question.
Alternative: collapse both into `is-` for one rule
(`isModified` would mean "is in modified state") — costs
the time-shape signal, buys one less rule to remember.

---

After these five land, I'll scope the pipeline (which
files first, type names + variable names in or out of
scope, proactive rename vs only-on-touch).
