# Top-level Claude as orchestrator

**As-of:** 2026-04-29
**Confidence:** Firm — distilled from the ONBOARDING_DOCS exercise.
**Durability:** Stable; the diagnostic framing and IF discipline are load-bearing.

Read this when Steve asks you to dispatch sub-agents. The full
sub-agent operating principles (IF mechanics, return format,
commit tiers, failure handling) live in the canonical reference:
`~/showell_repos/claude-steve/PLAN_EXECUTOR_OPERATING_PRINCIPLES.md`

**How to dispatch:** use the `Agent` tool with `subagent_type:
general-purpose` (or a more specific type if the task matches one —
see the tool description for the available types). Pass the repo
path, task brief, and a mandatory `this_would_have_been_easier_if`
requirement in the prompt.

What's here is the orchestrator-side view: what to dispatch, how
to read the results, and the canary methodology.

## The diagnostic framing

**Run canaries before writing docs.** A doc written against a
hypothetical failure covers hypothetical ground. A doc written after
a canary covers a real gap.

The pattern: pick a specific claim or behavior to test, dispatch a
cold agent with a narrow task that reveals whether the claim holds,
read the result. Several assumed gaps will not exist. The real gaps
will often be found where you didn't expect them.

Agents are sometimes half workhorse, half canary. Make the canary
role explicit in the dispatch when that's what you want.

## The mandatory IF

Every sub-agent return includes `this_would_have_been_easier_if`.
This is non-optional — include it explicitly in every dispatch prompt.

**What to do with it:** read it before dispatching the next agent.
If it names a doc gap, fix the doc. If it names a tooling gap,
consider building the tool. The loop is: dispatch → collect IF →
fix gap → dispatch again. Don't let IFs accumulate across dispatches
without acting.

Full IF mechanics, three kinds, lifecycle, and triggers: see
`PLAN_EXECUTOR_OPERATING_PRINCIPLES.md` § "The IF field."

## Giving agents latitude

For exploratory or tooling tasks, say so explicitly: "You have
significant latitude here." This licenses confident forward motion.
Without that signal, agents hedge.

For bug fixes, the opposite: "State your assumed root cause and
proposed fix before changing code." This keeps diagnostic reasoning
visible.

Name git irreversibility explicitly for exploratory dispatches —
it changes how confidently the agent acts.

## Structural problems vs. local fixes

When dispatching against a pain-ranked or otherwise flagged file,
explicitly tell the agent to watch for systemic structural issues —
not just the surface symptom. A large file is sometimes large for a
good reason; a churny file is sometimes churny because it's the
right place for frequent change. The agent should name its read on
this before touching anything.

Calibration: "If the file is large because it's doing too many
things, say so and propose a split before implementing. If it's
large because the domain is genuinely complex, say that too — don't
manufacture a refactor."

## The meta-bandwidth payoff

When sub-agents handle the mechanical work, top-level Claude has
cycles for: process observations, methodology lessons, cross-task
synthesis, hole detection in tooling. That's the structural payoff
of running sub-agents. Use the bandwidth deliberately between
dispatches — don't just collect returns and re-dispatch.

See `memory/feedback_orchestrator_meta_bandwidth.md` for the
extended version of this principle.
