# reorg

Language-aware batch package / module mover. Reads a script of
move lines and executes them as directory moves AND code
rewrites, so imports, package declarations, and qualified
references all stay consistent.

Two languages supported today: Go (`mv`) and Elm (`elm-mv`).

## Usage

```
# Dry-run (default — shows every rewrite that would happen):
go run main.go SCRIPT

# Apply for real:
go run main.go --execute SCRIPT
```

Run from the **root of the project being reorganized**, not
from this directory. The tool needs to find `go.mod` (for `mv`)
or `elm.json` (for `elm-mv`) by walking upward from the source
path.

## Script grammar

```
# Comments and blank lines are ignored.

# Go move: rewrites import paths + package declarations across
# every .go file in the repo.
mv auth/ core/auth/

# Elm move: rewrites `module X` headers + qualified `X.Y`
# references across every .elm and .claude file under the Elm
# project. The Elm project root is auto-detected via the
# nearest elm.json walking up from the source path.
elm-mv games/lynrummy/elm/src/LynRummy/ games/lynrummy/elm/src/Game/
```

## Go semantics (`mv`)

- For each move, scans every `.go` file for quoted imports
  matching the old package path or any sub-package and records
  rewrites.
- If the directory basename changed (e.g. `auth/ → core/newauth/`),
  records `package X` → `package Y` rewrites for files in the
  moved subtree.
- On `--execute`: rewrites imports, moves directories, rewrites
  package declarations, runs `go build ./...` to verify.

## Elm semantics (`elm-mv`)

- Reads `source-directories` from `elm.json` (defaults to `src`).
  Also treats `tests/` as a source-dir if it exists, by
  elm-test convention.
- Old/new module prefixes are derived from the path relative to
  the source-dir, with `/` converted to `.`. So
  `src/LynRummy → src/Game` becomes prefix rewrite
  `LynRummy → Game`.
- Scans every `.elm` and `.claude` file under the project root.
- Regex: `\b<oldPrefix>(\.\*|\.UpperCase[.Chain]*\b)` — matches
  `OldPrefix.Card`, `OldPrefix.Tricks.Hint`, and `OldPrefix.*`
  (the wildcard shorthand common in sidecars). Bare references
  without a `.` follow-up (e.g. the word "LynRummy" in prose)
  are NOT rewritten — prose mentions of a project name survive.
- After executing, runs `./node_modules/.bin/elm make
  src/Main.elm --output=/dev/null` (falls back to `elm` on
  `$PATH` if no pinned local install).

## What the tool does NOT do

- Does NOT update references from outside the language
  ecosystem being moved. A Go comment mentioning
  `elm/src/LynRummy/X` won't be rewritten by `elm-mv`. Use
  `grep + sed` for the post-move sweep of doc paths,
  reviewing each hit.
- Does NOT update code generators that emit module references
  in string templates. Update those by hand before re-running
  the generator.
- Does NOT handle single-file Elm renames (renaming
  `Game/Game.elm` to `Game/Turn.elm` would only change one
  module name's last segment). Different verb; not built.

## Provenance

Pulled from `angry-gopher/cmd/reorg/`. Last load-bearing use:
the `LynRummy → Game` Elm rename of 2026-04-21. Adapt freely
for your own projects; this copy is a snapshot, not a
synchronized source.
