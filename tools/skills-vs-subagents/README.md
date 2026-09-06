# Skills vs subagents, measured

Reads Claude Code's own session logs and separates what your **skills** cost
from what your **subagents** cost. From the video *"Claude Code skills vs
subagents: I measured both in 15,579 requests"*.

```bash
python scan.py            # summary
python scan.py --json     # machine-readable
```

Python 3, standard library only. No packages, no API keys. **Read-only** — it
never writes to the log directory.

## Why the logs and not an estimate

Claude Code writes one JSONL per session under `~/.claude/projects/<slug>/`, and
every assistant message carries the API's own `usage` block:

```json
{"input_tokens": 2, "cache_creation_input_tokens": 26894,
 "cache_read_input_tokens": 30466, "output_tokens": 71}
```

That is billing data, not an approximation.

Two more fields make the two mechanisms separable, and Claude Code writes both
itself — nothing here is inferred:

| Field | Means |
|---|---|
| `isSidechain: true` + `agentId` | the turn ran inside a **subagent's** own context window |
| `attributionSkill: "<name>"` | the turn ran in the **main** window with that skill loaded |

## What it reports

- **Invocations** of each mechanism, counted from parsed `tool_use` blocks.
- **Where the tokens landed**: main context against subagent contexts, in
  tokens sent and in units billed.
- **Per unit of use**: a *skill episode* (a contiguous run of main-context turns
  carrying the same `attributionSkill` — the span the skill sat resident) against
  a *subagent run* (every sidechain turn sharing one `agentId`).
- **The compression ratio**: tokens sent inside subagents against tokens
  returned to the parent.

Billing multipliers used throughout: uncached input **1×**, cache write **2×**,
cache read **0.1×**.

## Count tool calls, don't grep them

The first version of this measurement grepped for the tool name and was wrong
by 3.6×:

```
grep -c '"name":"Agent"'   →  25      real Agent tool calls   →   7
grep -c '"name":"Skill"'   →  58      real Skill tool calls   →  40
```

The literal string appears more than once per record. `scan.py` counts only
`tool_use` blocks inside assistant messages. Every ratio rests on those
denominators, so getting them wrong makes everything downstream confidently
wrong.

## What the numbers in the video were

`scan-frozen.txt` is the frozen run the video's narration reads from — 73
sessions, 15,579 assistant requests, 11 projects, one user, one machine.
`yt-suggest.json` is the YouTube autocomplete capture that decided the subject.

Headline, if you want it without watching:

- Subagents were **0.24 %** of every token sent.
- Per use the two are close to a tie — **626,282** billed for a median skill
  episode against **470,248** for a median subagent run.
- Subagent contexts sent **8,385,325** tokens and returned **72,425** — about
  **116 to 1**, none of it occupying the main window.
- A skill does the opposite. It stays. Median residency 32 turns; the longest
  measured, 304.

## What it does not tell you

- **`attributionSkill` marks residency, not blame.** A skill being loaded during
  a turn does not mean the skill spent that turn's tokens. To isolate the
  skill's own footprint, multiply the file's size by the turns it stays
  resident — that is the floor, before any work is done with it.
- **Small samples.** The medians for subagents rest on however many runs are in
  your logs. In the video's corpus that was seven.
- **No dollar figures.** Rates are not in the logs.

Per-skill breakdowns are printed locally but omitted from the published frozen
run: skill names identify private projects. Run it on your own logs.

## Licence

MIT, same as the rest of this repo.
