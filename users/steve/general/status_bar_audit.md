# STATUS_BAR audit — where we write today vs. where we should

## Every current status-bar write

Ten sites, no hidden ones:

| # | Where | Trigger | Message | Kind |
|---|---|---|---|---|
| 1 | `Main/State.elm:398` | Fresh-model initial value | "You may begin moving." | Inform |
| 2 | `Main/Replay/Time.elm:106` | ClickInstantReplay | "Replaying…" | Inform |
| 3 | `Main/Replay/Time.elm:159` | Replay walker exhausted | "Replay complete." | Celebrate |
| 4 | `Main.elm:72` | Reopen session via URL | "Resuming session N…" | Inform |
| 5 | `Main.elm:175` | ClickCompleteTurn with dirty board | "Board isn't clean: ..." | Scold |
| 6 | `Main.elm:235` | CompleteTurnResponded (Ok branch) | `statusForCompleteTurn` | varies |
| 7 | `Main.elm:264` | CompleteTurnResponded (Err branch) | `statusForCompleteTurn` | varies |
| 8 | `Main.elm:381` | ClickHint (hint fires) | `first.description` | Inform |
| 9 | `Main.elm:392` | ClickHint (no hint) | "No hint — no obvious play…" | Inform |
| 10 | `Main/Apply.elm:131` | `applyCompleteTurn` runs | "Turn N — Player M to play." | Celebrate |
| + | `Main/Gesture.elm:237` | Drop-off-board scold (today's commit) | "Don't knock cards off the board, please. You're not a cat!" | Scold |

## Where we should write but don't

The big gap: **none of the five physics actions write to the
status bar.** `applyPhysics` in `Apply.elm:103–116` does its job
(board + score + hand update) and returns. The only action that
writes status is `CompleteTurn` via `applyCompleteTurn`. So
after any successful drag, the status bar keeps showing whatever
it showed before — typically a stale hint message or "You may
begin moving." left from initialization.

That explains the "celebration messages are broken" surprise.
They weren't broken — they were never written into the Elm
port's physics layer. The TS original presumably had per-action
status writes colocated with the action handlers; the Elm port
consolidated physics through `applyPhysics` and didn't port that
part of the TS UX.

## Proposed messages (your call, but a starting point)

Per your ask: cosmetic `MoveStack` says "Tidying noted." as
Inform. The others should be a mix of Inform and Celebrate
based on whether the action made the board *cleaner* or just
different.

| Action | When | Text | Kind |
|---|---|---|---|
| `Split` | any | "Split." | Inform |
| `MergeStack` | any | "Stacks merged." | Celebrate |
| `MergeHand` | any | "Hand card played." | Celebrate |
| `PlaceHand` | any | "New stack started." | Inform |
| `MoveStack` | any | "Tidying noted." | Inform |

Simpler than "count score delta" or "detect whether the merge
produced a longer run." Keeps complexity out of the status layer,
per your "no fancy timeouts or state tracking" constraint.

## The natural-clearing mechanism

You said: no timeouts, no TTL. The message clears itself because
the next human action overwrites it. If every action writes,
that works. If some actions (today: all physics ones) don't
write, stale messages linger. So the fix is just: every action
writes. No other machinery needed.

## Where to wire it

Two reasonable spots:

**(A) Inside `applyAction`** in `Main/Apply.elm`. Add a
`statusForAction : WireAction -> StatusMessage` helper, call it
after each physics branch. Pro: one place owns the mapping, all
callers of `applyAction` benefit (replay would also write status
on each replayed step — which is either nice or noisy depending
on taste). Con: replay-time status writes would clobber
"Replaying…".

**(B) Inside `handleMouseUp`** in `Main/Gesture.elm`. Only human
drags go through here; replay bypasses it. Pro: scope is
exactly "the human just did something," which matches your
framing. Con: duplicate mapping if a future feature (e.g.,
opponent-delivered action) needs the same messages.

My gut is (B) — it's the literal answer to your "whenever a
human completes an action." Replay deliberately stays in
"Replaying…" until it finishes. Pick A if you want status
writes to be a universal action-level concern.

## Scope boundary

One thing NOT in this audit's scope: popups. You already have
`popupForCompleteTurn` and `PopupContent` machinery for
turn-boundary ceremony — those are separate from the status
bar and I'm leaving them alone unless you ask.
