# claude-collab

A small toolkit + set of conventions for collaborating with
Claude on long-running projects. Built by Steve, extracted
from `angry-gopher` on 2026-04-20 so others can use the parts
worth sharing.

This is a starting point, not a polished product.

## What's here

- **The essay format.** A minimal web app that renders your
  markdown essays with inline paragraph-anchored comments —
  the ergonomic surface Steve uses to read Claude's drafts
  and react in-line without leaving the text. Deployable
  locally with Go; comments are stored as JSON sidecar
  files alongside each essay.
- **Conventions.** Two documented conventions Steve uses
  with Claude: memory files and essays.
  See [CONVENTIONS.md](CONVENTIONS.md).
- **Templates.** Example sidecar, example memory entry, and
  demonstration essays showing what the format looks like
  in practice.

## Essays

Read on GitHub (rendered), or locally in the running app to
try the inline-comment mechanic. The `essays/` directory is
the canonical list — only what's on disk is linked here.

- [Where to Put the Files](essays/where_to_put_the_files.md)
  — agents aren't configured; they're asked
- [LLM Economics](essays/llm_economics.md) — many costs
  crossed below the interrupt-flow threshold at once;
  workflows that used to be foreclosed are now routine;
  re-evaluate what you flinch at as "too much work"

## Directory convention

- `/essays/` — **published** pieces. Transcend Steve-
  concerns; speak to a broad audience about collaboration
  patterns. Stable-linked; don't rename.
- `/users/<name>/general/` — **real-time** space, one per
  contributor. Drafts, working notes, essay-reply
  correspondence that hasn't earned (or doesn't need) the
  general-audience jump. Currently just `/users/steve/
  general/`; structure is ready for others.
- `/agent_collab/` — **agent-facing operational docs.**
  If you're a sub-agent doing work in this repo, start here:
  [`AGENT_CONVENTIONS.md`](agent_collab/AGENT_CONVENTIONS.md),
  [`ESSAY_SURFACE.md`](agent_collab/ESSAY_SURFACE.md),
  [`ORCHESTRATOR.md`](agent_collab/ORCHESTRATOR.md).
- `/templates/` — copy-from-here starting points for the
  conventions.
- `/server/` — the local-reading toolkit.

Graduation from a user's general/ to the published
`/essays/` is a deliberate act, not a drift.

## Read first, deploy second

Suggested order:

1. `CONVENTIONS.md` — the three conventions and why they
   exist.
2. `essays/` — read a few on GitHub (they're linked above).
   *Inclinations, Not Deficits* is a good starting point;
   the others stand alone.
3. `templates/` — copy these to bootstrap your own files.
4. `server/` — the Go code. Build and run to read the same
   essays with inline paragraph-anchored comments enabled.

## Deploy

See `server/README.md` for build and run instructions.

## Status

Early. The conventions and essays are stable enough to read;
the toolkit is functional but minimal. Expect the repo to
evolve as Steve learns what a fresh reader actually needs.
