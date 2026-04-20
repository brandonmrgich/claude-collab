# DSLs as Distillation

Most discussions of domain-specific languages are about
reuse: write a DSL when the same shape appears often enough
that the plumbing earns its keep. That's a fine reason to
write one. It isn't the interesting one.

The interesting reason to write a DSL is that designing the
DSL IS the distillation work — the act of figuring out what
the domain's primitives actually are. Every keyword choice,
every decision about what's a default vs. explicit, every
nesting rule forces the author to name what the problem's
vocabulary consists of. You can't hand-wave your way through
a DSL design; the grammar won't let you.

## What the plumbing used to cost

Historically, writing a DSL was expensive. You needed a
parser, a code generator or interpreter, error messages,
maybe a formal grammar, test coverage for edge cases. The
plumbing was so costly that DSLs were reserved for places
where reuse clearly justified the investment — build
pipelines, routing configs, SQL, regex. Fuzzy abstractions
that might have benefited from DSL-shaped thinking usually
didn't get it, because the cost of trying and discarding a
DSL was too high.

The plumbing-first cost structure made the DSL look like a
*deliverable* — something you ship because you're sure
you'll use it. Most ideas weren't ready to be delivered.

## The cost has collapsed

An agent can produce a parser, a generator, test coverage,
and error messages for a small DSL in well under an hour.
The plumbing has moved from "significant investment" to
"background task." What used to be half the cost of writing
a DSL is now almost free.

That changes what DSLs are *for*. They stop being
deliverables you justify by future reuse and become thinking
tools you reach for by default when an abstraction feels
unclear. The creative act — picking the vocabulary — is what
dominates the cost curve now, and the creative act was
always the valuable part.

## Why design reveals what code hides

Abstraction work is often described as "factoring out
commonalities." That framing hides the hard part: you have
to notice which commonalities are load-bearing and which
are accidental. Code doesn't force you to. You can write a
helper function, call it `doThing`, and ship the ambiguity.

A DSL can't do that. Every primitive needs a name. Every
field that's sometimes-required and sometimes-not needs a
default. Every concept that shows up in two places needs to
be called the same thing in both. The grammar is the
artifact that documents which concepts were actually
distinguishable. If you can't cleanly name a primitive,
that's a signal — the concept isn't ready, or you don't
understand it yet.

Sometimes the signal tells you to split a concept that
looked unitary. Sometimes it tells you to merge two concepts
that looked distinct. Sometimes it tells you the real
primitive is something neither of your first two drafts
included. The design pass is where these discoveries
happen, and code rarely forces them.

## The DSL might not survive

An important consequence of making DSL-design cheap: the
DSL doesn't have to survive. If you design one for a problem
and discover, through the design, that the problem is
actually simpler than you thought — or differently shaped —
you may not ship the DSL at all. That's fine. The artifact
was disposable; the thinking was the product.

This matters because it gives you permission to try DSLs
speculatively. You don't need to be sure the DSL will be
used. You only need to be sure the thinking will be useful,
which is almost always true when you're stuck on an
abstraction.

## A small working example

Imagine you're trying to describe what a "valid user
profile" is, and you've been pushing validation logic around
between views and services for months. The abstraction keeps
sliding.

Try writing a DSL for it. Force yourself to name:

- The required fields. (Do you have a `required` keyword?
  Or is everything required by default and you need an
  `optional` flag? Which default better reflects the
  domain?)
- The constraints on each field. (Length? Format? Enum?
  Relational?)
- The cross-field constraints. (Email domain agrees with
  employer? Country code agrees with phone format?)
- Who enforces each constraint. (Input-time? On save?
  Periodically, in a sweep?)

Fifteen minutes in, you'll notice that some of these
questions don't have good answers yet. The DSL is now doing
the work — it's surfacing which parts of "valid user
profile" are genuinely undefined. You may never ship the
DSL; you now have a list of concrete ambiguities to resolve,
which is worth more than any validation helper would have
been.

## How to start

The move is simple. Next time an abstraction feels unclear
and you find yourself pushing the same logic around between
modules, take ten minutes and write a DSL for what you're
trying to describe. Don't worry about the parser or the
generator — the agent can build those when they're needed.
Worry about the vocabulary.

Write the grammar. Write three example instances. Notice
which primitives you named cleanly and which you had to
fudge. The fudged ones are the real problem.

You might not keep the DSL. The thinking will have been
worth the ten minutes regardless.
