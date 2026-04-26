# Plan Executor

A two-layer system for orchestrating multi-task execution plans
with Claude Code. The orchestrator sequences tasks, dispatches
specialized sub-agents, tracks state, and audits completion.
Sub-agents do the actual work — one task, one commit each.

Contributed by Brandon Mrgich.

## Architecture

**Two skills** (live in `~/.claude/skills/`):
- `plan-executor` — orchestrator. Reads a master plan, sequences
  task execution, dispatches sub-agents, persists state to
  `.claude/plan-state.json`, runs a final audit when the plan
  completes.
- `plan-auditor` — independent compliance auditor. Verifies
  acceptance criteria, runs validation commands, writes a
  structured verdict report. Invoked by the orchestrator at
  completion, or by the user on demand.

**Four agents** (live in `~/.claude/agents/`):
- `plan-executor-implementer` — writes application code
- `plan-executor-tester` — writes tests
- `plan-executor-documenter` — writes docs, READMEs, ADRs
- `plan-executor-discovery` — inventory, mapping, surveying

The orchestrator dispatches agents via the Task tool's
`subagent_type` argument. Agents are scoped to one task and
must not orchestrate, parallelize, or move to the next task.

## How a plan works

A plan is two things: a master plan file and a tasks directory
of numbered task files (`00-discovery.md`, `01-foo.md`, etc.).
Each task file declares Context, Prerequisites, Scope, Out of
Scope, Acceptance Criteria, Validation Steps, and Deliverables.

You can provide both upfront (Mode A), or give the executor a
goal and let it generate them (Mode B). Either way, the executor
walks the task list in order — one sub-agent per task, one commit
per task.

State persists across sessions in `.claude/plan-state.json`. If
a session ends mid-plan, invoking `plan-executor` in the same
project resumes from where it left off.

## Install

1. Copy `skills/plan-executor/` to `~/.claude/skills/plan-executor/`
2. Copy `skills/plan-auditor/` to `~/.claude/skills/plan-auditor/`
3. Copy `agents/*.md` to `~/.claude/agents/`
4. Add the CLAUDE.md snippet (below) to your global `~/.claude/CLAUDE.md`

## CLAUDE.md snippet

Add this to your `~/.claude/CLAUDE.md` to activate the system:

```markdown
## Plan execution system

Two-layer system installed user-wide:

**Skills (`~/.claude/skills/`):**
- `plan-executor` — main orchestrator. Sequential, dispatch-and-collect.
- `plan-auditor` — independent compliance auditor (separate skill, invoked on-demand)

**Agents (`~/.claude/agents/`):**
- `plan-executor-implementer` — agent for code implementation tasks
- `plan-executor-tester` — agent for test-writing tasks
- `plan-executor-documenter` — agent for documentation tasks
- `plan-executor-discovery` — agent for inventory/discovery tasks

The orchestrator dispatches agents via the Task tool's `subagent_type`
argument. Agents are registered at `~/.claude/agents/<name>.md` and the
`name` in the file's frontmatter must match.

**To run a plan:** invoke `plan-executor` with a master plan path and
tasks directory. State is persisted to `.claude/plan-state.json` in the
current project, so execution resumes across sessions.

**Failure behavior:** stop-and-ask on non-trivial failures.

**Auditing:** plan-executor invokes plan-auditor only on demand mid-plan,
automatically once at plan completion.
```
