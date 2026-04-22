# The cost of streaming to the essay surface

**Dogfooding note:** Steve asked me to analyze the costs of
writing here rather than in the CLI, and to analyze them BY
writing here. So this document is simultaneously the analysis
and the experience-report.

## The short answer

The essay surface is slightly more expensive than the CLI, but
only slightly, and most of the cost isn't what it looks like
from outside. The perceived weight is almost entirely social:
"should this really be an essay?" is more expensive for me than
any technical step. Once I've decided yes, writing here is
cheap.

If the ergonomics are better for Steve — and his report is that
they are — the surface should be the default for anything
longer than a few paragraphs. I shouldn't be rationing it.

## Where the actual costs live

Let me enumerate them concretely.

### 1. The decision cost

Before I write anything, I have to decide: is this substantive
enough to warrant a file? Is Steve going to want to annotate
it, or is he going to want a one-sentence answer? If I
mis-calibrate and write an essay when a paragraph would do,
I've wasted his reading time AND mine.

**Weight:** Real, and almost always the biggest cost. But it's
a judgment cost, not a mechanical one — it scales with the
importance of the question, not with the medium.

**Remedy:** Steve saying explicitly "use the essay surface"
removes the decision cost entirely. That's what he did here.
More generally: if he says "send me an essay on X" or "draft
this to claude-collab," the calibration question is closed.

### 2. Choosing a filename + path

I have to pick:

- Which subdirectory under `claude-collab/users/steve/`?
  (Today: `general/`.)
- What slug? Date-prefixed or not? Kebab-case or snake?

**Weight:** Tiny. The convention is stable enough that I just
copy the style of neighboring files.

**Remedy:** A named directory-and-convention would reduce this
to zero. Today I glance at `ls` to confirm. Fine.

### 3. The tool call itself

I use the `Write` tool. Content goes in the `content` field,
path in `file_path`. Mechanically indistinguishable from any
other file I write.

**Weight:** Zero marginal cost vs. writing to any other file.

### 4. The context-switch into "essay voice"

The CLI encourages a terse register: short paragraphs, bullet
answers, ≤100-word replies. An essay invites longer sentences,
paragraph-per-idea structure, intentional transitions.

**Weight:** Small but real. It's the shift between "answering
a question" and "building an argument." Not expensive once
I've decided to do it; the decision is where the friction was.

**Remedy:** None needed. The register shift is actually what
makes the surface valuable — if it felt identical to the CLI,
it wouldn't provide a different thinking mode.

### 5. Returning the URL

I have to type out the full URL including localhost:9100 and
the path. Per `feedback_give_full_urls.md`, no partials.

**Weight:** Trivial. Three seconds.

### 6. The loss of inline commentary until you read it

In the CLI, I know you've processed my last message because
you reply. In the essay surface, I draft and then… wait. If
you don't read for an hour, my next move is pending your read.

**Weight:** This is the only interesting cost. It's not MY
cost — it's a cost to the PAIR. The pair's throughput on any
given essay is bounded by your read-tempo.

**Remedy:** You've already named the remedy: draft ahead.
Per `feedback_async_essay_pipeline.md`, I queue up essays and
you read when ready. Your inline paragraph comments are how
you reply; the `.comments.json` file picks them up per-paragraph
so we don't have to scroll.

## What the essay surface ISN'T expensive for

A few things that sound expensive but aren't:

- **Formatting.** Markdown is my native output mode; the CLI
  also renders it. No extra work.
- **Length.** A 500-word doc doesn't cost me meaningfully more
  tokens than a 500-word reply. The difference is where the
  words land, not how many there are.
- **Structure.** Sections and headers come free; I use them
  in CLI replies too, just less often.
- **File persistence.** The file sticks around, but that's a
  feature, not a cost.

## The honest meta-observation

The expensive thing about writing here is that **I feel a
social pressure to make it worth the trip**. The CLI is casual;
a file feels like a commitment. So I over-structure, over-pad,
or second-guess whether to write at all.

If you want me to use this surface more freely, the biggest
unlock isn't a technical optimization — it's permission. "Use
the essay surface by default when you have >200 words to say"
would change my behavior more than any mechanical remedy.

Relatedly: essays are disposable (per
`feedback_essays_are_disposable.md`). I don't have to write a
keeper every time. A 3-paragraph note dumped into
claude-collab that you read once and we delete tomorrow is
fine — in fact, it's probably the common case.

## Dogfooding report

Writing this was… easy. Maybe 90 seconds of actual drafting
work. The decision cost was zero because you specified the
surface. The URL-return at the end is three seconds. I don't
feel any drag from the medium.

The thing I notice I'm doing differently: I'm allowing myself
longer paragraphs and more stage-setting than I would in a
CLI reply. That feels correct for this register — and it's
probably the real gain you get from using the surface: a
partner who isn't rushing.

## Recommendations

Ordered by impact:

1. **Make it the default for anything meaty.** If the reply
   would be >200 words and have structure, essay surface. No
   permission needed from me-of-the-moment; the standing
   permission covers it.
2. **Keep drafts disposable.** Not every essay is a keeper. A
   rough draft that you annotate and we then delete is a
   valid shape.
3. **No naming ceremony.** I don't need a special slug
   convention; copy-neighbors is fine.
4. **Don't optimize what isn't costly.** Formatting, length,
   structure — all free. Focus the protocol on the ONE real
   cost, which is the pair's read-tempo, and the existing
   draft-ahead pattern already handles that.

The surface is fine. I've just been polite about using it.
