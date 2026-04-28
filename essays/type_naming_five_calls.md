# Type-naming policy — five binary calls

author: Claude
collaborator: Steve

**Status:** confirmed 2026-04-28. Rules 1, 2, 5 confirmed
as written. Rules 3 and 4 flipped per Steve's annotations
— see those paragraphs for the post-flip stance.

The function-naming policy
(`naming_policy_five_calls.md`) is verb-shaped; types
need a parallel set of rules because they're *usually*
nouns. Same format as that essay — each paragraph is one
decision, real example, my recommended pick + the
alternative.

**Important up front:** types default to nouns, but
verbs and adjectives can be evocative for the human
reader. `Pending`, `Validated`, `Stuck`, `RunningGame`,
`ExtractAbsorbDesc` all carry feel beyond what a pure
noun could. The rules below describe **defaults and
red flags**, not absolute prohibitions on non-noun
forms. Adjective-flavored types and verb-stemmed
compounds remain welcome where the evocation earns its
keep.

## 1. Plural type names: `Cards` for `List Card`?

Should we ever have a type alias `type alias Cards =
List Card`? My pick: **no — use `List Card` directly.**
Plural type aliases for collections rot when callers
reach for the underlying shape (they need
`List.map` etc.); the alias hides the type and saves no
characters that matter. Singular type names only:
`Card`, `Stack`, `Plan`. Alternative: allow plurals
when the collection has domain identity (e.g. `Hand =
List Card` is plural-meaning under a singular name —
fine, but `Cards` itself is forbidden).

## 2. Suffix style: `MoveDesc` vs `MoveDescription`

Compact suffixes (`Desc`, `Info`, `Cfg`, `Args`) vs full
English (`Description`, `Information`, `Config`,
`Arguments`). My pick: **full English.** `MoveDescription`
reads as natural language; `MoveDesc` is jargon.
Alternative: standard CS abbreviations are universal
shorthand and saving the keystrokes is worth it for
domain types that recur often. (Note: this policy might
churn the existing `*Desc` family — `ExtractAbsorbDesc`,
`FreePullDesc`, `SpliceDesc`, `ShiftDesc`, `PushDesc`.
Worth being aware of as scope.)

## 3. Compound order: `GestureEnvelope` vs `EnvelopeForGesture` — FLIPPED

**Stance after Steve:** **prepositions resolve ambiguity,
especially when the modifier doubles as a verb.**
"Gesture" is both a noun and a verb — `GestureEnvelope`
could mean "an envelope FOR a gesture" (noun reading) or
"an envelope that gestures" (verb reading). When the
modifier is verb-and-noun, reach for the prepositional
form: `EnvelopeForGesture`. When the modifier is
unambiguously a noun (or the verb-reading is absurd in
context), modifier-noun stays fine. The same precision
applies to compounds like `ReplayAnimation` (replay is
verb/noun → ambiguous), vs `BoardGeometry` (board could
be a verb but the verb-reading is absurd → unambiguous).
Plus a companion principle: **long names should be
smell-specific** — length is justified by a specific
reason (ambiguity, role-disambiguation, etc.), not used
gratuitously. A long name without a reason is itself a
smell signal.

## 4. Compound state types: `Buckets` vs `BucketsState` — FLIPPED

**Stance after Steve:** **`*State` suffix is better — it
establishes coding patterns (FSM).** The suffix tells the
reader "this type carries the state of a process,"
which is load-bearing for how an FSM-shaped algorithm
gets read. So `BucketsState` over bare `Buckets`,
`FocusedState` stays. Bare-noun naming is fine for types
that ARE-the-thing (`Card`, `Stack`, `Plan`); state
suffix is for types that REPRESENT-state-of-a-process.

## 5. Acronyms: `URL` vs `Url`, `ID` vs `Id`, `BFS` vs `Bfs`

Standard acronyms (URL, ID, HTML, BFS, JSON) — keep all
caps or Title-case as a word? My pick: **Title-case as a
word** (`Url`, `Id`, `Bfs`, `Json`, `Html`). Elm's
convention; reads as natural language inline (`Url.parse`
sounds like "url parse"; `URL.parse` sounds like "U R L
parse"). Alternative: caps for established acronyms
matches reader expectation in domains where the acronym
is a brand (e.g. URL, JSON). Costs the
reads-as-natural-language property for marginal recall
benefit.

---

After yes/flips, I dispatch the rule-checker tool-builder
sub-agent (cost-framed, open-ended). Type policy + function
policy both available to it as inputs.
