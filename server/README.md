# claude-collab server

A minimal Go HTTP server that renders the essays in `../essays/`
with inline paragraph-anchored comments. Localhost-only. No
auth, no database. Comments live as JSON files next to their
essays (`foo.md` → `foo.md.comments.json`).

## Build and run

```
cd server/
go mod tidy
go run .
```

Then open http://localhost:9100.

Defaults: port 9100, essays directory `../essays` (resolved
from the working directory). Override with flags:

```
go run . --port 9200 --essays /path/to/my/essays
```

## Files

- `main.go` — routes + bootstrap.
- `essays.go` — list view + single-essay render.
- `article_comments.go` — GET/POST `/article-comments`; the
  JS widget injected into each essay.
- `markdown.go` — goldmark renderer (CommonMark + GFM).
- `helpers.go` — page shell.

Five small files. All the collaboration ergonomics sit in
`ArticleCommentsJS` — the inline widget code.

## Conventions

- Essays: put `*.md` files in the essays directory.
- First `# Heading` in the file becomes the display title.
- Comments: editable JSON files alongside each essay. Manual
  edits are fine; the UI is append-only.
- Port 9100 (not 9000) so it doesn't clash with angry-gopher
  running on the same machine.
