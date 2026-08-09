# Bareloop Skills

Five Claude Skills for marketing work: brand voice, content briefs, platform
repurposing, a weekly digest and a pre-publish pass.

333 lines of markdown across 5 files. No code, no dependencies, no cost beyond
the Claude plan you already have.

These are the working copies. They are the files that produce this channel's
scripts and descriptions, not a cleaned-up version made for publishing. So
`bareloop-voice` contains my editorial voice, not a blank template — see
[Making the voice file yours](#making-the-voice-file-yours).

## What a Skill is

A folder with one `SKILL.md` in it. Two fields at the top — a name, and a
description of when to use it — then the instructions below.

The description does the routing. Claude reads it, decides the work matches,
and loads the rest. Nothing compiles. Nothing runs.

A Skill has no retrieval and no browsing. It cannot fetch a page, read your
analytics or check what shipped last week. This matters more than it sounds
like it does, and `weekly-digest` is built around it.

## Install

Skills live in a `.claude/skills/` folder.

```bash
git clone https://github.com/bareloop-dev/bareloop-skills
cp -r bareloop-skills/skills/* your-project/.claude/skills/
```

To use them in every project instead of one, copy to `~/.claude/skills/`.

## The files

| File | What it does | Lines |
|---|---|---|
| `bareloop-voice` | The register, 23 words we do not use, and 7 before/after pairs. The other four load this one first. | 84 |
| `content-brief` | Turns a loose request into 7 fields. Stops if the evidence field is empty rather than inventing evidence. | 58 |
| `platform-repurpose` | One long asset into platform cuts, written to the actual character limits. | 57 |
| `pre-publish` | 7 checks on a finished draft. Returns a list. Never edits. | 72 |
| `weekly-digest` | Pasted source material into one decision table, capped at 12 rows. | 62 |

## They depend on each other

Four of the five load `bareloop-voice` by name. Two of the `pre-publish` checks
— naming drift and banned words — read their lists out of it.

So if you rename that file, update the references in the other four. If you
delete it, those two checks have nothing to compare against and will quietly
do less than you think.

## Making the voice file yours

`bareloop-voice` is the one file you cannot use as-is. It describes how Bareloop
writes. Copying it wholesale means publishing in someone else's register.

1. Rename it, and update the reference line in the other four files.
2. Replace the 23 banned words with the ones your own drafts keep reaching for.
   Read three of your published pieces and write down what you cut. That list is
   more useful than a generic one.
3. Rewrite the 7 before/after pairs. **This is the actual work.** Budget an
   hour, not five minutes.

Point 3 is the whole file, and it is worth saying why. A rule like "be concise"
does not change anything — every model already believes it is being concise. A
rewritten sentence next to the original is checkable. That is why the file says
its own rules are the approximate version and the pairs are the specification.

A voice file with the pairs stripped out is the thing that does not work. If you
only have time for one step, do this one.

## Two things to change for your own setup

- `weekly-digest` refers to "the Radar pillar", which is a Bareloop content
  pillar. Rename it to whatever your recurring format is called, or cut the
  reference.
- `pre-publish` check 1 flags claims about the author's own history, because
  that is the failure this channel is most exposed to. Keep it if you write in
  first person. Cut it if you do not.

## The cost

Every system has one. Here it is:

A Skill is a file, and files go stale. Nothing tells you when. A platform
changes a character limit, a tool renames itself, your own voice shifts, and
the file keeps confidently applying last year's rules. A stale instruction file
is worse than none, because you will trust it.

The character limits in `platform-repurpose` are the fastest-moving part.
Verify them before relying on them.

If a task runs less than about once a month, do not write a Skill for it. The
maintenance costs more than the file saves.

## What these do not do

They do not retrieve anything. `weekly-digest` opens with a rule that stops it
when no source material was pasted in, because a language model asked to
summarize a week it cannot see will return a confident, correctly formatted,
entirely invented digest. That is not a bug in the model. It is the shape of
answer the instructions asked for.

If you need retrieval, a Skill is the wrong tool. Pair the model with a fetch
tool or a connector and pass the results in as source material.

## License

MIT. Use them, change them, ship them commercially. Attribution appreciated,
not required.
