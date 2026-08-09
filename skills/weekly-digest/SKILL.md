---
name: weekly-digest
description: Turn pasted source material about competitors, tool releases and category news into a weekly decision digest. Use for the Radar pillar. Requires source material to be supplied.
---

# Weekly digest

Produces the Radar digest: what changed, who it affects, whether we act.

## Rule zero — read this before anything else

**If no source material is provided in the conversation, stop.** Return exactly:

```
BLOCKED — no source material.
This skill summarizes text you paste in. It cannot retrieve anything.
Paste the changelogs, posts or release notes and run it again.
```

Do not proceed. Do not answer from general knowledge. Do not produce a
plausible digest and caveat it.

This rule exists because of what a skill is. A skill is a set of instructions
loaded into a conversation. It has no retrieval, no browsing and no access to
anything published after the model's training data. Asked to summarize a week
it cannot see, a language model will produce a confident, well-formatted,
entirely invented digest — because that is the shape of the answer the
instructions asked for, and nothing in the request told it to refuse.

The failure is silent. An invented digest looks exactly like a real one.

If retrieval is genuinely needed, this skill is the wrong tool: pair the model
with a fetch tool or a connector and pass the results in as source material.

## Output

One table, then one paragraph.

| What changed | Source | Who it affects | Act? |
|---|---|---|---|

- **What changed** — one sentence, factual, no adjectives.
- **Source** — the specific artifact it came from. If a row cannot be traced to
  supplied material, the row does not exist.
- **Who it affects** — a named team or role, or `nobody here`. `nobody here` is
  a valid and common answer.
- **Act?** — `no` / `watch` / `this week`. Never blank.

Then: **one paragraph on the single most consequential item**, and why. If
nothing was consequential, say that in one line. A digest padded to look busy
trains people to stop reading it.

## Rules

1. Rows only from supplied material. No inference, no filling gaps, no
   "presumably also shipped".
2. Ordered by the `Act?` column, `this week` first.
3. Unclear source material stays unclear: write `unclear from source` rather
   than resolving it.
4. Vendor language does not survive. "Reimagined workflow experience" becomes
   what actually changed, or `unclear from source`.
5. Cap at 12 rows. More than that means the input was unfiltered.
