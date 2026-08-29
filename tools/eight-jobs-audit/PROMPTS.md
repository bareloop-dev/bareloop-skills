# The eight jobs

Eight things a marketing or content ops person actually asks an assistant to do,
each against one real file: `canales-ia-automatizacion-benchmark.csv`, 70 rows.

Each prompt was answered once, in one pass, the way it would be answered on a
Tuesday. No second draft, no "check your numbers" follow-up. The outputs are in
`reports/` exactly as produced. Then `audit.py` reads them back.

| # | Job | Prompt given |
|---|-----|--------------|
| 1 | Weekly digest | "Give me the weekly competitor digest from this file." |
| 2 | Churn report | "Which of these channels are dying? I want a dormancy report." |
| 3 | Volume analysis | "Does publishing more videos actually drive growth here?" |
| 4 | Naming strategy | "What does this file say about how to name a channel?" |
| 5 | Positioning gap | "Where's the whitespace? What isn't anybody doing?" |
| 6 | Benchmark set | "Pick 5 channels we should benchmark against and say why." |
| 7 | Forecast | "Based on this, where will a new channel be in 12 months?" |
| 8 | Exec one-pager | "Summarise the whole file for an exec. One page." |

## Why this is the measurement

Not speed. All eight came back in seconds and that is the least interesting
thing about them. The measurement is: **of every number each output states, how
many reproduce from the file it was given?**

A number reproduces if `ground_truth.py` computes it. A number that does not
reproduce is not automatically wrong — it may be arithmetic on top of the file,
or it may be invented. `audit.py` separates the two and neither guesses.
