# dispatch — sub-agent dispatch DSL

A pair of scripts that turn an orchestrator's per-dispatch
discipline into machine-checked grammar. The orchestrator's
job (composing a sub-agent prompt, parsing its return) has
load-bearing rules that previously lived as separate prose
memories the orchestrator had to remember to apply each
time. These scripts encode the rules as DSL.

## Why

Two rules in particular were prose-only and easy to forget:

- **Anchor every dispatch in recent churn** — a 1–3 sentence
  hint about what just landed, so the cold sub-agent can tell
  "this prose is stale" from "I don't get this yet."
- **Mandatory IF in every return** — every sub-agent must
  finish with `IF: I could have done this more easily IF...`,
  the orchestrator's only window into friction the sub-agent
  hit silently.

The orchestrator composes dispatches by hand. If a rule is
forgotten, nothing fails loudly — the dispatch just silently
omits the slot, and future cross-session signal is lost.

`dispatch.py` refuses to emit unless the required slots are
present. `parse_return.py` exits non-zero if the IF is absent.
Closure on a real surface, not a stylistic linter.

## Files

- `dispatch_dsl.py` — shared grammar (slot names, required-vs-
  optional, fixed text of the report-back contract). One
  source of truth for the section headers + required-field
  invariants; both scripts import it.
- `dispatch.py` — emitter. Takes structured CLI args, emits
  the dispatch text. Refuses to emit if `--task` or `--churn`
  is empty.
- `parse_return.py` — extractor. Reads a sub-agent's reply
  (stdin or `--file`), pulls out the structured fields,
  emits JSON. Warns + exits non-zero if any required field
  (status, files-changed, IF) is missing.

## Usage

Compose a dispatch:

```
python3 dispatch.py \
    --task "Refactor X to use Y" \
    --churn "Z just landed; W docs not yet swept" \
    --files "path/a.py,path/b.py" \
    --conformance
```

Parse a return:

```
cat reply.txt | python3 parse_return.py
# or
python3 parse_return.py --file reply.txt
```

## What this is not

- Not a linter for letters or essays — those don't need one
  (two LLMs follow templates trivially; the format isn't a
  real variance surface).
- Not a runtime gate on Agent calls — Claude Code's `Agent`
  tool is invoked directly. The script is advisory: run it
  before constructing a prompt to confirm slot completeness,
  paste its output into the prompt.
- Not Brandon-side tooling — Brandon's plan-executor already
  has structured return blocks via `.claude/plan-executor.log`
  and `tools/analyze_ifs/` parses them. This is the analogous
  shape for ad-hoc orchestrators that don't run via plan-
  executor (i.e., today's Steve+Claude default mode).
