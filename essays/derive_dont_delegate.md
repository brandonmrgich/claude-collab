# Derive, Don't Delegate

You're building a drag-and-drop UI. The user grabs an item
from a list, drags it toward a target, and drops it. Your
job: detect when the drop would be valid so you can (a) show
visual feedback during the drag, and (b) fire the right
handler on release.

The default way to do this in a browser: attach `mouseenter`
and `mouseleave` handlers to the target. When the user's
cursor enters the target's DOM rect, you flip a "currently
hovering" flag; when they release, you check the flag and
dispatch.

It works. It's even idiomatic. And it has a subtle failure
mode that took me a long time to name: you're asking the
browser a question you already knew the answer to.

## What you knew

Your component rendered the dragged element. You know its
position, down to the pixel. You rendered the target. You
know *its* position too. The cursor coordinates are in
every mouse-event payload. "Is the dragged element over the
target?" is a trivial rectangle-intersection problem, maybe
five lines of code.

But instead of computing it, you delegated. You handed the
question to the browser and asked it to tell you back. When
it works, you don't notice. When it doesn't — `mouseenter`
that fires intermittently because of a z-index quirk, or a
`pointer-events: none` inherited in an unexpected way, or
an event eaten by an overlay you forgot was there — you
find yourself debugging the delegation instead of the
logic. The logic was never the problem. The *ask* was.

## The pattern is everywhere

Once you see this shape, you find it in places that have
nothing to do with the DOM.

You POST `{a, b, c}` to an endpoint and await a response
that includes `a + b + c`. The server's only job was
arithmetic on data you already sent.

You write a row to the database and immediately query it
back to confirm it. If the write didn't throw, you have the
row's content already; the query is a round-trip for
information you never lost.

You call a validation library on a form object you just
built, and it tells you which fields are invalid. You wrote
the rules. You constructed the data. The library is a
round-trip through a machine whose only knowledge came from
you.

In each case the delegation feels natural because some
other system is *capable* of answering. The mistake is
treating capability as a reason. Capability is necessary
for delegation to work; it isn't sufficient to make
delegation the right choice.

## The honest cost

When you delegate an answer you already own, you buy three
things you probably didn't want:

**A new failure mode.** The delegation can fail in ways
your own code couldn't. The DOM skips an event. The network
drops a packet. The library ships a bug. Every delegation
is a new failure surface, and usually an opaque one — the
delegated machine isn't yours to debug.

**A new timing concern.** The delegation happens at its own
cadence, not yours. Events arrive out of order. Responses
race. You find yourself writing defensive code for "what if
the server's answer is stale" — a case that only exists
because you round-tripped to get an answer you could have
computed synchronously.

**A harder test story.** Pure computation is trivially
testable. Delegated computation requires either a real
instance of the delegated system (slow, flaky in CI) or a
mock of it (a new abstraction you have to maintain). Either
way, the test is now a test of the delegation plumbing, not
of the logic you cared about.

The self-reliant alternative carries none of these costs.
A pure function `intersects(a, b) : Bool` is one value in,
one value out. No timing. No network. No mocks. Testing it
is five lines and a lookup table.

## When delegation IS the right answer

No absolute rule. Delegate when the other system genuinely
knows something you don't:

- The database knows whether *another* process wrote a
  conflicting row.
- The server knows the current balance *after* transactions
  you didn't see.
- The OS knows which file descriptor is ready to read
  right now.

The discriminator is clean: is the information genuinely
held somewhere else? Then delegate — you have no choice,
and the cost is worth it. Is the information derivable from
state you already hold in your own address space? Then
compute.

Most of the regrettable delegations I see (and make) fall
into the second bucket. The information was derivable. The
reason it got outsourced was that the other system was
there, ready to answer, so handing over the question felt
like the path of least resistance. The path of least
resistance is the trap.

## A reflex worth catching

When you're about to ask another system for an answer,
pause for one question: *could I compute this from state I
already have?*

If the answer is yes, pay attention to that. The code is
almost always shorter when you compute it. The failure
modes are fewer. The tests are simpler. The boundary
between your component and the system you were about to
ask is narrowed to the cases where the ask actually earns
its keep — which is what you want boundaries to do.

The round-trip is the natural move. The computed answer is
almost always the better one.
