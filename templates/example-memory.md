---
name: Example memory — delete me after you've read it
description: Demonstration of the memory file format; replace with your own first real memory entry
type: feedback
---

A memory is a durable note that an agent keeps across
conversations. Each memory file is a small Markdown document
with YAML frontmatter (`name`, `description`, `type`) and a
short body.

## Types

- **`user`** — who the human is, what they prefer, how they
  like to work.
- **`feedback`** — corrections or confirmations from the
  human that should outlive the current session.
- **`project`** — facts about the current project: its
  state, stakeholders, decisions, in-flight work.
- **`reference`** — pointers to external resources (URLs,
  file paths, other people's docs).

## Body structure

For `feedback` and `project` types, a good template is:

- The rule or fact itself, stated plainly.
- **Why:** the reason the rule exists (often an incident,
  a strong preference, or a constraint).
- **How to apply:** when the rule kicks in and what
  behavior follows.

The **Why** matters most. A rule without context rots
fast; a rule with context lets future-agent judge edge
cases instead of blindly applying the letter.

## Indexing

Add a one-line pointer to each new memory file in a
top-level `MEMORY.md` index — one line per memory, under
~150 characters, with a short hook describing what's
inside. The index is what the agent reads first on every
session; individual memory files are loaded on demand.

## Discipline

- Update memories that go stale.
- Delete memories that lose their subject (a memory
  pointing at code that no longer exists is noise).
- Don't save memories for things the code itself already
  tells you — the source is the source of truth for what
  code does.
