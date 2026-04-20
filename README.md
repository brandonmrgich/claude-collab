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
- **Conventions.** Three documented conventions Steve uses
  with Claude: `.claude` sidecars, memory files, and essays.
  See `CONVENTIONS.md`.
- **Templates.** Example sidecar, example memory entry, and
  demonstration essays showing what the format looks like
  in practice.

## Read first, deploy second

Suggested order:

1. `CONVENTIONS.md` — the three conventions and why they
   exist.
2. `essays/` — one demonstration essay rendered with the
   format. Read it, then load it in the running app and
   try dropping an inline comment.
3. `templates/` — copy these to bootstrap your own files.
4. `server/` — the Go code. Build, configure, run.

## Deploy

See `server/README.md` for build and run instructions.

## Status

Early. The conventions and essays are stable enough to read;
the toolkit is functional but minimal. Expect the repo to
evolve as Steve learns what a fresh reader actually needs.
