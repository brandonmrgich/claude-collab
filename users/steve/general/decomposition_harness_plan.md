# Decomposition Harness

A test-first plan to teach the Python `auto_player` to produce
the same primitive wire actions a human produces — so motor-
fidelity replay works on agent-played games, not just yours.

Three layers, built bottom-up: harness, per-trick loop, gesture
synthesis.

## Harness

A Go endpoint that creates a session from a hand-crafted
initial state instead of the dealer's deal. This is what lets
us stage narrow puzzles — "one hand card, a few board stacks,
one obstacle" — that isolate a single trick without the noise
of a full game.

A Python catalog — `tools/lynrummy_elm_player/puzzles.py` —
of named puzzle specs. Each spec is hand + board + obstacle
stacks + the trick it exists to exercise. Starts with one
entry; grows one trick at a time.

A CLI — `puzzle_harness.py` — with three commands:
`--list` (catalog inventory), `--play <name>` (creates the
session and prints the Elm URL for you to open), and
`--compare <name> --session <id>` (diffs your primitive
sequence against the decomposer's).

## Per-trick loop

For each trick in ascending complexity — HandStacks, PairPeel,
PeelForRun, SplitForSet, LooseCardPlay, then rb_swap — you
pose the puzzle, I build the decomposition, we compare until
equivalent, then move on. One trick per iteration.

## Non-determinism: why the comparison has to be fuzzy

Your choice of open-loc is a free variable. You pick `(300,
100)` for a new stack this run and `(320, 90)` next run, both
perfectly fine. The decomposer shouldn't have to reproduce
your exact coordinates — it just has to produce an equivalent
solve.

"Equivalent" means three things:

- **Same sequence of primitive kinds.** `split, split,
  move_stack, merge_hand, merge_hand` — in that order.
- **Same logical targets.** Split *that* stack at *that* card
  index (the one containing the trick's target card); merge
  *that* hand card onto *that* newly-formed stack.
- **Locations that fit geometrically.** Inside the board, no
  overlap with obstacles, enough room for the subsequent
  merges. Not locations that match yours exactly.

The `--compare` tool prints the two sequences side-by-side and
labels each step `match` / `equivalent` / `differ`. A `differ`
line shows up immediately; the fuzzy matches don't generate
noise.

## Gesture synthesis

This part drops in after decomposition works.

`telemetry.py` already reads your captured drag paths from
`lynrummy_elm_actions.gesture_metadata`. One calibration pass
over your played sessions computes pixels/ms per drag and
takes the mean — a single velocity number.

A new `gestures.py` provides
`linear_drag(start_xy, end_xy) -> {"path": [{t,x,y}, ...]}`
with `duration_ms = distance / avg_velocity` and samples
spaced evenly along the line. `client.send_action` gets a
wrapper that synthesizes a gesture for every primitive the
auto_player emits.

Elm replay has no way to distinguish a synthesized path from
a real one. No Go edits, no Elm edits.

## Exit criterion

After each trick lands green in `--compare`, and `gestures.py`
is wired, the final test is a visual one: play a full game
through `auto_player`, watch it in Elm replay, and confirm
that nothing teleports and the motion reads as a slightly-
robotic but recognizably-human drag sequence.

## Open questions

**The puzzle-session endpoint.** Cleanest way to stage
arbitrary initial state is a new Go endpoint:
`POST /gopher/lynrummy-elm/new-puzzle-session` taking
`{label, board, hands, deck, active_player_index}` and seeding
the session. About 40 lines of Go. Is that the path, or is
there a cheaper staging mechanism I'm missing?

**The first puzzle.** HandStacks is the simplest — no
obstacle, three primitives (place_hand + merge_hand +
merge_hand), good harness shakedown. Any reason to start
somewhere else?

**Fuzzy-match tolerance.** The `equivalent` label covers
"kinds and logical targets match, locations are geometrically
valid." Is there a tighter spec you'd want — e.g., locations
within a pixel radius of yours, or any open spot that fits?
Looser is easier to build; tighter catches more regressions.
