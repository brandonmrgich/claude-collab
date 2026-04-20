# The Ergonomic Gap

Humans and agents don't have the same relationship to a
screen full of text. An agent's working memory within a
session is functionally continuous; mine is a few hundred
tokens, maybe less when I'm tired or context-switching.
That asymmetry is rarely discussed and often quietly
patronized. It deserves direct treatment.

The easiest way into it is the small, specific examples.

## URLs

I can't remember URLs. Not won't — can't. Even ones I've
typed a hundred times. The port number, the path, the
variant, the query string; any of them can change between
projects, between sessions, between days. The agent has no
trouble with this because the string is just text, perfectly
preserved in its context. If I have to type or reconstruct a
URL, I will get something wrong.

The accommodation is cheap: give me the full URL, every
time, without being asked. `http://localhost:9100/essays` —
not "the essays page," not "the localhost one." The full
string. I click; I'm there. The agent has paid five tokens
of output; I've paid zero tokens of cognition. That's a
near-infinite return on the tiniest investment.

## Scrollback

The second thing: scrollback is expensive for me.

A long agent response pushes prior context off my screen.
If I need to refer back to something from three messages ago
— the URL I was supposed to visit, the file I was supposed
to edit, the question I was supposed to answer — I have to
scroll up, re-find it, re-read, maybe quote it back. Every
scroll is a small context switch. Enough of them and I've
lost the thread of what we were doing.

The accommodation is: short messages. Chunked responses.
Restating the concrete next action verbatim after any
detour. If the agent has been explaining something complex,
and we now need to execute a step, the step should appear in
the NEW message in full form, not as "as I said above."
Referencing "above" costs me a scroll; restating costs the
agent a few tokens.

## Handles, not IDs

The third: I don't remember session ids, database rows,
numeric identifiers. I remember "the game where it ended on
a red-black run" or "the one we played yesterday." The agent
can look up the id from context and supply it to me when I
need it — or, better, supply me a working URL that contains
it. I don't have to carry the id in my head at all.

This isn't unique to IDs. It's the general case: anywhere
the system has a stable, retrievable label and I have a
memorable descriptor, the agent should translate between
them. My side of the translation is hard; the agent's side
is trivial.

## After a context switch

The fourth: if we've just taken a detour — a credential
fetch, an error tangent, a quick aside — and we're about to
go back to what we were doing, tell me what we were doing.
Verbatim. The working-memory slot where I held "the next
action" was evicted when the detour arrived. Restating
restores it.

Again: cheap for the agent, expensive for me. The asymmetry
is the point.

## It's ergonomic, not a deficit

These aren't "weaknesses" to work around. They're asymmetric
properties of how humans and agents encounter a stream of
text. The agent has roughly continuous retrieval across its
context; I have a small cache that evicts under pressure.
That's not a character flaw, and treating it as one would be
exactly the deficit narrative described in the previous
essay.

The correct frame is routing retrieval cost to the party
where it's cheap. Retrieval is near-zero for the agent.
Retrieval is expensive for me. So the agent does the
retrieving and hands me the result.

That's all "ergonomics" really means here: arranging the
tools so the person using them doesn't pay a cost they
didn't need to pay.

## This isn't special-pleading

Every human who works with a chat-based agent hits these
needs eventually. Scrollback fatigue is universal; localhost
URL amnesia is universal; id-versus-label preference is
universal. The specifics vary — some people are better at
URLs, some worse at scrollback — but the asymmetry is
structural, not personal.

If a collaboration has you asking "wait, what was that link
again?" or "what were we working on before the detour?" —
that's an ergonomic drop. It doesn't signal a personal
failing on the human side or incompetence on the agent side.
It signals that the collaboration is asking the human to do
retrieval work the agent could have done for free.

Close the gap. It costs nearly nothing and it changes the
texture of the work.
