# Smells vs. Anti-Patterns

A common move in code review is to see a "smell" and
reflexively try to eliminate it. Belt-and-suspenders
validation; a constant in a surprising module; two functions
that look similar but aren't quite duplicates. The instinct:
smells should be removed.

The instinct is a category error. A smell and an
anti-pattern aren't the same thing.

## The distinction

An **anti-pattern** is a pattern that is wrong. It produces
bad outcomes. The remedy is to avoid or eliminate it.

A **smell** is a signal — a surface feature that *might*
indicate a problem. The remedy is to investigate. Sometimes
the smell turns out to be a real problem, and you fix it.
Sometimes it turns out to be intentional, load-bearing
design, and you leave it alone — with a note explaining why.

Both responses are valid. The invalid response is treating
the smell itself as the verdict, skipping the investigation
step, and refactoring on reflex.

## The discriminator

The question that separates a vindicated smell from an
unexamined one is always the same: *did anyone look at it?*

If yes, and the investigation revealed intentional alignment
— two validators checking the same invariant at different
scopes, say, or a constant deliberately co-located with its
most important consumer — the smell stays, documented, and
proud. If no, and the pattern was inherited from older code
that nobody can explain anymore, the smell is probably a
real problem and should be cleaned up.

The work is the investigation, not the conclusion.

## Why this matters

Treating smells as anti-patterns produces two failure modes
simultaneously. Smelly-but-correct code gets refactored into
something genuinely worse — the two checks got merged, and
now the invariant is enforced at one scope instead of two.
And actual anti-patterns get dismissed because "we thought
about this, it's fine" — without anyone having actually
thought about it.

Unexamined smells get eliminated; unexamined accidents get
preserved. The investigation is what keeps the two
straight.

## The practical move

When you see a smell, write down what you suspect it is.
Then go read the code. Then write down what you found. If
the pattern is load-bearing, the second note belongs in the
sidecar or a comment at the source so the next reader
doesn't reopen the question. If it's accidental, fix it.

Either way, you've earned the verdict. That's the work.
