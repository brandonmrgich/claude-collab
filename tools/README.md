# tools

> **IN TRANSITION (2026-04-29):** The tools model is being
> revised. Agent workflow tools will be built here canonically
> (not copied in from other projects). Skip this directory
> until the transition is complete — do not add new tools as
> snapshots from angry-gopher.

General-purpose scripts and small utilities pulled from
project-specific repos. The convention here is **snapshot, not
import**:

- Each tool's source-of-truth lives in the project where it was
  written (today, mostly `angry-gopher`). The version in this
  directory is a copy.
- No two-way sync. If you find a tool in here useful, copy it
  into your own project and adapt freely. Improvements made
  downstream don't flow back automatically; they flow back
  through conversation, if at all.
- Each tool gets its own subdirectory and its own `README.md`.
  The README explains what the tool does, when to use it, and
  what it doesn't do. The actual source files live alongside.

The point is to make it cheap for another Claude (or another
human) to find a useful tool, understand it, and adapt it —
without having to navigate a strange project's source tree to
get there.

## What's here

- **`reorg/`** — language-aware batch package mover for Go and
  Elm. Reads a script of `mv` / `elm-mv` lines and rewrites
  imports, module declarations, and qualified references across
  the codebase before moving the directories. Dry-run by
  default; `--execute` applies. Was the load-bearing tool for
  several major rename passes in `angry-gopher` (Go reorg into
  `games/`, Elm `LynRummy → Game` rename). Source: cloned from
  `angry-gopher/cmd/reorg/`.

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
