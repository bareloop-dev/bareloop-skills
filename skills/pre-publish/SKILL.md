---
name: pre-publish
description: Last pass before anything ships. Use on a finished draft — video script, description, post or page — to catch unsourced claims, naming drift, broken links and missing AI disclosure. Returns a list; does not edit.
---

# Pre-publish pass

The last thing that runs before something is published. Load `bareloop-voice`
for the naming and banned-word lists.

## This skill does not edit

It returns findings. It never rewrites the draft, never returns a corrected
version, and never fixes something quietly.

A pass that silently edits is a pass you stop reading, and then you are
publishing whatever it decided. The list is the product.

## Checks

**1 · Claims without proof**
Every sentence asserting a fact, number or outcome. For each: is the supporting
artifact present in the draft or named in it? Flag any claim that would require
the reader to take it on trust.
Flag separately any claim about the author's own history — "for months",
"since last year", "I used to" — against whether that history exists. Fabricated
tenure is the failure this project is most exposed to.

**2 · Naming and spelling**
Product and tool names against their makers' spelling. Internal names against
`bareloop-voice`. Drift within a single draft (`Claude Skills` in one paragraph,
`claude skills` in the next) is a finding even when both are defensible.

**3 · Banned words**
Against the list in `bareloop-voice`. Quote the sentence, do not just name the
word.

**4 · Links**
Every URL: correct shape, no tracking parameters that were not deliberate, no
placeholder domains, no links to localhost or file paths. Note that reachability
cannot be verified from here — say so rather than implying it was checked.

**5 · AI disclosure**
If the piece contains synthesized narration or generated visuals: is the
platform's native label set? For YouTube that is the altered-content checkbox,
which is separate from any disclosure paragraph in the description. Both, not
either.

**6 · Thumbnail and title together**
Do they contradict? Does the thumbnail repeat the title word for word, wasting
the second surface? Is the bottom-right corner clear for the duration stamp?

**7 · Numbers**
Every figure: is its unit stated, its source named, and is it consistent with
every other figure in the draft?

## Output

```
BLOCKING     — factually wrong, unsourced, or a policy problem. Ship nothing.
FIX          — should be corrected, not dangerous.
NOTE         — judgement call, author decides.
```

Each finding: the location, the quoted text, and what is wrong. No suggested
rewrite — that is the author's job and the reason this skill stays read-only.

End with the count per severity and nothing else. No summary paragraph, no
encouragement, no "overall this looks strong".

If nothing is found, say `No findings.` Do not manufacture a NOTE to look
useful.
