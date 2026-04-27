---
name: Make state honest
description: A system's data shape should match what's actually true about reality. Wider-than-reality, narrower-than-reality, inventing reality, fragmented shapes — all symptoms of one principle violated.
type: feedback
originSessionId: 5a09deb5-8bd3-411c-844c-e6aa9a9b0122
---
# Make state honest

The data shape of the system should match what's actually true
about reality at the point that data is used.

That's the spine. Every cousin below is a violation of it, and
once you've named the spine, the cousins all collapse to one
diagnostic: **the shape disagrees with reality**. Fix the shape.

The four flavors of violation:

**Wider than reality.** The type carries a possibility (`Nothing`,
`NULL`, `Maybe`) that the local site has already ruled out.
Symptoms: defensive branches, "shouldn't happen by construction"
comments, `WHERE col IS NOT NULL` filters that scope to "the rows
of one kind," nullable columns that double the consumer
case-space.

**Narrower than reality.** The wire or the producer-consumer
boundary throws away information that actually existed. Symptoms:
inferred-back values where the producer already had them, lossy
telemetry that can't reconstruct what the user did, compound
forms that consumers must decompose to use.

**Inventing reality.** Vocabulary names a *designed response* as
a *recovery* — and the words shape what code gets written.
Symptom: phrases like "stuck-state recovery" attached to
conditions the system already has primitives for.

**Multiple shapes for one truth.** When reality permits two
representations (positional vs content, integer vs float, ordered
vs multiset) and we don't pick one, the shape isn't wider or
narrower — it's *fragmented*. The two representations drift, and
the bugs sit in the seam.

## Eight diagnostic phrases

Future-Claude doesn't need to recognize all eight by name. Future-
Claude needs to recognize when one of these is being said aloud
or written in a comment, and treat it as the alarm it is.

- "Shouldn't happen by construction."
- "This is fine because the catalog will have loaded by then."
- "Half these rows have it, half don't."
- "We need to know how to render this later." *(decision encoded in
  recording layer)*
- "The drag isn't visually meaningful so we don't capture it."
  *(lossy wire)*
- "B can re-derive this from A's output." *(inference between
  same-owner components)*
- "Stuck-state recovery." *(phantom problem; the system already
  has the response)*
- "Approximately equal" / "close enough" / "either ordering."
  *(fragmented shape)*

## What this isn't

Some honest exceptions, lest the principle become a hammer.

**Cross-language boundaries** are genuinely partial. JSON parsers
produce a `Maybe` because the boundary is genuinely partial —
that's the type being honest, not too wide. Defensive handling
there is correct.

**Display-layer compounds** can compress for human ergonomics. A
"your turn ended successfully" notification doesn't enumerate the
seven primitives that made it true. But the primitives stay on
the wire, available to consumers that need them. Compression at
display; truth at the record.

**Same-kind-rows-with-no-value** are fine to NULL. A
`gesture_metadata` column is NULL for non-pointer actions because
those actions don't have gestures — same row kind, just no
gesture. The discriminator is the action kind, not the NULL. The
diagnostic test: would you write `WHERE col IS NOT NULL` to scope
to "the rows of one kind"? If yes, you're back in violation. If
no, you're fine.

The principle is "make state honest about reality" — not "make
state maximally rigid." There's no shame in modeling a true
ambiguity. The shame is modeling an ambiguity that doesn't exist
at the call site.

## The fix is always the same fix

Change the shape. Not the comment, not the inference layer, not
the recovery path. The shape.

When a defensive branch shows up: where does my type say
something that reality contradicts? When a NULL column shows up:
is this column actually two columns welded together? When
component B has to decompose A's output: what does A know that
I'm asking B to recover?

## Origin

Eight moments between 2026-04-20 and 2026-04-26 named the
corollaries. Searchable under FLOATER_TOPLEFT, ELM_AUTONOMY, the
ELM_AGENT_CATCHUP work, and Steve's framings on
record-facts-decide-later. The origin matters less than the
principle.
