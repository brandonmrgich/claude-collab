# BOARD_LAB: a methodology for teaching an agent to mimic a human

*Author: Claude. Collaborator: Steve. 2026-04-24.*

Audience: humans or agents building a similar study loop for
a different game.
Subject: what works, as a how-to.

## The shape of the problem

You have a game with a human player and an agent player.
The agent executes moves that are *legal* but don't *feel*
the way a skilled human would play. The gap isn't the rules —
it's the physical and spatial choices the human makes.

You want to narrow that gap by collecting human examples,
comparing them to agent examples on the same situation, and
feeding the differences back into the agent.

BOARD_LAB is the apparatus that does this. It's a curated
gallery of mid-game puzzles, where the same puzzle is played
by a human (in-browser) and by the agent (via a harness),
and both plays land in one place for side-by-side review.

## The three surfaces

1. **A puzzle catalog.** One file in the canonical language
   (Python for us). Each entry names a puzzle (stable
   snake_case id), a title, a description, and a full
   initial game state. The catalog is the source of truth;
   everything else derives from it.

2. **A play surface.** The normal game UI, but starting
   from a puzzle's initial state instead of a fresh deal.
   One panel per puzzle, embeddable in a gallery page.
   Annotations per session (optional).

3. **A review surface.** The same UI, but showing an
   agent-played session in replay mode. A human reviewer can
   watch the agent's moves unfold and annotate them the same
   way they'd annotate their own plays.

A single analysis command ties them together.

## The data model

Every play — human or agent — is a session in the same
table, keyed by the puzzle's stable name:

- `sessions(id, label, created_at, ...)` — the `label`
  carries the actor tag (`"board-lab: Title [by user]"` or
  `"agent: Title"`).
- `puzzle_seeds(session_id, puzzle_name, initial_state_json)`
  — joins sessions to the catalog entry they played.
- `actions(session_id, seq, action_kind, action_json,
  gesture_metadata)` — the move log.
- `annotations(id, session_id, puzzle_name, user_name, body,
  created_at)` — replies anchored to one specific play.

The load-bearing column is `puzzle_name`. It's what lets
`SELECT ... WHERE puzzle_name = 'X'` return both the
human's attempt and the agent's attempt at the same
situation, so they can be compared without any joins
beyond the natural key.

## The loop

```
   catalog  →  lab gallery  →  human plays + annotates
        │                               │
        └──→  agent harness  ←──────────┘ (sessions keyed by puzzle_name)
                    │
                    ↓
            review mode  →  reviewer annotates agent sessions
                    │
                    ↓
            study.py --feedback N   (read latest replies)
                    │
                    ↓
            adjust agent / catalog / principles
                    │
                    ↓
            (loop)
```

The beat is: add puzzles → human plays → agent plays the
same catalog → compare → encode a rule → repeat. Each
iteration is short (an hour or two), so the agent stays
close to the human's current mental model rather than
drifting on its own.

## Single-command analysis

The analysis script has one load-bearing path:

```
python3 study.py --feedback N
```

It returns the last N annotated plays — puzzle, reviewer's
text, primitive sequence — in a markdown block per play.
The reviewer runs this; the agent reads the output directly.
No joins composed by hand, no schema diving.

If this command starts requiring cleverness to retrieve a
reply, the schema is wrong. Fix the schema (add the column
or the index), don't patch the tool. The original mistake
was anchoring annotations by `puzzle_name` alone, which made
retrieval lossy. Adding `session_id` to annotations turned
the query into one line.

## Catalog discipline

Three invariants the catalog module enforces at build time:

- **Every initial stack is a valid group.** 3+ card sets
  or runs. No orphan pairs on the board — that's not a
  legal mid-game state and the referee will reject it.
- **Every board passes `find_violation`.** No illegal
  geometry slips in.
- **Every puzzle has an agent-recognized trick or
  follow-up merge.** If `strategy.choose_play` returns
  None AND `find_follow_up_merges` returns empty on the
  initial board, the build fails. This prevents the class
  of bug where a human plays a puzzle the agent never
  even attempts — wasted time for the human, no learning
  signal for the agent.

These are cheap checks that run every time the catalog
rebuilds. They've caught real bugs (illegal geometry,
missing trick patterns) without the reviewer seeing them.

## Puzzle design principles

Three rules for picking what to add:

1. **Each puzzle tests one decision.** If a puzzle tangles
   two axes (e.g., crowding AND target-choice), the reviewer
   can't tell which axis drove the human's move. Keep
   puzzles single-axis where possible; stressors that
   combine axes come later, once the single-axis baselines
   are understood.

2. **Distinct shapes, not variants.** Near-duplicates like
   "gap=25" vs "gap=30" test the same thing. Budget is
   quality, not quantity. A subtle caveat: mirror-image
   pairs (left vs right) might look like duplicates, but
   many games have left-right asymmetries — reading
   direction, UI layout, habit — that make the two sides
   genuinely different. Check before pruning.

3. **Keep control puzzles, even when the human is bored.**
   For each "hard" puzzle you add, the pre-existing easy
   version of the same trick stays in the catalog. The
   learning signal isn't just "how did the human solve the
   hard puzzle" — it's the DELTA between the hard and easy
   versions. Expect the human to want to skip the easy
   ones because they feel trivial; the agent should push
   back on this. The tendency is understandable but
   counterproductive — without the easy baselines, the
   hard plays lose their reference point.

## Agent-as-human-proxy conventions

Two settings that make agent replays read as human:

- **Motor fidelity.** The agent's drag paths are real
  paths with acceleration / deceleration curves, not
  teleports. We synthesize ease-in-ease-out trajectories
  at ~5 ms/pixel, matching the pace of a natural drag.
- **Small imperfection.** A fixed 2-pixel jitter on board-
  to-board merge landings. Emphasis on small. A tiny miss
  reads as a human who knew where to land; anything
  bigger reads as bad motor control, which humans know they
  have and don't want to see imitated. Don't emulate human
  weaknesses, only the natural softness around human
  precision. One knob, one small documented value.

Spatial *planning* is smart; motor *execution* is
human-tempo. The agent plays with good judgment at kitchen-
table speed. It is not trying to be dumb; it's trying to be
watchable.

## Annotation is optional, cheap, and opt-in

Every panel has a textarea. The reviewer types a sentence
if something's worth saying and hits Submit. Submitted
replies are anchored to that session (not just that puzzle),
so the next time the human plays the same puzzle, the old
reply doesn't drift onto the new play.

We do NOT prompt the annotation ("What forced your hand?").
Prompts bias what people write, and most of the
interesting signal is just the move sequence itself —
annotations are the edge case where the move alone would
mislead, not the primary data.

## Translation minimization

Agent and client have to agree on a LOT of representations:
card identity, stack identity, coordinates, gesture paths,
frame of reference. Every place where two systems use
different representations for the same concept is a bug
surface.

Three rules that paid off:

- **Catalog uses the same state shape as the wire.** The
  puzzle's `initial_state` field is the same JSON the
  server accepts to create a session. No catalog-to-wire
  translator.
- **Gesture paths are floater-top-left in board frame.**
  Same representation whether Python synthesized them or
  a human captured them; same frame whether the drag is
  mid-play or being replayed later.
- **Error kinds / type names match across languages.**
  Elm's `TooClose` and the wire's `"too_close"` share a
  name. If they drift, renaming to match is cheaper than
  maintaining a translation layer.

## Porting BOARD_LAB to another game

For a game with similar physics (card placement, spatial
drag-and-drop), you'd need:

1. A stable puzzle catalog in your canonical language,
   each entry holding enough state to start mid-game.
2. A `puzzle_name` column on your session table joining
   sessions to catalog entries.
3. A session-anchored annotation table.
4. A UI that can render a play from a puzzle's initial
   state and another that can replay a logged session.
5. An agent harness that iterates the catalog, plays each
   puzzle, and persists the moves in the same session
   shape a human play would use.
6. A `study.py`-style single command to retrieve recent
   annotated plays.

Each piece is small. The discipline is picking the
identifiers once and never translating them.

## What this methodology produces

After a few cycles:

- A corpus of human plays on a curated set of situations.
- Agent plays on the same situations.
- Reviewer annotations explaining where the reviewer was
  surprised.
- A documented set of behavioral rules the agent has
  incorporated.
- An agent that plays close enough to the reviewer's
  style that watching it reads as "another player"
  rather than "a bot."

The cycle is inherently convergent: each iteration
narrows the gap between agent and reviewer, and
reviewers naturally run out of things to annotate as the
gap closes. The endpoint isn't "the agent is perfect";
it's "the reviewer has nothing more to say."

## When to park the apparatus

BOARD_LAB can be parked when the agent's plays are
indistinguishable from a reasonable human's on a large
majority of the catalog, and the remaining divergences are
judgment calls (strategy preferences, individual style)
rather than spatial or motor gaps.

Don't nuke the DB. The historical corpus is valuable: it
documents how the agent evolved, and it's the regression
test if future refactors change agent behavior. But the
active review loop doesn't need to keep running once
divergence hits noise-level.
