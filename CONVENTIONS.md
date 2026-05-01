# Conventions

Two conventions Steve uses when working with Claude on
long-running projects. Neither is mandatory. Both reinforce
each other.

## 1. Memory

Durable notes Claude keeps across conversations. Live in
a per-project directory (Claude Code manages the path).
Written as Markdown files with YAML frontmatter.

**Types**:
- `user` — who Steve is and how he prefers to work.
- `feedback` — corrections and confirmations — guidance
  that should outlive the current session.
- `project` — facts about the project's current state,
  stakeholders, decisions.
- `reference` — pointers to external resources.

**Format**: each file has a `name`, `description`, and
`type` in frontmatter; body is a short structured note
(typically: the rule, a `**Why:**` paragraph, a
`**How to apply:**` section). Memory files are indexed in
a top-level `MEMORY.md` that Claude reads on every session.

**Discipline**: save memories when Claude learns something
non-obvious from code state OR from Steve's corrections.
Update memories that go stale. Delete memories that lose
their subject.

See `templates/example-memory.md`.

## 2. Essays

Long-form markdown files where Claude or Steve work out an
idea in prose. Rendered with inline paragraph-anchored
comments, so the reader can react to a specific paragraph
without breaking flow.

**Why prose matters**: not every thought is a ticket, a
commit message, or a chat turn. Some ideas need 400-800
words to sit in. Essays are where that happens.

**Why inline comments matter**: the comment is tied to the
paragraph it's about. The original writer can't hide from
specific objections; the commenter can't flatten
everything into a single thread.

**Lifecycle**: many essays are disposable — written to
think, then discarded or compacted into memory. A few
turn out to be durable and get promoted to named docs in
the project tree. The disposability is a feature; quality
is cheap to regenerate in the next session.

See `templates/example-essay.md` for the form, and the
`essays/` directory for one demonstration essay rendered
in-place.

## How the three fit together

| Convention | Lifetime   | Audience              | Shape        |
|---         |---         |---                    |---           |
| Memory     | Persistent | Claude (self)         | Structured   |
| Essay      | Occasional | Human (maybe public)  | Prose        |

Memory answers "what did we learn that should outlive this
session." Essays answer "let me think this through in
prose before it becomes either."

They reinforce: an insight that lands in an essay often
deserves to be distilled into a memory; a memory that has
grown into a principle often deserves an essay to explain
the reasoning behind it.
