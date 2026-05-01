# analyze_ifs

Extracts and ranks `this_would_have_been_easier_if` entries from a
`plan-executor.log`. Surfaces which spinup briefs are overdue for
refresh and which tooling gaps have been flagged but never built.

## Usage

```bash
python3 analyze_ifs.py [repo_path]
```

`repo_path` defaults to the current directory. Reads
`.claude/plan-executor.log` from that root.

## Output

- **Category counts** — spinup-brief / tooling / task-spec / other,
  with fixed vs. deferred breakdown.
- **DEFERRED spinup-brief IFs** — these are brief gaps that were
  named but not fixed. The ones that recur across dispatches are
  highest priority for a brief refresh pass.
- **Tooling IFs not yet actioned** — scripts or tools that sub-agents
  requested but were deferred. Escalating flags (same tool named
  twice or more) are worth building next.

## What it doesn't do

- Doesn't read briefs directly — it only knows what sub-agents said
  about them. Cross-referencing with actual brief content is manual.
- Clustering is keyword-based and coarse. Similar IFs phrased
  differently won't group together.

## Source

Built as a canonical claude-collab tool (2026-04-29). Not a
snapshot from another project.
