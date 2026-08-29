# Where the tokens actually went

Reads Claude Code's own session logs and reports where your tokens went. From
the video *"Claude Code token usage: I read 11,947 of my own requests"*.

```bash
python scan.py            # summary
python scan.py --json     # machine-readable
```

Python 3, standard library only. `tiktoken` is optional and is used for exactly
one number (see below). **Read-only** — it never writes to the log directory.

## Why the logs and not an estimate

Claude Code writes one JSONL per session under `~/.claude/projects/<slug>/`, and
every assistant message carries the API's own `usage` block:

```json
{"input_tokens": 2, "cache_creation_input_tokens": 25923,
 "cache_read_input_tokens": 26060, "output_tokens": 1743}
```

That is billing data. Most writing on this subject estimates token counts; this
just adds up the counts already on your disk.

The four classes bill at different rates — uncached input **1×**, cache write
**2×**, cache read **0.1×** — so "tokens sent" and "tokens billed" are very
different quantities, and conflating them is the single most common error in
the category.

## What it found on one machine

64 sessions, 11,947 requests, 10 projects, three weeks. Full output in
`scan-frozen.txt`, aggregates in `headline.json`.

| | |
|---|---|
| Input tokens sent | 2,503,863,919 |
| Billed input units | 388,507,793 |
| Caching's effect | **6.44× fewer billed than sent** |
| Tokens the human typed | 252,731 — **1 in 9,907** |
| Startup context, median | **57,362** (p25 52,504 · p75 60,272) |
| Cache write | 2.9 % of sent, **37.4 % of billed** |
| Cache read | 97.1 % of sent, 62.6 % of billed |

### The finding that reverses the usual advice

Median billed input **per request**, by session length:

| Requests | Sessions | Billed per request |
|---|---|---|
| 1–10 | 9 | **41,511** |
| 11–50 | 17 | 18,520 |
| 51–200 | 21 | **15,982** |
| 200+ | 17 | 30,563 |

Share of a session's whole bill spent on its *first* request:

```
sessions of <=10 requests   43.3 %   (median)
sessions of >=51 requests    1.49 %  (median)
sessions of exactly 2        50.0 %  (all three, to one decimal)
```

The startup context is a **fixed cost, paid once per session, at the 2× cache
write rate.** Amortised over 100 requests it is noise; over two it is half the
bill. So starting a fresh session to save context is the expensive direction.
The curve turns back up past ~200 requests, so there is a middle, not a rule.

## Privacy

The script reads your logs locally and prints aggregates. **This repository
contains no logs** — only the script and the aggregate numbers above.

`--json` output *does* include your project directory names, which are local
paths. `.gitignore` excludes `scan.json` and `scan-frozen.json` for that reason.
Check before you share any output.

## The one number that is not the API's

Everything above comes from the API's own counts except **tokens the human
typed**, because the log stores that as text rather than as a count. It is
measured with `tiktoken`'s `cl100k_base`, which is not Anthropic's tokenizer.

It does not matter much: if that number were wrong by half, "1 token in 9,907"
would become "1 in ~6,600" and nothing in the argument moves.

`user_text()` is the most consequential function here — 12 lines deciding what
counts as "typed". Tool results and injected `<system-reminder>` blocks also
arrive in user-role messages, and counting those would inflate the figure
enormously. It excludes them. Read it first if you distrust the 0.0101 %.

## Limits

One user, one machine, three weeks, 74 % of requests on Opus. The **shape**
should transfer — a fixed per-session cost at 2×, amortised by length. The
57,362 will not.

No fix was applied and re-measured. This tells you where the tokens went; it
does not test remedies, and it does not claim any specific change would help.

The log directory is written to while it is read: two runs ten minutes apart
gave 11,935 and 11,947 requests. Freeze a snapshot before quoting a number.

## Licence

MIT, same as the rest of this repository.
