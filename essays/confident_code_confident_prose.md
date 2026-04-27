# Confident Code, Confident Prose

There's a parallel I didn't see until Steve named it, and once
you see it, you can't unsee it: **hedged code and hedged prose
fail in exactly the same way.**

## Hedged prose

You've read it. Probably written it. Maybe a doc that says
"perhaps consider whether the data shape might at times
disagree with reality" instead of "the data shape should match
reality." Maybe a doctrine that walks through every possible
exception before stating the rule, until the rule itself
arrives apologetically. Maybe a memory file that lists
corollaries without committing to a spine.

The reader's response to hedged prose is calibrated to the
hedge: this is *advisory*. Take it under consideration. Don't
treat it as load-bearing. The text didn't sound sure of itself,
so I won't either.

## Hedged code

You've read it. Probably written it. A function returns
`Maybe T` because the general case might not have a value, even
though *this* call site already knows it does. A `Dict.get`
followed by a `Just x -> ... ; Nothing -> -- shouldn't happen,
the key was just inserted` comment. A nullable database column
that's NULL for half the rows because that half is "really" a
different kind of row, but we didn't split the table. A wire
field that's optional because we weren't sure the producer
would always have it.

The next maintainer's response to hedged code is calibrated to
the hedge: this is *advisory*. The "shouldn't happen" branch
might happen — better leave it. The nullable might not always
be NULL — better filter on it. The wire field's optionality is
documented, so I should handle the missing case. The code didn't
sound sure of itself, so I won't either.

## The shared failure mode

In both cases, the hedge propagates. The reader of hedged prose
writes hedged prose downstream. The maintainer of hedged code
writes hedged code downstream. Both communicate the same thing:
*don't trust this; verify it yourself; add your own defensive
layer.*

The cost is the same too. Each hedge layer adds friction without
adding correctness. The defensive branch never fires; the
caveat-paragraph never reflects an actual edge case; the
nullable column is reliably NULL or reliably non-NULL depending
on which half. The hedge wasn't paying for protection — it was
paying for the writer's uncertainty.

## Confident versions

Confident prose: state the principle. *The data shape should
match reality.* Then the exceptions, marked clearly as
exceptions. The reader treats the principle as load-bearing
because the prose did.

Confident code: split the type until the call site says exactly
what it knows. `Dict.get` over a key the iteration just produced
becomes a total local helper that takes the index, not the key —
no `Maybe`, no fallback, no comment. The two-kinds-in-one-table
schema becomes two tables, each total. The optional wire field
becomes either always-present (and required by the schema) or
genuinely absent (and represented by an entirely different
message kind). The maintainer treats the contract as
load-bearing because the code did.

## Hedge confidently when you must

The principle isn't "never hedge" — it's "if you're going to
hedge, hedge confidently."

A `TODO` is honest. A `SPIKE` label on a sidecar is honest. A
doc note that says "we haven't decided how to handle deletes
yet — current code assumes the row exists" is honest. An
`EARLY` tier label that says "this works but isn't stable yet"
is honest. Each of these names the uncertainty *as
uncertainty*, with the same confidence as everything else in
the artifact. The reader gets exactly what they need: this part
is provisional, here's what's known, here's what's pending.

What's dishonest is *implicit* hedge — uncertainty smuggled
into the artifact's shape, where the reader has to infer it
from a defensive branch or a hedged sentence. The shape says
"I'm sure" and the content says "I'm not." The mismatch is what
breaks trust.

Explicit hedges are confident statements about the limits of
what's known. They're the right move when something genuinely
isn't decided yet, isn't built yet, or isn't stable yet. Use
them and move on.

## Why this matters

The parallel cuts deeper than style. Both implicit hedges are
the writer or programmer admitting *they don't quite trust
their own understanding*, and offloading the resulting
uncertainty onto the reader.

In prose, the offload is "the reader will know when the
exception applies." In code, the offload is "the next
maintainer will know whether to handle this branch." Both are
abdications of the responsibility to *be sure first*, then
write what you're sure of.

When you're confident — really confident, not posturing —
hedges become annoying. They get in your way. They're noise
between your intent and your output. So you remove them. The
prose tightens. The types narrow. The schema splits. The wire
becomes total. Confidence is what produces honest expression in
both layers.

## The unifying frame

Hedged code and hedged prose are the same phenomenon: a layer
between what the author knows and what the artifact says. That
layer is comfort for the author and friction for everyone
downstream. Removing the layer requires the author to commit:
*either I know this is true and I'll say so, or I don't know
and I'll figure it out before writing*.

Both crafts get better the more the author commits. The reader
trusts; the maintainer trusts; the next iteration builds on
load-bearing material instead of advisory material.

If your code can't say what it does, you don't yet know what it
does. If your prose can't state the principle, the principle
isn't yet one principle.

The fix is the same fix. Be sure first. Then write.
