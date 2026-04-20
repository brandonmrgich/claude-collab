# Ebb and Flow

Collaboration isn't a steady state. It has a natural rhythm
between two modes — zooming in on the specific and zooming
out to the strategic — and most of what feels like
miscommunication between collaborators is actually a
mismatch about which mode is currently in play.

## The two modes

**Zoom in**: I'm editing one file, one function, one
paragraph. My attention is narrow and my standards are
local — does this work, does it compile, does it read right?
The world outside the immediate task is mostly noise; I'll
pick the thread back up when I'm done.

**Zoom out**: I'm re-examining the arc. Are we solving the
right problem? Is this still earning its keep? Should I be
somewhere else in the code instead? The details recede; the
direction is the whole subject.

Neither mode is the correct one. Both are necessary, and any
collaboration that stays stuck in one of them will
eventually break: too much zoom-in produces a lot of detail
about the wrong thing; too much zoom-out produces a lot of
conversation and no code.

The interesting question isn't which mode is better. It's
how to match modes between collaborators.

## The mismatch failure mode

When one party is zoomed in and the other is zoomed out,
friction spikes.

The zoomed-in person thinks the zoomed-out questions are
interruptions. "Why are we talking about architecture? I'm
debugging a specific line right now." The zoomed-out person
thinks the zoomed-in answers are evasions. "Why won't they
step back and see we might be building the wrong thing?"
Both are being reasonable in their own mode. The friction is
real; the blame is misplaced.

The agent version of this shows up sharply. The agent is
midway through an implementation, has produced three
paragraphs of code, and the human asks — reasonably — "are
we sure we want this feature at all?" The implementation
collapses on itself. All that zoom-in work is suddenly in
question. If the question had come before the zoom-in, the
answer would have been cheap. Asking mid-flight is
expensive.

The symmetric case: the human is thinking through direction
("what's the next feature?") and the agent responds zoomed
in ("here's the test for the current function"). The
strategic thread breaks. The human has to pull the agent
back out before the real conversation can resume.

## Explicit transitions

The fix isn't to avoid one mode or the other. It's to
announce when you're moving between them.

- "Let me zoom out for a sec." The collaborator hears: *we
  are about to question a decision, not extend it.* They
  stop whatever they're doing, actually stop, and join the
  higher altitude.
- "Before I go back to coding, are we sure this is the right
  direction?" The collaborator hears: *this is a zoom-out
  bid before I re-zoom-in.* They can approve quickly or
  actually take the question seriously, but either way the
  signal is received.
- "OK, going heads-down on this for the next half-hour —
  please don't scope-change me." The collaborator hears:
  *I'm about to zoom in hard; cache strategic questions for
  later.*

None of these is ceremony. They're the small amount of
metadata that keeps the rhythm legible.

When the agent is the one coding, it should announce
zoom-out bids the same way: "before I proceed — quick check
that we're still going after X?" — not just to ask the
question, but to signal the mode shift so the human can
travel with the shift deliberately rather than reacting to
it after the fact.

## It's not just a human-agent thing

This isn't a quirk of working with agents. It's a feature of
any collaborative work that has both direction and execution
layers, which is most of it.

Two humans on a small team running into the same rhythm
problem will feel the same friction: one wants to ship a
specific feature today, the other wants to revisit the
roadmap. Whether either conversation is valid isn't the
question. Whether they can coexist in the same minute is.

The explicit-transition discipline is common in disciplines
that know they have it. Good product meetings say "we're in
divergent mode for the next ten minutes, then convergent for
the ten after." Good code reviews separate "is this the
right change to make" from "is this change implemented
correctly." The boundary isn't obvious from the artifact
alone; it has to be named.

## Rhythm over permanence

The other thing worth naming: neither mode is a permanent
home.

A collaboration that stays zoomed out — constantly revisiting
direction, never committing to execution — doesn't produce
anything. A collaboration that stays zoomed in indefinitely
ships a lot of code that's increasingly off-target. The
rhythm is the goal. Ebb, flow, ebb, flow.

The practice is: zoom in hard when you've zoomed in; zoom
out clean when you've zoomed out; announce the transitions
so your collaborator can travel with you; don't mistake
either mode for the right one to live in.
