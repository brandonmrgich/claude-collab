# Framing: the first move, seen through Steve's screen

## Scope

The task: the Python player executes the first move of the game
— play the `7H` from the hand onto the 7-set on the board. One
move. Nothing else.

## Who is watching

A human — Steve — is watching the Elm app. The whole point of
the Python player isn't to "play a game of LynRummy" in some
private simulation. It's to play a game that Steve can see
happening through the Elm UI.

This reframes what "the move" is. The move isn't an abstract
`merge_hand(target=3, side=right)`. The move is "pick up the
7H from where it's sitting in Steve's viewport and set it down
on the right edge of the 7-set where the 7-set is sitting in
Steve's viewport."

## The implication: shared geometry

Python and Elm need to agree, in advance, on the geometry of
what Steve sees. Not at runtime, not via DOM introspection —
in advance. A single declared layout both sides consult.

Python doesn't invent coordinates. Python reads the agreed
geometry and says "the 7H in the hand is at (x₁, y₁); the
7-set's right edge is at (x₂, y₂); compose a move from there
to there." Elm renders the same geometry and so (x, y) on
Python's side equals (x, y) on Steve's screen.

Without that agreement, Python is generating telemetry in a
frame of reference Elm doesn't share, and what Steve sees is
noise — a floater landing nowhere near the cards, or nothing
at all.

## The implication: human time

A move isn't a wire event. It's something Steve watches
happen. Two time scales matter, and both need to be set in
human-visible units, not arbitrary constants:

1. **Between major events** — on the order of a second.
   Pre-roll before the first move. Beat between moves. Long
   enough that Steve can register "this is the starting
   board," then "the hand card lifted off," then "it landed on
   the 7-set," as discrete perceivable moments. Shorter than
   that, they blur.
2. **During the drag itself** — on the order of Steve's own
   drag velocity when he plays. The drag duration is a
   function of the distance traveled, not a fixed number. A
   card going a short distance moves fast; a card going across
   the board takes longer. The metric is "pixels per second at
   human speed."

## What this doesn't commit to (yet)

- The specific values of the shared-geometry constants.
- Where the shared-geometry constants live in the repo (a
  single source file, code-generated across languages, etc.).
- The specific value of "Steve's drag velocity."
- How this layer interacts with real human drags, which DO
  come from DOM events at live viewport coordinates — i.e.,
  whether the agreed-geometry shortcut ever disagrees with the
  live rendering and what we do about that.

## What I think I now understand

- The bug Steve kept seeing wasn't a timing bug in Elm's
  replay state machine. The state machine was doing what it
  was supposed to do. The coordinates I was feeding it were
  in the wrong reference frame, so the visible motion went
  somewhere nobody was looking.
- "Fix the drag" was framed as a coordinate-transform problem
  on my side. It's actually a geometry-agreement problem
  between two sides, and neither side should be introspecting
  the other's rendering to find out where things are.
- The time-scale question is separate from the coordinate
  question. Even if the coordinates were right, a 300ms drag
  with no pre-roll reads to a human as "something flickered."
  Human-visible animation needs human-time budgets.
