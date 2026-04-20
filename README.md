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
  See [CONVENTIONS.md](CONVENTIONS.md).
- **Templates.** Example sidecar, example memory entry, and
  demonstration essays showing what the format looks like
  in practice.

## Essays

Read on GitHub (rendered), or locally in the running app to
try the inline-comment mechanic. Suggested first read is
*Inclinations, Not Deficits* — the frame the others build on.

- [Inclinations, Not Deficits](essays/inclinations_not_deficits.md)
  — route work to inclinations, not to imagined deficits
- [The Ergonomic Gap](essays/the_ergonomic_gap.md) — humans
  and agents have asymmetric retrieval costs; close the gap
- [Ebb and Flow](essays/ebb_and_flow.md) — zoom-in /
  zoom-out rhythm; announce mode transitions
- [Where to Put the Files](essays/where_to_put_the_files.md)
  — agents aren't configured; they're asked
- [DSLs as Distillation](essays/dsls_as_distillation.md) —
  designing a DSL IS the abstraction work; mechanics are
  cheap, so the creative act dominates
- [Smells vs. Anti-Patterns](essays/smells_vs_anti_patterns.md)
  — a smell is a signal to investigate, not a rule to apply;
  the work is the investigation, not the conclusion
- [Fish in the Water](essays/fish_in_the_water.md) —
  expertise compresses assumptions; an agent's naive
  questions surface them
- [On the Quiet Paragraph](essays/on_the_quiet_paragraph.md)
  — why paragraph-anchored comments change the feel of
  reading

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
