# tools

General-purpose scripts and small utilities. Two kinds of
tools live here:

- **Snapshots from other projects** — source-of-truth lives in
  the originating project (today, mostly `angry-gopher`); the
  version here is a copy. No two-way sync. If you find one
  useful, copy it into your own project and adapt freely.
- **Canonically-here tools** — tools written specifically to
  support work in `claude-collab` itself (essay tooling, plan-
  executor instrumentation). Source-of-truth lives here.

Each non-trivial tool gets its own subdirectory and its own
`README.md`. The READMEs explain what the tool does, when to
use it, and what it doesn't do.

The point is to make it cheap for another Claude (or another
human) to find a useful tool, understand it, and adapt it —
without having to navigate a strange project's source tree to
get there.

## What's here

- **`reorg/`** *(snapshot)* — language-aware batch package
  mover for Go and Elm. Reads a script of `mv` / `elm-mv` lines
  and rewrites imports, module declarations, and qualified
  references across the codebase before moving the directories.
  Dry-run by default; `--execute` applies. Was the load-bearing
  tool for several major rename passes in `angry-gopher` (Go
  reorg into `games/`, Elm `LynRummy → Game` rename). Source:
  cloned from `angry-gopher/cmd/reorg/`.
- **`analyze_ifs/`** *(canonical)* — extracts and ranks IF
  entries (`I could have done this more easily IF...`) from
  `.claude/plan-executor.log`, classifying them by gap type
  (spinup-brief, tooling, task-spec) and surfacing the spinup
  briefs most due for refresh.
- **`show_comments.py`** *(canonical)* — renders an essay file
  with its inline `.comments.json` sidecar interleaved as quoted
  reader notes. Used to read essay-surface replies in plain
  text without the browser. Single-file tool; no subdirectory.

## Why "snapshot, not import"?

The alternative — making this directory the canonical home and
having projects import from it — sounds appealing but pays a
real cost. Tools are short. They evolve with their projects.
Coupling a tool's lifecycle to a separate repo means the
canonical project has to wait on a multi-repo dance to make a
local change. Worse, the tool starts hedging because it has to
serve more than one project well.

The snapshot model accepts that copies of useful tools will
duplicate on disk, and bets that the duplication is cheap (these
are short scripts) and that drift across copies is fine (each
project owns its version). Steve's `feedback_eliminate_round_trips`
generalization applies: shipping the data once, no coordination
required, beats coordinated lazy fetching at small scale.
