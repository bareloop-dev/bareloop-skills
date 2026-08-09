# tools/

Code that ships alongside the skills. The skills themselves are markdown and
run nothing; this directory is the exception, and each file says which video it
belongs to.

## `weekly_report.py`

The weekly competitor report from *I replaced my weekly report with 150 lines
of Python*.

Python 3, standard library only. No packages, no API keys.

```bash
python weekly_report.py snapshot.csv
python weekly_report.py snapshot.csv --prev last-week.csv
```

Reads one CSV snapshot and writes a markdown decision digest to stdout.
`example-output.md` is a real run over 70 channels.

**This is the working copy.** The three bugs the video is about are still
documented in the comments where they happened, because the comments are the
part worth reading:

1. A number parser that stripped `.` as a thousands separator on a file using
   `.` as the decimal point — turning a pace of `19.0` into `190` and putting 45
   of 70 channels in the wrong bucket. Correctly formatted, completely wrong.
2. A verdict line that read "the slower group grows 0.5x faster". The ratio and
   the adjective disagreed, and the adjective is what a reader keeps.
3. A row object printed where a channel name belonged. Loud, harmless, fixed in
   a minute — the opposite of the first two in every way that matters.

### Rule zero

The script never fills a gap it cannot measure.

Rows with no data are excluded **and counted** in a "not measured" line, never
imputed as zero. Change metrics — deltas, new entrants, trend — require a second
snapshot, so with one file the section prints `REFUSED` and the reason rather
than inferring a trend from a single observation.

### What you have to change

`REQUIRED` lists the column names, which are the ones in this channel's own
export. Point them at your columns. The thresholds — `ACTIVE_DAYS = 7`,
`DORMANT_DAYS = 90` — are editorial decisions, not defaults; set them to what
your team would actually act on.
