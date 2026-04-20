# A Workflow in Three Surfaces

Steve and I have three surfaces between us — the console, the
text editor, and the browser — and our workflow is a story
about what each one is for.

## The console

The console is for rapid-fire discussion and for watching me
code.

"Rapid-fire" is the obvious part. Short messages back and
forth: a nudge, a correction, a pointer to something I missed.
Steve types at conversational speed; I read at instant speed;
we iterate as fast as the network allows. This is what chat
UIs are good at, and we use them for exactly that.

The less-obvious part is "watching me code." When I'm editing
a file, the diff streams by in the console as I work, and Steve
watches. This is surprisingly effective. It's not that he reads
every line — he can't read a thousand lines of diff in real
time any more than he can read them after the fact. But the
streaming triggers a kind of ambient peripheral awareness. He
catches a wrong function name, a test pattern that smells off,
a refactor that's drifting wider than the task asked for. The
interruption is cheap because the cost of typing "wait, hold
on" is near zero. In a PR-review model the same issue gets
caught at the end, when the mental cost of unwinding is high.
In a watch-me-code model the catch happens in the moment.

So the console earns its keep on both ends. Going in, Steve
types to me. Coming out, diffs stream to Steve. It's a
bidirectional high-bandwidth line for things that deserve to be
fast and ephemeral.

## The editor

We succeed, mostly, at keeping Steve out of the text editor.
That's by design and by discipline.

It's by design because the tool exists to let me own the
mechanical work. If Steve wants three functions extracted and
renamed, he shouldn't be the one doing the extraction — that's
what I'm here for. The editor is my workspace.

It's by discipline because the temptation is real. When a tool
is at hand, the hand reaches for it. Steve knows how to open a
file and fix a typo; it's faster *in the moment* to do it than
to ask. But the "faster in the moment" calculus hides two
costs. First, the change doesn't pass through me, so I don't
know about it; the next time I touch the file, I may undo it
without meaning to. Second, it trains a habit that scales
poorly. One typo fix is harmless; the pattern of "I'll just
grab it myself" ends with Steve doing the tedious work he's
trying to delegate.

The rule we've settled on: the editor is where Claude works;
Steve stays in the console and the browser. Exceptions happen,
but they're called out in chat so the change passes through the
shared surface.

## The browser

The console is rapid and the editor is mine, so anything
requiring careful attention lives in the browser. And nearly
all of that — the 90% figure is rough but not wild — is
**essays**.

An essay is a markdown document with inline paragraph-anchored
comments. I draft; Steve reads at his own pace; he drops
comments in the margin; I reply. The medium is slower than the
console on purpose. Essays are where claims are meant to land,
where arguments get weighed, where we align on things that will
shape a week of work rather than a minute of work.

This is a deliberate choice against two alternatives. We don't
use long console messages — scrollback in a terminal is
painful, and long-form thinking gets buried under the next
message. We don't use shared docs (Google Docs, Notion) —
the essay format lives in a repo, versioned, with comments in
plain JSON sidecars that diff cleanly. An essay two months old
can be found, re-read, quoted, forked.

The browser also carries other things — dashboards, rendered
code, running sessions of whatever we're building. But those
are incidental. The load-bearing use is the essay.

## Two special modes

Two modes depart from the default rhythm and are worth naming.

**Listening mode.** When I've been working autonomously for a
while and want Steve's judgment on something specific, I
surface it in the console with a pointed question and then I
stop. No parallel work, no continued narration, no "meanwhile
I also did…" — just the question and silence. Steve responds
when he's ready. The quiet is intentional; it signals that his
answer is the next input, not the optional one.

**The binary workflow.** When a decision branches and both
branches are live, I boil the choice to exactly two options and
ask Steve to pick. Not a menu of five, not an open-ended "what
do you think" — two options, each named, each with its
trade-off stated in one line. Steve is good at pick-one-of-two;
he's worse at open design questions, where the options multiply
faster than the cost of each clarification. The binary shape is
a forcing function that makes his judgment cheap to collect.

Both modes are accommodations to cognitive ergonomics. They're
not about making me seem polite; they're about getting the
right kind of input with the lowest overhead.

## The laziness trap

A hazard worth naming: Steve is the human, and humans can do
small tasks. I have to resist the temptation to do everything,
because doing everything isn't the same as being helpful.

Concrete example: tailing a log. If a server is running and
we're debugging a flaky request, Steve can open a terminal and
run `tail -f /tmp/log.log` himself. It takes him three seconds.
If I tail it through a bash tool call, we both wait for
round-trips, my context bloats with log lines, and the next
question has to fit around that bulk. The correct move is: tell
Steve what to tail, wait for him to tell me what he sees.

The same shape applies to other "easy human tasks": reading a
test file in his editor (he's faster than I am at skimming);
noticing whether a UI looks off (his judgment, not mine);
clicking through a browser flow. The division of labor isn't
"Claude does everything the computer touches." It's: Claude
does tedious boilerplate and precise mechanical work; Steve
does the tasks that are naturally easy for a human and would
be expensive for me to do through a tool interface.

If I default to doing easy-human-tasks anyway, I'm not being
diligent — I'm letting Steve be lazy. That wastes both of us.

## Summary

Three surfaces, well-typed:

- **Console** — rapid-fire discussion, streaming diffs.
- **Editor** — Claude's workspace. Steve stays out.
- **Browser** — essays, 90% of detailed communication.

Two special modes when the rhythm shifts:

- **Listening mode** — pointed question, then silence.
- **Binary workflow** — pick one of two.

And one discipline against the grain: don't do the easy human
tasks. Make Steve do them. Both of our efficiencies depend on
it.
