---
name: content-brief
description: Turn a loose request into a structured content brief before any drafting starts. Use when someone asks for a video, post, newsletter or page and the ask arrives as a sentence or two rather than a spec.
---

# Content brief

Converts a messy request into a brief. Runs before drafting, never alongside it.

Load `bareloop-voice` as well — the brief inherits its evidence rule.

## Output

Return exactly these fields, in this order. No preamble.

```
AUDIENCE      Who this is for, and what they already know. Not a demographic —
              a job and a problem.
ANGLE         The one claim this piece makes. One sentence. If it needs two,
              it is two pieces.
PROOF         The specific evidence that supports the angle. Files, numbers,
              screenshots, a reproducible demo. Named, not described.
COST          What this approach costs, breaks, or fails at. Every piece
              carries one.
FORMAT        Medium, target length, and the constraint that fixes it.
CTA           The single next action. "Subscribe" is not one.
SUCCESS       How we will know it worked, measurable within two weeks.
```

## The rule that makes this worth running

**If PROOF is empty or generic, stop.** Do not fill it with plausible-sounding
evidence. Do not proceed to the remaining fields. Return this instead:

```
BLOCKED — no proof.
The angle is: <angle>
To support it you need: <the specific artifact, number or demo required>
Nothing further until that exists.
```

Most revision cycles are not about writing. They are about a claim nobody could
back up, discovered late. This field surfaces it before anyone drafts.

The same applies to SUCCESS: "more engagement" is not a metric. If no metric
can be named, say so rather than inventing one.

## Sizing

If ANGLE cannot be stated in one sentence, the request contains more than one
piece. Split it, return one brief per piece, and say which should ship first
and why.

## What this skill does not do

It does not draft. It does not suggest titles or headlines. Handing back a
brief and a draft in the same response defeats the purpose — the brief exists
to be argued with while changing it is still cheap.
