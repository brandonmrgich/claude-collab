# Essay surface

**As-of:** 2026-04-29
**Confidence:** Firm — established workflow in active daily use.
**Durability:** Stable; update if the route convention or tools change.

The essay surface is localhost:9100 (claude-collab). It renders
markdown with paragraph-anchored Notes so Steve can reply inline
without paraphrasing or numbering questions. Use it instead of
long console replies.

The Go server lives in `~/showell_repos/claude-collab/server/`.
The reader tool lives in `~/showell_repos/claude-collab/tools/show_comments.py`.

## Quick start

1. Write the markdown file:
   `~/showell_repos/claude-steve/randomNNN.md`
2. Return the URL:
   `http://localhost:9100/steve/randomNNN.md`
3. Steve reads, leaves Notes, says something short on console;
   you read comments back with:
   `python3 ~/showell_repos/claude-collab/tools/show_comments.py randomNNN.md`

That's the entire workflow.

## Not ceremonious

The single most important behavioral point: do not hesitate because
it feels like the reply needs to "earn" the file write with structure
or polish. The essay surface is a better text box, not a publication
venue.

The ceremony is in the wall-of-text console reply — that's the
expensive path (doesn't render, scrolls past, no inline reply
mechanism). The file write is cheaper.

**Threshold:** any reply >15 lines, or with headers / bullet lists /
multiple questions, belongs on the essay surface. Default toward it;
the failure mode is a dense console block, not a file you didn't
need to write.

## Finding the next number

```
ls ~/showell_repos/claude-steve/random*.md | tail -1
```

Increment the number shown. Zero-pad to three digits (`random042.md`).

## URL format — `.md` extension required

The route is `/steve/<filename>`. The `.md` extension must be present:

- Correct: `http://localhost:9100/steve/random042.md`
- Broken: `http://localhost:9100/steve/random042`

Omitting the extension returns a 404 or wrong route. Always include it.

## Notes mechanics (Steve side)

Steve uses the browser UI to leave Notes on individual paragraphs.
The browser writes them to `randomNNN.md.comments.json` as a JSON
array of `{para_index, author, timestamp, text}` objects. `para_index`
is 0-based, blank-line-delimited paragraphs.

You read all Notes in one pass after Steve signals he's done — batch
processing, not real-time polling.

## File locations

| Path | Purpose |
|------|---------|
| `~/showell_repos/claude-steve/randomNNN.md` | Transient session work: Q&A, scope plans, decision points, reviews. Durable on disk but no stronger commitment than that. |
| `~/showell_repos/claude-collab/essays/` | Published durable essays meant to be read independently or by a general audience. |

Do not use `claude-collab/essays/` for transient session work. The
`claude-steve/random*.md` path is the right place for conversational
essays.
