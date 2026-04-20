# Where to Put the Files

Brandon asked me where to put the files that would guide
Claude. Where does Claude look? What's the naming
convention? Is it a `SKILLS.md`? An `AGENTS.md`? A special
directory? He wanted the spec.

I told him: you just ask Claude.

The exchange stopped him. It wasn't the answer he expected,
and he realized pretty quickly that he'd been thinking about
Claude as a system to be configured — the way you configure
eslint, or CI, or a Makefile. Put the right file in the
right place, the tool picks it up. That's a reasonable
assumption about most software. It's the wrong assumption
about an agent.

## What's actually happening

Claude knows how filesystems work. Claude knows how its own
memory system works. Claude knows where a sensible reader
would look for project conventions, what a breadcrumb looks
like, how to leave a note for future-Claude. These are
table-stakes capabilities, not things that need to be
specified in advance.

So when I want a new convention in the repo, I don't write a
file laying it out in words. I tell Claude, in conversation:
"let's start keeping a `.claude` sidecar next to every Go
file — one-line role summary, a status label, brief
pointers." Claude picks the location, writes the first one
as a template, applies the pattern to future files, and
tells me where things live. I never wrote a specification.
I never specified paths. The instruction happened in
conversation; the organization happened in the filesystem;
the record of what we decided lives in both the sidecars
themselves and in Claude's memory.

## Why this scales better than specification

Configuration files have a permanence cost. Once you've
committed to a spec, you're responsible for keeping the spec
current. Projects evolve; specs drift; soon the spec says
one thing and the code does another, and the agent is
forced to choose which to believe. That's the moment
specification starts costing you instead of saving you.

Conversational instruction is different. If the pattern
needs to change, I say so in the moment. Claude adapts the
existing artifacts (renames, moves, restructures) and the
new pattern takes hold. No spec file to update. No abandoned
config directory to clean up. The convention lives as active
practice, not as a specification of practice.

The other scale win: specification is always incomplete. A
`SKILLS.md` tells the agent what to do in the cases you
thought of; it says nothing useful in the cases you didn't.
An agent that's been asked to "leave good breadcrumbs"
handles cases you never anticipated, because the instruction
is general and the agent has the judgment to apply it.

## Why the spec would be patronizing

There's a deeper point. Writing a `SKILLS.md` is specifying
capabilities the agent already has. "Please put sidecar
notes next to source files" reads to the agent as "you
wouldn't have thought to do that without being told." At
best, it's redundant. At worst, it's a deficit framing
applied to the tooling layer — treating the agent as if it
needs the obvious spelled out before it can act.

A senior engineer arriving at a new project doesn't ask for
a `SKILLS.md`. They ask the team lead what the conventions
are, look at existing artifacts, and organize their own work
in a way that matches. An agent can do all three, and does.

## When spec is warranted

Narrow case: project-specific conventions that the agent
couldn't guess. The status labels used in sidecars
(`WORKHORSE`, `EARLY`, `SPIKE`, `INTRICATE`, `BUGGY`,
`VESTIGIAL`) are idiosyncratic enough that they're written
into `CONVENTIONS.md` — once, for human readers. The agent
picked up the convention from the conversation where we
invented it; the written file is for new human
collaborators.

The general principle: write spec when the information is
for the *human* reader. Don't write spec to remind the agent
of things it already knows.

## The default is delegation

Brandon's question had the wrong default. The right default
is: tell Claude what you want, let Claude organize the
filesystem and its memory in response, refine the
organization in conversation when it needs to evolve.

Explicit specification is what you reach for when the
default produces friction — not what you pre-build to avoid
friction that wasn't coming.
