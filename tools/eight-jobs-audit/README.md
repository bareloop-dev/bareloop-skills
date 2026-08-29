# Eight jobs, every number audited

The working copies from the video *"I gave Claude 8 marketing jobs and audited
every number"*. Not a cleaned-up rewrite — these are the files that produced the
figures spoken in the video, including the eight reports exactly as they came
back, with their errors intact.

```bash
python ground_truth.py   # the aggregates, computed straight from the CSV
python audit.py          # reads reports/*.md back, checks every claim
```

Python 3, standard library only. No packages, no API keys, no network.

## What is here

| Path | What |
|---|---|
| `PROMPTS.md` | The eight prompts, and why the measurement is what it is |
| `reports/01..08` | The eight outputs, **unedited** |
| `ground_truth.py` | Every aggregate, computed from the CSV. The only source of truth |
| `audit.py` | The 82 claims, each with a check that runs against ground truth |
| `canales-ia-automatizacion-benchmark.csv` | The input: 70 channels |

## What it reports

```
82 claims across 8 jobs

job   claims   ok  wrong  unsup
-------------------------------
01        15   15      0      0
02        10    3      3      4
03         9    8      0      1
04         7    4      2      1
05         8    2      2      4
06         9    7      1      1
07        12    2      0     10
08        12    8      2      2
-------------------------------
all       82   49     10     23
```

Three verdicts, and the middle one is the only accusation:

- **REPRODUCES** — the file produces this number.
- **WRONG** — the file produces a different one.
- **UNSUPPORTED** — the file cannot produce it at all, either way. A
  recommendation is unsupported by construction and that is fine. The point of
  separating it is that in the reports, unsupported claims are written in the
  same voice, with the same decimal places, as the checked ones.

The finding is not the 60%. It is the split: the two jobs that asked only for
arithmetic produced 24 claims and zero wrong; the five that asked for a
judgement produced 49 claims, 19 reproduce, and every contradicted claim is in
that group.

## The honest limit

`audit.py` registers the 82 claims **by hand** — a person decided which
sentences count as claims and what each asserts. The verdicts are not
hand-written: every one comes from running a check against `ground_truth.py`,
and a claim passes only when a number computed from the CSV equals it.

So the register is a judgement call and the verdicts are not. A different reader
would draw the claim boundaries differently and get a different denominator.
That is why the split carries the argument rather than the headline percentage
— the split survives a redrawing, the percentage does not.

Second limit, stated because it cuts against the video: the eight reports were
produced knowing an audit was coming, which biases toward care, not away from
it.

## Using it on your own work

Two things to replace:

1. **The CSV.** Any export will do. `ground_truth.py` is the only file that
   knows its column names — change `load()` and nothing else.
2. **The claim register in `audit.py`.** This is the real work and it does not
   transfer. Read your own output, write down each claim, and give each one a
   check that computes the answer from the source. If you cannot write the
   check, that is itself the finding: the claim is unsupported.

Budget roughly an hour per report the first time. It drops sharply after that,
because most checks are variations on three or four shapes.

**What it will not do.** It does not detect a wrong claim you did not register,
it does not read prose for meaning, and it does not test whether a better prompt
would have avoided the errors. That was not measured and nothing here claims it.

## Licence

MIT, same as the rest of this repository.
