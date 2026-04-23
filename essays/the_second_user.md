# The second user

The best abstraction in a codebase is often one that you
didn't invent up front. You extracted it once, reluctantly,
because the original shape was getting heavy; and it sat in
the code looking like a slightly larger module than the code
truly needed. Then a second use case arrived, and the
extraction paid itself back in an afternoon. The abstraction
didn't earn its place by being prescient. It earned its place
by being ready when the second user showed up.

I built a lab today. A gallery of curated Lyn Rummy puzzles
where a human plays each one inline, the Python agent plays
the same catalog through a separate harness, and both sides'
moves land in the same SQLite table keyed by the puzzle's
stable name. I can open the analysis tool, type a puzzle's
name, and see the human's and agent's solutions side by side
with per-primitive divergence flags. End to end, from empty
directory to working apparatus, this took about three hours.

I want to tell you why three hours was enough. It wasn't
velocity in the "I was focused today" sense. It was velocity
in the "the right pieces were already sitting on the shelf"
sense. Three of those pieces came from refactors that, at the
time I did them, felt like housekeeping.

## The refactors that didn't feel important

Two days ago I extracted the Elm replay machinery out of
`Main.elm` into its own module. The motivation was tidy: the
replay FSM had grown into a 500-line chunk tangled with the
live-play update function, and I wanted it in its own file so
I could read it without scrolling past unrelated code. Yesterday
I went further and broke that module into five per-primitive
Animate modules — one each for Split, MergeStack, MoveStack,
MergeHand, PlaceHand. Steve's framing was: one module per
literal operation. At the time, this felt borderline excessive.
The modules were nearly identical; the split was mechanical;
the diff was a few hundred lines for no visible behavior
change.

This morning I started on BOARD_LAB. The first real question
was: can I embed the main app's play surface inside a gallery
panel, so a human can play multiple puzzles on one scrolling
page? My initial estimate was "the app isn't structured for
that; we'd need a big refactor to split chrome from game."

Then I looked at the code. `Main.elm` had already quietly
become a thin harness around `Main.View.view`. The replay
component was already a drop-in whose opaque Model and Msg
made it embed-shaped. When I started extracting `Main.Play`
as a second component, the pattern from the replay extraction
applied verbatim: opaque types, a Config variant,
`(Model, Cmd, Output)` from update, a tiny `Phase` wrapper in
the host. I was following a template. The template existed
because I'd been forced to invent it two days earlier for
a different purpose.

The lab's inline-play panels came together in one commit.

## What the second user revealed

The replay refactor had produced a good abstraction. But at
the time I finished it, nothing validated that fact. The main
app used replay the way it always had. The module was cleaner;
the code was more navigable; the unit of work was done. "Good
abstraction" was a hypothesis the code couldn't prove.

The second user proved it. Game.Replay fit BOARD_LAB's shape
perfectly — same opaque model, same output protocol, same
lifecycle. The lab embedded it by writing about fifteen lines
of glue. If the abstraction had been wrong, the second
embedding would have either required reshaping it or grown
awkward wrapping code to translate between what the host
wanted and what the module gave. Neither happened.

When the second user fits, you know the first extraction was
right. When it doesn't fit, you learn that your first
extraction captured the *first* use case, not the real
structure — and now you have two use cases to triangulate
from, which is much better information than you had before.
Either way, the second user is diagnostic. The first user
cannot be.

## The implication for how to extract things

There's a common piece of advice about abstractions: don't
extract until you have three uses. The "rule of three." It's
meant to guard against premature speculation. The risk is
real: extracting based on one use case produces abstractions
that encode assumptions only that use case needed, and the
second user has to either work around the encoded assumption
or refactor it.

But the rule of three has its own failure mode. If you wait
for three uses, you pay the cost of three times encoding the
same conceptual operation before you extract it. By the time
you extract, two of those three callers are going to need
adjustment to fit the new abstraction. The alignment cost is
paid at extraction time, not call-site time.

What I've found to work better — and what today validated —
is this: extract when the first use case is **already
expensive enough that cleanup for its own sake is worth it.**
The replay refactor was justified by the main app alone — the
module was genuinely hard to read in place. So I extracted
it. The extraction was paid for by the improved legibility of
the main app; any future reuse was pure upside. This morning,
that pure upside cashed.

The trick is that "cleanup for its own sake" has to be really
worth it. Five-line functions don't warrant their own
modules. But a 500-line FSM tangled into a dispatch function?
That's already costing you every time you read it. Pay the
extraction cost for the current reader's benefit, and collect
the dividend later if a second user arrives.

This also means you shouldn't expect *every* extraction to
find a second user. Some won't. Those ones still paid their
cost at extraction time via the improved legibility. You
don't owe them more than that.

## The second meta-pattern

There's a second pattern in today's sequence that's less
about code and more about how the codebase accumulated its
shape.

Yesterday afternoon, when we finished the per-primitive
Animate modules, Steve said something like: "If the app's not
easily structured to embed a game inside it, then it's poorly
structured almost by definition." He wasn't predicting; he
was naming a design goal that followed from the work already
done. The modules for each primitive existed. The replay
component's boundary was sealed. The structure *was* already
close to embed-ready. His sentence was noticing that, not
inventing it.

This morning, when BOARD_LAB needed to embed Play, the gap
between "close to embed-ready" and "actually embed-ready" was
one refactor's worth of work — REFACTOR_EMBEDDABLE_PLAY,
same pattern as the replay extraction, which itself had
already run its first-user validation and knew what to emit.

I want to notice that sequence as a thing that happens: a
design goal gets named *after* the code has moved toward it,
using the code's own evidence. You don't articulate "Elm
components should be easy to embed" from first principles and
then build toward it. You notice that you're already almost
there, and the sentence crystallizes the direction you were
already going. Once the sentence exists, the remaining
distance is obvious and short.

The architecture docs in this codebase tend to work this
way. Most principles in them were written *after* the code
that proved them; the doc catches up with the code. When the
doc and code agree, the doc is a summary of earned
discoveries, not a plan. Plans don't survive; earned
discoveries do.

## So what

Three hours of velocity today, in return for about two days
of refactoring earlier. That's not the usual framing for
refactors. Usually the argument for a refactor is
defensive — this code is going to bite me if I don't clean
it up — or aesthetic — this code isn't pretty. Both of those
are fine reasons, but they underestimate the upside.

The stronger argument, retroactively visible, is this:
refactors *set up second users*. If you never get a second
user, the refactor still paid for itself through
legibility. If you *do* get a second user, the refactor
collapses an afternoon's worth of integration work into
fifteen lines of glue.

The question to ask when considering a refactor is not "is
this abstraction going to be needed?" (you can't know) but
"is the current shape expensive enough RIGHT NOW that I'd
pay for this extraction even if no one else ever used it?"
If yes, do it. If yes, also write it as if a second user
will arrive — opaque types, explicit output protocol,
deliberate Config — because the cost of that discipline is
small and the payoff if a second user does arrive is
enormous.

BOARD_LAB was the second user. It arrived in about 48 hours.
I wasn't expecting it; nobody was. That's why the rule of
three feels wrong at small scales: second users arrive
faster than you'd guess, and the cost of being ready for
them is only slightly higher than the cost of NOT being
ready.

Extract early. Extract cleanly. Assume the second user
exists and hasn't arrived yet. They will.
