# LLM Economics

Before LLMs, one of the sharper paradigm shifts in software
engineering came from test-suite speed. If your tests took
50 seconds, you ran them on a schedule — after a batch of
changes, in CI, at end of day. If they took 1 second, you
ran them after every save. The difference wasn't linear.
Somewhere between those numbers a threshold got crossed, and
the entire workflow flipped: feedback-driven development
stopped being a ceremony and became an ambient condition.

The 50x speedup isn't what mattered. Dropping below the
threshold where the cost stopped interrupting flow is what
mattered.

LLMs are doing this, simultaneously, for about a dozen costs
in software engineering. That's the shift worth naming.

## The operations that dropped below threshold

Writing a small parser: was days, now minutes.

Producing a code generator: was a project, now a background
task.

Reading a 10,000-line codebase to find how a specific flow
works: was hours of focused attention, now a conversation.

Refactoring across multiple files: was risky manual work,
now mechanical.

Writing a first-draft essay or a decision doc: was a
half-day effort, now thirty minutes.

Generating test fixtures for an unfamiliar schema: was
annoying boilerplate, now free.

Maintaining per-file sidecar documentation as code changes:
was impossible in practice (nobody does it), now the default.
When a function gets renamed or a type refactored, the
adjacent `.claude` file updates in the same session, usually
the same commit. The half-life of documentation used to be
measured in weeks; the half-life is now "until next edit."

Each of these costs crossed a threshold. Taken individually,
each is a modest improvement. Taken together, they compound.

## Why compounding matters

When one operation drops below its threshold, you do more of
that operation. Run tests more often. Refactor more freely.
That's linear.

When *many* operations drop below threshold at once, the
workflow changes qualitatively. You can diagnose a bug,
*then* discover the underlying model is wrong, *then*
refactor the model, *then* watch the bug disappear and a
shelved UI feature land as a byproduct, *then* write tests
covering the new shape, *then* update the docs and sidecars,
*then* write an essay on the lessons — all in one afternoon,
because each individual step is now below the interrupt-flow
threshold. Previously this sequence was a multi-sprint
project; now it's an afternoon.

The compound effect enables workflows that were foreclosed
by the old cost structure. "Design a throwaway DSL to
sharpen your thinking" used to be absurd advice — the
plumbing made every DSL a commitment. Now it's a ten-minute
move. "Rip this subsystem and rebuild it cleaner" used to
require political capital; now the rip is cheaper than the
maintenance.

## The implication

Every assumption about what's expensive is potentially
stale.

Before LLMs, if someone said "let's generate per-file
documentation that stays current with the code," the honest
answer was "nobody maintains that; it'll drift in a week."
The economics made it impossible. After LLMs, the same
suggestion is reasonable. The economics changed.

Most software engineering intuition is built from pre-LLM
cost structures. You probably still have a reflex that says
certain things are too expensive to do — speculative DSLs,
aggressive refactors, comprehensive docs, thorough
exploration of alternative designs. The reflex was
calibrated against a cost structure that no longer applies.

The tactical move: when you find yourself flinching at an
idea because it "would be too much work," ask specifically
*how much work*, and whether your estimate was built on
pre-LLM intuitions. Often the answer is "less work than I
think, by a factor that crosses a threshold."

## Economics and ergonomics

This essay pairs with *The Ergonomic Gap*. They're two
faces of the same accounting question, and it's worth
naming them together — especially because the words come
from the same Greek root (*oiko-*, household management).
The two cost-axes go hand in hand.

Ergonomics asks, within a single moment of collaboration:
which party does each task cost less, *right now*? The
answer routes work spatially — this task to the human,
that task to the agent — based on who pays less retrieval
cost in this moment. Give the human the full URL; let the
agent look up the id from context; restate the next action
verbatim after a detour.

Economics asks, comparing against history: how expensive
is this task *now* versus how expensive it used to be? The
answer routes work temporally — speculative designs,
aggressive refactors, per-file documentation — based on
what recently crossed below threshold.

Both are cost questions. Both require noticing when a
stale assumption is driving the wrong routing. The
ergonomic failure mode is treating a cheap task as
expensive because it would have cost the human a lot
(retyping a URL from memory instead of asking the agent to
hand one over). The economic failure mode is treating a
newly-cheap task as expensive because it used to cost the
whole team a lot (refusing to propose a throwaway DSL for
an abstraction you're stuck on).

Same reflex. Different axes.

## What the compounding doesn't touch

Not everything gets cheaper. Judgment still costs what it
always cost. Deciding *which* refactor to do, *which* DSL
to design, *which* subsystem to rip — those decisions still
require a human who's been close to the problem. The agent
can execute any of them; the agent can't want any of them
more than any other.

The compounding frees up attention for judgment. What used
to be 80% mechanics and 20% judgment is now 20% mechanics
and 80% judgment. That's a good thing — judgment is where
the interesting work was all along — but it also means the
bottleneck hasn't gone away. It's just been relocated.

A related trap: because the mechanics are cheap, it's easy
to keep executing past the point where judgment should have
stepped in. Agents will happily refactor the wrong thing
for a full afternoon if you let them. The human's job isn't
gone; it's been distilled to the most expensive, least
mechanizable fraction of what it used to be.

## A running check

Next time you have an idea and immediately discard it as
"too much work," stop and list what actually has to happen.
For each step, ask: was this expensive before LLMs? Is it
still expensive now?

If many of the steps crossed a threshold, the idea is
probably cheaper than your reflex says. Consider trying it.
Compounding is how you end up doing things that were
impossible last year while not noticing you've done anything
unusual.
