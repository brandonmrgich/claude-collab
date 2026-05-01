---
title: Custom skill system audit vs. superpowers
status: open
created: 2026-04-28
last-active: 2026-04-28
tags: [skills, audit, methodology, claude-config, roadmap]
anchors:
  produced: []
  references:
    - cross-claude-mantras-and-skills-integration.md
    - essay-system.md
---

# Custom skill system audit vs. superpowers

## Purpose

A future agent consumes this document. It compares the user's current
homebrew skill system (`~/.claude/skills/`, 20 skills) against the
community baseline `obra/superpowers` plugin and surfaces the gaps that
are worth closing, the strengths that should not be regressed, and a
prioritized backlog that an agent can pick up without re-doing this
research.

Source material:
- Local skills enumerated under `claude/.claude/skills/` (20 SKILL.md files read in full)
- `claude/.claude/CLAUDE.md` for taxonomy and anchor chain
- Superpowers repo: `obra/superpowers`, `obra/superpowers-skills`, `obra/superpowers-marketplace`
- Skills inspected: `using-superpowers`, `writing-skills`, `writing-plans`,
  `test-driven-development`, `systematic-debugging`,
  `verification-before-completion`, `brainstorming`,
  `subagent-driven-development`, `dispatching-parallel-agents`,
  `receiving-code-review`

---

## Inventory of current skills

20 skills in three buckets:

### Discipline / workflow (8)
| Skill | Bytes | Role |
|---|---|---|
| `plan-executor` | 19k | Orchestrate sequential multi-task plan execution via dispatched sub-agents |
| `plan-auditor` | 11k | Independent compliance auditor for completed plan tasks |
| `session-ready` | 6k | Fresh-Claude continuity probe — can a cold session pick up the work? |
| `top-down-sweep` | 4k | Breadth-first doc audit walking from a canonical root |
| `doc-freshness` | 5k | Staleness detection via `covers:` + `last-verified:` front-matter |
| `worktree-orchestrator` | 6k | Git worktree management with registry; never auto-merges |
| `zoom-in` | 3k | Narrow attention to a task; interactive or autonomous sub-agent |
| `zoom-out` | 2k | Surface from a focused task; optional plan-promotion handoff |

### Capture / knowledge (4)
| Skill | Bytes | Role |
|---|---|---|
| `essay` | 8k | Capture/maintain design-discussion essays with anchor chain |
| `idea-tracker` | 5k | Pre-plan idea stash; replaces legacy TODO system |
| `environment-map` | 3k | Multi-host/network/repo reference for cross-machine work |
| `skill-author` | 10k | Meta-skill for creating new skills/agents |

### Domain specialists (8)
| Skill | Bytes | Role |
|---|---|---|
| `astro-static-sites` | 7k | Astro framework specialist (islands, content collections) |
| `ddex-standards` | 9k | DDEX music-industry messaging reference |
| `github` | 7k | Git/GitHub policy: commits, PRs, push policy, headless-auth pre-flight |
| `gitignore` | 5k | `.gitignore` policy and `.claude/` ignore catalog |
| `nextjs-app-router` | 10k | Next.js 13+ App Router specialist |
| `royalty-splits-music` | 9k | Royalty split modeling, MASTER/PUBLISHING buckets, payouts |
| `turborepo-patterns` | 9k | Turborepo monorepo build orchestration |
| `web-audio-howler` | 10k | Web audio playback, Howler.js, MediaSession integration |

Plus four plan-executor sub-agents (`~/.claude/agents/`), two mantras
(`~/.claude/mantras/`), and two reference docs
(`~/.claude/references/console-discipline.md`,
`~/.claude/references/plan-system.md`).

---

## What the current system does *better* than superpowers

Do not regress these on the way to closing gaps.

1. **Six-class artifact taxonomy** (memory / mantra / idea / essay / plan
   / doc) with a single linear anchor chain
   `idea → essay → plan → doc → code` plus mantras informing it.
   Superpowers collapses to brainstorm → plan → execute. The local
   taxonomy is significantly more expressive and is the load-bearing
   skeleton the rest of the system hangs on.

2. **Anchored-doc staleness system** (`covers:` + `last-verified:` +
   `doc-freshness` skill + `top-down-sweep`). Superpowers has no
   equivalent. This is a genuinely novel pattern and the local
   implementation is well thought through (static/speculative opt-outs,
   git-leveraged staleness, plan-aware bumping recommendations).

3. **Sidecar conventions** (`<file>.<ext>.claude` files with `# label:` /
   `# role:`). Superpowers has nothing comparable. The label/role
   taxonomy (CANONICAL, ELEGANT, INTRICATE, SPIKE, BUGGY, …) gives a
   stability signal on every non-trivial file.

4. **Mantras as a separate class** — short, embodied, never-retrieved
   doctrines (`make_state_honest`, `eliminate_dont_paper_over`).
   Superpowers leans on procedure; the local system pairs procedure
   with principle. Worth keeping.

5. **Domain depth** — the eight specialist skills (DDEX, royalty
   splits, Howler, Turborepo, Astro, Next.js App Router) are
   substantially more specialized than anything in superpowers. The
   pitfall lists, decision matrices, and "what you must never do"
   sections are the right shape.

6. **Plan-executor elaboration** — multi-plan awareness, state files
   under `.claude/plan-states/`, commit-footer conventions
   (`Plan:` / `Task:`), audit-on-completion, Phase-5 cleanup with
   user consent, and `affects-docs` verification at the end. This is
   meaningfully richer than superpowers' `executing-plans`.

7. **Worktree-orchestrator with a registry** — superpowers has
   `using-git-worktrees` (a usage skill), the local version is an
   actual orchestrator with a JSON registry, conflict detection, and
   never-auto-merge discipline.

8. **Two-tier scope tagging** (`[HomebrewSkill]` vs `[ProjectSkill]`)
   makes user-authored skills distinguishable from built-ins in the
   skill picker. Superpowers does not formalize this.

9. **`session-ready` continuity probe** — superpowers has no
   equivalent. Dispatching a cold sub-agent to verify the docs carry
   enough context for a fresh session is a strong pattern.

10. **`environment-map`** — multi-host/Tailscale/SSH-config awareness.
    Superpowers is single-host by assumption.

---

## Where the current system falls short of superpowers

Ranked by impact. Each gap is described as: what's missing, why it
matters, and what action would close it.

### Gap 1 — No discipline-pressure skills (highest impact)

Superpowers' core innovation isn't its skills' content — it's the
*pressure language* they use to force activation and compliance:
"Iron Law", "NO X WITHOUT Y FIRST", "If you think there is even a 1%
chance a skill might apply, you ABSOLUTELY MUST invoke it",
rationalization tables, red-flag lists, scripted refusals. This is the
mechanism that makes the framework load-bearing.

The local skills are uniformly *policy / reference* tone —
"trigger on phrase X, do procedure Y". They do not fight the
default agent's incentive to skip skills under pressure.

Specifically missing:

| Superpowers skill | What it enforces | Local equivalent |
|---|---|---|
| `systematic-debugging` | 4-phase root-cause methodology; "NO FIXES WITHOUT ROOT CAUSE INVESTIGATION FIRST"; halt and question architecture after 3 failed attempts | None. `make_state_honest` mantra is adjacent but not procedural |
| `test-driven-development` | RED → verify-RED → GREEN → verify-GREEN → REFACTOR; "NO PRODUCTION CODE WITHOUT A FAILING TEST FIRST"; pre-test code must be deleted | None. Plan-executor `tester` agent writes tests but no skill enforces TDD discipline on regular work |
| `verification-before-completion` | Fresh evidence required for any "done" claim; agent reports must be independently checked against VCS diff; no hedging language | Partially covered by `plan-auditor` (plan-scoped only). No general "don't claim done" skill |
| `brainstorming` | Mandatory design-before-code, even for "simple" tasks; divergence/convergence; spec doc before plan | `essay` + `idea-tracker` cover capture but nothing *enforces* design-first on every task |

These four are the highest-leverage additions. Each one prevents a
specific class of agent failure (plausible-fix-without-investigation,
test-after-the-fact, fake-completion, jump-straight-to-code).

**Action:** add four new skills modeled on superpowers' pressure
language. Adapt the procedures to fit the local taxonomy
(verification anchors back to `last-verified:` bumping; brainstorming
graduates into the existing `essay` skill rather than a separate
spec doc).

### Gap 2 — No `using-superpowers`-style meta-rule

Superpowers' first skill is a meta-rule: "before responding to
anything, scan your loaded skills, and if any plausibly apply,
invoke them — even before asking clarifying questions." It includes
a rationalization table for the twelve common excuses agents use to
skip the check.

The local `skill-author` skill is about *creating* skills. There is
no skill that pushes the agent to *use* the skills it already has
aggressively.

**Action:** add a `using-homebrew-skills` skill (or fold this into
`CLAUDE.md` as a top-level rule). Borrow the rationalization table
verbatim — the rationalizations are universal across agents, not
specific to superpowers.

### Gap 3 — Code-review discipline is absent

Superpowers ships `requesting-code-review` and `receiving-code-review`.
The receiving skill is particularly load-bearing: a 6-step protocol
(READ → UNDERSTAND → VERIFY → EVALUATE → RESPOND → IMPLEMENT) with an
explicit ban on performative agreement ("You're absolutely right!"
forbidden).

Local skills cover commit/PR mechanics (`github`) but not the
*discipline* of giving or receiving review.

**Action:** add `receiving-code-review` first (higher impact — it
fights the sycophancy default). Add `requesting-code-review` after.
Cross-reference the existing `github` skill so review discipline
chains into PR mechanics.

### Gap 4 — No "finishing a branch" ritual

Superpowers has `finishing-a-development-branch` — a checklist
ritual for closing out feature work (full test run, clean commits,
verified diff, all TODOs addressed or filed, etc.).

Locally this is implicit in `plan-executor` Phase 4/5 (audit +
cleanup) but only for plan-driven work. Ad-hoc feature branches
have no equivalent ritual.

**Action:** add a `finishing-a-branch` skill. It can defer to
`plan-executor`'s Phase 4 when a plan is active, but stand alone
otherwise. Cross-reference `github` for the push/PR mechanics and
`worktree-orchestrator` for worktree cleanup.

### Gap 5 — Plan format is under-specified for sub-agent execution

Superpowers' `writing-plans` enforces an extreme rigor that the
local plan-executor task format does not:

- Tasks are 2–5 minutes of work each (not whole-feature units)
- Every task contains *complete* code in backticks (not
  "add appropriate error handling")
- Zero-context engineer assumption (the plan must be executable by
  someone who has never seen the codebase)
- No placeholder language: TBD, TODO, "similar to previous task"
  are anti-patterns
- Exact commit messages provided per task

The local plan-executor delegates task content quality to whatever
generated the tasks. When tasks are vague, the dispatched
sub-agents fill gaps with guesses — exactly the mode superpowers'
plan format is designed to prevent.

**Action:** upgrade `~/.claude/agents/plan-executor-implementer.md`
(and the other sub-agent definitions) to *reject* under-specified
tasks back to the orchestrator rather than improvise. Add a
"task-quality" gate to plan-executor Phase 1 (validation): every
task must contain complete code or an explicit "explore-and-decide"
flag. Steal the rationalization table from superpowers'
`writing-plans` and embed it in `plan-executor`.

### Gap 6 — No skill-testing methodology

Superpowers' `writing-skills` defines a TDD-for-skills cycle:
1. RED: run pressure scenarios with a sub-agent *without* the skill,
   document baseline rationalizations verbatim
2. GREEN: write the minimum skill that fixes the observed failures
3. REFACTOR: re-run pressure scenarios, identify new rationalizations,
   add explicit counters

The local `skill-author` skill has decision matrices and an authoring
procedure but no verification step. There is no concept of testing
whether a skill actually changes behavior under load.

**Action:** add a "pressure test" section to `skill-author`. Define a
small fixture format for scenarios. Optionally: a
`skill-pressure-test` agent that takes a skill file + a scenario and
runs the sub-agent twice (with/without).

### Gap 7 — Description format diverges from CSO best practices

Superpowers' `writing-skills` is explicit: descriptions are the only
signal Claude uses to decide whether to load a skill, and badly-shaped
descriptions cause skills to be silently skipped.

Rules superpowers enforces:
- Max 1024 characters
- Third person, starts with "Use when…"
- Trigger conditions ONLY — never workflow summaries
- Workflow summaries cause Claude to "shortcut" the skill (read the
  description, skip the body)

Local skills systematically violate these. Quick audit:

| Skill | Issue |
|---|---|
| `plan-executor` | Description starts with workflow summary ("Orchestrate sequential…"), not triggers |
| `plan-auditor` | Starts with "Activates when…" — better, but mixes summary into the body |
| `session-ready` | Starts with workflow summary ("Probe whether…") |
| `essay` | Long description (~1100+ chars) mixing triggers with concept explanation |
| `skill-author` | Description embeds proactive-mode policy — should live in body |
| Several specialists | Use "Trigger when the prompt or files in scope reference any of:" — good for keyword density, but lengthy |

The local descriptions are not broken — keyword density is high — but
they pre-summarize behavior in a way superpowers warns against.

**Action:** audit all 20 descriptions. Pull workflow narration out into
the body. Move the policy-mode descriptions ("activates proactively
when X") into a `## Triggers` body section. Aim for <1024 chars and
"Use when…" prefix where possible.

### Gap 8 — Token budget is not a stated constraint

Superpowers targets:
- Frequently-loaded skills: <200 words
- Most skills: <500 words
- Heavy reference: in supporting files, not SKILL.md

Several local skills are large enough that loading them costs real
context budget:

| Skill | Approx words | Target |
|---|---|---|
| `plan-executor` | ~3000 | Move task-format spec, sub-agent return format, generation procedure to a reference file; SKILL.md keeps the operating principles + dispatch loop only |
| `plan-auditor` | ~1700 | Move audit report template to reference file |
| `skill-author` | ~1600 | Trim or split (skill vs agent authoring could separate) |
| `nextjs-app-router` | ~1500 | Acceptable for a domain specialist; consider splitting "patterns" (caching, hydration) into a reference |
| `web-audio-howler` | ~1500 | Same |

**Action:** introduce a `references/` pattern that's already partially
used (`plan-system.md`, `console-discipline.md`). Move heavy templates
and code blocks out of SKILL.md into sibling reference files. The
SKILL.md keeps frontmatter + principles + decision tables; references
hold long examples and templates.

### Gap 9 — No slash commands for the most-invoked workflows

Superpowers ships `/brainstorm`, `/write-plan`, `/execute-plan` as
direct entry points. The local system has rich plan-executor and
zoom-in skills but no slash command to launch them ergonomically.

The `github` skill mentions an existing `commit-commands` plugin
(`/commit`, `/commit-push-pr`, `/clean_gone`) — so the pattern is
known, just not extended.

**Action:** consider a small commands plugin alongside the skills:
`/zoom-in`, `/zoom-out`, `/session-ready`, `/sweep`, `/audit-task`.
Most local skills already declare `triggers:` arrays that look like
slash commands but aren't actually wired as commands.

### Gap 10 — Anchor-chain enforcement is weaker than the design

The CLAUDE.md anchor chain (`idea → essay → plan → doc → code`) is
documented but not *enforced* by any skill. There is no skill that
checks: "you're starting a plan — is there an essay it's
`from-essay:`'d to?" or "you're producing a doc — does it have
`from-plan:` or `covers:` set?".

Superpowers' equivalent (brainstorm → plan → execute) is enforced
because `writing-plans` refuses to run without an upstream design
doc, and `executing-plans` refuses to run without a written plan.

**Action:** add a small validation pass to `plan-executor` Phase 0
(initialize): if `from-essay:` is missing in the master plan
front-matter, surface a soft warning ("no essay anchored —
intentional?"). Same for `affects-docs:`. Don't block, just nudge.

---

## Prioritized backlog for a future agent

Each item is sized for one focused work session. Order is the order
in which I'd execute them — earlier items unblock or reduce the
scope of later ones.

### P0 — discipline-pressure skills (Gap 1)

1. **Add `systematic-debugging` skill.** Adapt superpowers' 4-phase
   methodology. Cross-reference `make_state_honest` mantra. <500
   words. Target `~/.claude/skills/systematic-debugging/SKILL.md`.

2. **Add `verification-before-completion` skill.** Adapt the
   "fresh evidence" protocol. Cross-reference `plan-auditor` for
   plan-driven verification and `doc-freshness` for doc verification.

3. **Add `test-driven-development` skill.** Adapt the iron-law
   pressure language. Cross-reference the existing
   `plan-executor-tester` agent.

4. **Add `design-before-code` skill** (or equivalent —
   `brainstorming` may not be the right local name). Cross-reference
   `essay` for capture and `idea-tracker` for pre-plan stash.
   Activate on phrases like "let's just build it", "I'll start
   coding", "skip the planning".

### P1 — fill missing rituals (Gaps 2–4)

5. **Add `using-homebrew-skills` meta-skill** — pushes Claude to
   actively scan available skills before responding. Steal the
   rationalization table from superpowers. Target word count: <200.

6. **Add `receiving-code-review` skill** — 6-step protocol, ban on
   performative agreement. Cross-reference `github` for PR mechanics.

7. **Add `requesting-code-review` skill** — checklist for what to
   include when asking for review.

8. **Add `finishing-a-branch` skill** — closeout ritual. Defers to
   `plan-executor` Phase 4 when a plan is active.

### P2 — upgrade existing skills (Gaps 5, 6, 7, 8)

9. **Audit and rewrite all 20 descriptions** (Gap 7). One pass.
   Apply: third person, "Use when…" prefix, triggers-only, <1024
   chars. Include the audit table in the commit message.

10. **Move heavy content out of SKILL.md into `references/`**
    (Gap 8). Specifically: `plan-executor` task format,
    `plan-auditor` report template, `nextjs-app-router` patterns
    section, `web-audio-howler` patterns section.

11. **Tighten plan-executor task quality gate** (Gap 5). Update
    `plan-executor-implementer` agent definition to reject
    under-specified tasks back to the orchestrator. Add a
    task-quality validation step in Phase 1.

12. **Add pressure-test methodology to `skill-author`** (Gap 6).
    Define a small scenario-fixture format. Optional: a sub-agent
    type that runs the test.

### P3 — anchor enforcement and ergonomics (Gaps 9, 10)

13. **Wire up slash commands** for the top-used skills:
    `/zoom-in`, `/zoom-out`, `/session-ready`, `/sweep`,
    `/audit-task`. Likely lives in a new `commands` plugin
    alongside the existing `commit-commands`.

14. **Add anchor-chain nudges** to `plan-executor` Phase 0 and
    `essay` Resolve mode — soft warnings when the chain is broken.

---

## Non-goals for this work

These would be regressions if pursued:

- **Replacing the local taxonomy with superpowers'.** The
  six-class artifact taxonomy and anchor chain are strictly more
  expressive; do not collapse them to brainstorm/plan/execute.
- **Importing superpowers wholesale via `/plugin install`.** Skill
  collision (e.g., the existing `worktree-orchestrator` vs
  superpowers' `using-git-worktrees`) and description-style
  mismatches make this messy. Cherry-pick the patterns instead.
- **Removing the sidecar conventions, mantras, or anchored-doc
  system.** These are local strengths superpowers has no answer to.
- **Auto-bumping `last-verified:` or auto-merging worktrees** to
  match superpowers' lighter touch. The local "always require
  human consent" stance is the right default.

---

## Appendix A — description-format quick audit

Snapshot for the future agent's P2.9 task. Char counts approximate,
based on the visible YAML in each SKILL.md.

| Skill | Starts with | Length | Triggers-only? | Verdict |
|---|---|---|---|---|
| `plan-executor` | "Orchestrate sequential execution…" | ~720 | No (workflow summary) | Rewrite |
| `plan-auditor` | "Activates when the user asks to audit…" | ~590 | Mostly | Tighten |
| `session-ready` | "Probe whether a fresh Claude…" | ~500 | No | Rewrite |
| `top-down-sweep` | "Breadth-first documentation audit…" | ~370 | No | Rewrite |
| `doc-freshness` | "Detects stale documentation…" | ~530 | No | Rewrite |
| `worktree-orchestrator` | "Manages git worktrees…" | ~670 | Mixed | Tighten |
| `zoom-in` | "Narrow focus to a specific task…" | ~190 | No (workflow) | Rewrite |
| `zoom-out` | "Surface from a zoomed-in task…" | ~110 | No | Rewrite |
| `essay` | "Captures and maintains essay-format records…" | ~1100 | No | Trim + rewrite |
| `idea-tracker` | "Capture and manage ideas…" | ~520 | Mixed | Tighten |
| `environment-map` | "User's broader environment map…" | ~830 | Yes (mostly keyword list) | Acceptable |
| `skill-author` | "Meta-skill for creating new Claude Code skills…" | ~890 | Mixed (embeds policy) | Rewrite |
| `astro-static-sites` | "Astro framework specialist…" | ~1700 | Yes (heavy keyword list) | Trim |
| `ddex-standards` | "DDEX (Digital Data Exchange) standards reference…" | ~1900 | Yes (heavy keyword list) | Trim |
| `github` | "Activate when pushing, opening a PR…" | ~470 | Yes | Acceptable |
| `gitignore` | "Activate when editing or auditing…" | ~360 | Yes | Acceptable |
| `nextjs-app-router` | "Next.js 13+ App Router specialist…" | ~1900 | Yes (heavy keyword list) | Trim |
| `royalty-splits-music` | "Music royalty split modeling…" | ~1100 | Yes | Acceptable |
| `turborepo-patterns` | "Turborepo monorepo build orchestration…" | ~960 | Yes | Acceptable |
| `web-audio-howler` | "Web audio playback specialist…" | ~1500 | Yes | Trim |

Pattern: discipline/workflow skills almost universally lead with a
workflow summary; domain specialists almost universally use a
trigger-keyword list. The specialist pattern is closer to
superpowers' guidance — use it as the template for rewriting the
workflow skills' descriptions.

---

## Appendix B — superpowers skills not present locally, mapped

Quick reference mapping superpowers skills to whether the local
system has an equivalent:

| Superpowers skill | Local equivalent | Status |
|---|---|---|
| `using-superpowers` | none | Add (P1.5) |
| `brainstorming` | `essay` partially | Add `design-before-code` (P0.4) |
| `writing-plans` | `plan-executor` (Mode B) | Upgrade rigor (P2.11) |
| `executing-plans` | `plan-executor` | Stronger locally |
| `subagent-driven-development` | `plan-executor` + agents | Stronger locally |
| `dispatching-parallel-agents` | none | Optional — local plan-executor is sequential by design |
| `systematic-debugging` | none | Add (P0.1) |
| `test-driven-development` | none | Add (P0.3) |
| `verification-before-completion` | `plan-auditor` (partial) | Add general version (P0.2) |
| `using-git-worktrees` | `worktree-orchestrator` | Stronger locally |
| `finishing-a-development-branch` | none | Add (P1.8) |
| `requesting-code-review` | none | Add (P1.7) |
| `receiving-code-review` | none | Add (P1.6) |
| `writing-skills` | `skill-author` (no test methodology) | Augment (P2.12) |

---

## How to use this document

If you are the future agent picking this up:

1. Read CLAUDE.md first for taxonomy and conventions.
2. Read this essay end-to-end. Don't skim — the priorities are
   ordered for a reason.
3. Pick **one P0 item**. Implement it as a single skill file,
   pressure-tested if possible (Gap 6's methodology applies even
   though it isn't formalized yet).
4. Open a PR per skill. Don't batch — descriptions and pressure
   language need per-skill iteration. The `skill-author` skill's
   authoring procedure applies; the new pressure-language tone
   does not match its current decision tree, so propose updates to
   `skill-author` in the same PR if needed.
5. After P0, P1, and P2 are landed, revisit this essay and mark
   `status: resolved` if the gap list is exhausted, or
   `superseded` if a deeper rewrite of the skill system is now in
   scope.

The system is in good shape. Closing these gaps is incremental
hardening, not a rewrite.
