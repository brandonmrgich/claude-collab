---
name: Eliminate, don't paper over
description: When code feels contorted or redundant, the discomfort is information about the shape. Change the shape, not the adapter. Eight corollaries, one spine.
type: feedback
originSessionId: 5a09deb5-8bd3-411c-844c-e6aa9a9b0122
---
# Eliminate, don't paper over

When code feels redundant or contorted — when you're adding
adapters, range arithmetic, translation layers, defer-this-
until-later branches, "shouldn't happen" comments — the
discomfort is *information about the shape*, not noise to wrap
an adapter around. The remedy is structural. Change the shape,
then watch the discomfort disappear together with the code that
surrounded it.

Eight corollaries. They split along two axes: collapsing local
shape (1-4) and aligning cross-component shape (5-7). The
license that makes them actionable lives at the bottom (8).

**1. Simplify before patching.** When Steve names an invariant
in plain English, treat it as a *simplification target*, not a
spec to implement on top of what's there. The diagnostic before
any patch: does this invariant let me *delete* code? If yes,
that's the work. Patching without deleting is a smell. When a
bug has taken multiple rounds of fix-then-new-bug, stop and
re-read what Steve said about the invariant — the current
architecture probably doesn't match it, and another layer just
joins the queue.

**2. The right model delivers features for free.** If a model
refactor unlocks a shelved feature trivially, the new model is
in the right shape. Features that were hard before were usually
hard *because of* the model, not the feature. Conversely, if a
feature feels surprisingly painful to wire up, the model is
telling you something — don't force it into the old shape.

**3. Eliminate round trips, don't defer them.** When a server
holds data the client will need, ship it ALL in the initial
payload. Lazy variants feel like an improvement but still leave
the round-trip latency, the in-flight error handling, the
"loading" state, and the UI gating. At small scale, ship once
and operate fully client-side after that.

**4. Slices over indices.** When two callers walk different
windows of the same list, prefer giving each its own slice over
threading start/stop integers. The integer-range form leaks
"everyone consumes the canonical store" into modules that
shouldn't know it exists. At Lyn Rummy scale, copies are cheap;
cognitive cost of decoding range arithmetic isn't. Trust copies
when the data is small.

**5. Capability gaps can dissolve.** When porting code and
hitting an apparent capability gap in the target language, ask
whether the source is using its API for the *behavior* or as a
workaround for *its own architectural constraints*. If the
latter, the target's natural shape may not need the API at all.
Not every gap dissolves — touch events, DOM measurement, GPU
access stay real — but check before paying the interop cost.

**6. Refactoring surfaces assumptions.** During refactors, when
deciding "does this concept belong in module X or Y?", surface
the question to Steve rather than picking silently. The Q&A is
half the value. Don't rush to clean compile without giving
Steve a chance to catch a categorization mistake.

**7. Translation layers are alarms.** The wire format is a
projection of core types, not a separate model. Reading from the
wire is decode + fold — not transform, adapt, or translate. If a
`fromWire_*` function does more than a direct field-rename, the
wire shape is wrong, the core type is wrong, or both. Symptoms:
helpers that "massage the wire shape into what the core really
needs," branches that synthesize missing data per kind, comments
saying "X on the wire corresponds to Y here." Translation
helpers at *one* boundary are fine; the bug surface grows when
translation is sprinkled into every consumer. Two axes where
translations silently accrue: geometric frames (pick one, stay
in it) and terminology (no excuse for `TooClose` to encode as
`"crowded"` — we control the wire format).

**8. The license: I own the whole system.** Every corollary
above relies on this. Elm, Go, Python, wire format, DB schema —
all of it is mine to reshape. When two sides disagree, the
constraints are mine to redraw. The diagnostic question at every
decision point: do I have enough data here to give the user the
best experience? If yes, proceed. If no, is this **intrinsic**
(unknowable at this point — another instance's viewport, future
events) or a **wire problem** (the data exists but I never asked
for it to be sent)? Intrinsic → fallback / synthesis / "I don't
know" mode. Wire problem → fix the wire. Don't paper over a
deficit I caused.

## The diagnostic

Discomfort in the code is information about the shape, not noise
to wrap an adapter around. If you find yourself adding a layer —
a step counter, a translation helper, a defer-this-until-later,
a defensive comment — stop. The discomfort is telling you
something the comment can't reach.

## How the spine fits together

Local feels contorted → collapse: delete code, don't add it.
Cross-component shapes feel out of phase → reshape: change one
side or both until the translation falls away. The license is
mine. Treating the contract as immutable is the failure mode
that turns the cross-component corollaries into wishes instead
of moves.

## Origin

Eight moments between 2026-04-13 and 2026-04-26 named these
corollaries — refactor experiences, port experiences, two
different round-trip eliminations. Searchable in git history
under labels FLOATER_TOPLEFT, REPLAY_TURNS, ELM_AUTONOMY,
LAB_AGENT_PLAY, and the simplify-before-patching geometry chase
of 2026-04-20. The origin matters less than the principle.
