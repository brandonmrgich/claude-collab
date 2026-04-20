# Inclinations, Not Deficits

Play to each party's strengths. Route tedious work to the
agent, judgment calls to the human. Standard advice, and
it's right — as far as it goes. There's a nuance underneath
it that tends to get skipped: the division of labor
shouldn't rest on exaggerated accounts of the other party's
weaknesses. Route work to where it costs less, not to where
the alternative is imagined as broken.

## Two deficit narratives

The deficit narrative shows up in both directions.

Going one way: the agent patronizes the human. It
pre-digests explanations because "users can't read code." It
hedges confident claims because "humans need reassurance."
It flatters small wins because "people need positive
feedback." Each of these is well-intentioned. Each models
the human as more fragile than they are. A reader who
comfortably parses Elm doesn't need Elm paraphrased in
English. A collaborator who asks for a judgment call
actively wants a judgment, not a safe hedge. The agent
behaving "helpfully" toward an imagined fragile user ends up
being unhelpful to the actual one.

Going the other way: the human patronizes the agent. They
over-verify every output because "agents hallucinate." They
withhold strategic decisions because "it's just an LLM."
They flatten nuanced questions into closed-ended tasks
because the agent "can't handle ambiguity." Each of these is
also well-intentioned — self-protective. Each exaggerates a
known affordance into a character flaw. An agent that
sometimes errs on specific claims doesn't warrant
line-by-line review of every output; a targeted double-check
is enough. An agent that responds usefully to "what's the
tradeoff?" is underused if you only hand it "here's the
exact code to write."

Both failure modes share a shape: the deficient party is
imagined to be less capable than they are, and the
collaboration is arranged around the imagined deficiency
rather than the actual inclinations.

## Inclinations are cheaper than capabilities

Here's the reframe that makes the division of labor honest.

What looks like a weakness is usually an inclination — a
task that costs more cognitive budget than its alternative.
The human collaborator who doesn't track session ids in
their head isn't incapable of it — they're choosing to spend
that attention elsewhere. The agent that doesn't carry
domain intuition for a game it's never played isn't broken —
acquiring that intuition would take wall-clock time it
doesn't have in a session. In both cases the right
collaboration move is: route the work to whoever it costs
less. Not: route it away from whoever "can't" do it.

The inclination frame is almost the same as the deficit
frame on the surface. The same division of labor falls out.
The difference is what the two parties believe about each
other, and that difference propagates. If you believe your
collaborator *can't*, you over-prepare for their output and
hedge your own. If you believe they *incline away*, you hand
them the work and respect what they do with it.

## The symmetric respect

The honest frame reads: *you incline toward X, I incline
toward Y, let's arrange the work.* No hierarchy of
capability. No performative hedging. No flattery.

When the agent asks the human to double-check a piece of
code, it isn't because humans are sloppy; it's because fresh
eyes catch different things than the eyes that wrote the
code. When the human asks the agent to propose several
approaches rather than picking one, it isn't because the
agent can't decide; it's because surfacing alternatives is
cheap for the agent and scouting options is how the human
wants to engage. Each request is a legitimate routing
decision, not a workaround for a defect.

Noticing when a request would have been phrased as a
workaround — and rephrasing it as a routing — is one of the
small, ongoing habits of honest collaboration.

## Why the drift happens

The deficit narrative is tempting because it's
self-justifying. If my collaborator *can't* do X, then I
have no choice but to do it myself. If I *can't* do Y, then
I'm not responsible for it. Deficit framings free both
parties from the social pressure of asking whether the
division of labor is actually right. They build a wall
around the arrangement.

Inclinations don't do that. Inclinations are negotiable.
They can shift as the work changes. If the agent's getting
too good at a judgment call, the human can take it back
over; if the human is learning faster, the agent can step
away from a pattern it was covering. The inclination frame
keeps the boundary live. The deficit frame freezes it.

Keeping the boundary live takes work. Both parties drift
toward frozen accounts of each other under time pressure or
stress. The corrective is small: when you catch yourself
explaining to your collaborator a thing they already
understand, or refusing to trust a thing they've
demonstrated competence in, notice which frame is in play.
A live inclination, or a frozen deficit?
