# Current Top-Level Entry Points (snapshot, 2026-04-27)

A catch-up audit — what code is actually running today, what
it does, and how mature each piece is. Names noted where they
read off — but no rename proposals here. Just orientation.


## Web entry points (Browser apps)

Two Elm `Browser.element` boots, both compiled from
`games/lynrummy/elm/`:

| Source | Output | URL | Role |
|---|---|---|---|
| `src/Main.elm` | `elm.js` | `/gopher/lynrummy-elm/` | Full LynRummy game client |
| `src/Puzzles.elm` | `puzzles.js` | `/gopher/puzzles/` | Puzzle gallery (multi-panel) |

Both share the same `Game.*` and `Main.*` source tree. Puzzles
is a vertical gallery of `Main.Play` instances, one per mined
puzzle, sharing a single page-load session id.

**Maturity: both are production code paths.** The full game
runs end-to-end (deal → play → complete turns → score). The
puzzle gallery hosts the "Let agent play" + "Hint" buttons
plus per-panel annotations the user uses to exercise the
agent on real puzzles.


## Server-side handlers (Go)

Three relevant `views/` files, all production:

- `views/lynrummy_elm.go` — full-game HTTP surface: session
  bootstrap, action log fetch, action persistence, complete-
  turn validation. Writes to `lynrummy_elm_actions`.
- `views/puzzles.go` — puzzle HTTP surface: catalog at
  page-load, action persistence, annotations. Writes to
  `lynrummy_elm_puzzle_actions` and `lynrummy_puzzle_annotations`.
- `views/wiki_*.go` and friends — unrelated; the broader
  Gopher site.


## CLI / agent tooling

**Mining + fixture generation** (`tools/`):
- `mine_puzzles.py` — generates 25 puzzles from agent
  gameplay snapshots; writes to `lynrummy_puzzle_seeds`.
  Mature, currently produces the puzzle corpus the gallery
  serves.
- `export_primitives_fixtures.py` — Python verbs +
  geometry_plan output captured per BFS plan step. Asserts
  the post-step pack-gap invariant at generation time.
  Produces `primitives_fixtures.json` plus an auto-generated
  Elm test module.
- `export_replay_walkthroughs.py` — concatenates per-puzzle
  primitive sequences into `replay_walkthroughs.dsl`. Each
  puzzle gets one full-walkthrough DSL scenario.
- `export_corpus_to_dsl.py` and `export_mined_to_dsl.py` —
  emit BFS plan-text scenarios; the corpus side is older,
  the mined side is the post-mining sibling.

All four exporters are stable, regenerate cleanly, and feed
the same conformance pipeline.

**DSL → test code** (`cmd/fixturegen` in Go):
- Reads `games/lynrummy/conformance/scenarios/*.dsl`.
- Emits Go test code, Elm test code, and JSON fixtures.
- Op set: `validate_game_move`, `validate_turn_complete`,
  `build_suggestions`, `hint_invariant`, `enumerate_moves`,
  `solve`, `find_open_loc`, `click_agent_play`,
  `replay_invariant`. Most are mature.

**Python agent core** (`games/lynrummy/python/`):
- `bfs.py` — four-bucket BFS solver with focus rule, iterative
  cap, doomed-third filter. Mature (21/21 corpus + 25 mined).
- `verbs.py` — verb-to-primitive layer (geometry-agnostic).
  Recently restructured (2026-04-27): all per-verb pre-flight
  logic moved out.
- `geometry_plan.py` — the unified post-pass. Walks primitive
  sequences, injects pre-flights at points where the next
  primitive would crowd a pre-existing stack. New module as
  of today's unification work.

Everything else (referee, dealer, etc.) is older-but-stable.


## Conformance test surfaces

Run from `games/lynrummy/elm/`:
- `npx elm-test` — 665 tests pass. Mix of unit (e.g.,
  `Game.PlaceStackTest`), integration
  (`Game.AgentPlayThroughTest`, drives click+drain through
  `Play.update`), and DSL conformance.
- `npx elm-review` — newly installed at the unified level
  (was attempted in two places earlier today and ran into
  cross-project visibility issues). Currently zero findings.

From `games/lynrummy/python/`:
- `python3 test_dsl_conformance.py` — 113 tests pass.


## Names that read off

The "BOARD_LAB" / "board-lab" / "Lab.elm" framing was acted
on later the same day (2026-04-27): the module became
`Puzzles.elm`, the URL `/gopher/puzzles/`, the Go file
`views/puzzles.go`, the table `lynrummy_puzzle_annotations`,
the Python tool `mine_puzzles.py`. See
`lab_to_puzzles_rename.md` for the rename essay and
`~/showell_repos/claude-steve/lab_to_puzzles/MasterPlan.md`
for the multi-task plan.


## What's NOT current (avoid confusion)

- The Cat TS UI (`angry-cat/`) — legacy LynRummy UI. Still
  exists in the repo but isn't in the agent flow.
- Old corpus_report.py and friends — superseded by the DSL
  conformance pipeline.
- Old "review mode" in the Puzzles gallery (formerly
  BOARD_LAB) — ripped 2026-04-26.
