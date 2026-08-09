#!/usr/bin/env python3
"""
weekly_report.py — the weekly competitor report, as a script.

Reads one snapshot CSV and writes a decision digest to stdout.

    python weekly_report.py snapshot.csv
    python weekly_report.py snapshot.csv --prev last-week.csv

RULE ZERO
---------
The script never fills a gap it cannot measure.

Two ways that shows up:

  1. A row whose value is "s/d" (no data) is excluded from the metric AND
     counted in a "not measured" line. It is never treated as zero, and it
     never quietly shrinks the denominator without saying so.

  2. Change — "up from", "down from", "trending" — requires a previous
     snapshot. With one file there is no previous week, so every change
     metric prints REFUSED instead of a number. A report that infers a
     trend from a single observation is not a report.

That is the whole difference between this and the report it replaces. The
formatting was never the hard part.
"""

import argparse
import csv
import sys
from datetime import date

# Columns this script depends on. Missing one is a hard stop, not a warning:
# a report that silently drops a section is worse than no report.
REQUIRED = [
    "Canal", "Handle", "Suscriptores", "Dias desde ultimo video",
    "Ritmo (videos/mes, ultimos 15)", "Faceless", "Tipo de nombre",
    "Antiguedad (meses)", "Velocidad (subs/mes desde creacion)",
]

NO_DATA = {"s/d", "", "n/a", "-"}

ACTIVE_DAYS = 7    # published inside the reporting week
DORMANT_DAYS = 90  # stopped, for our purposes


def num(raw):
    """Parse a numeric cell. Returns None for anything not measured.

    None is not zero. Every caller has to decide what to do with it, which
    is the point — an imputed zero is how a dormant channel becomes a
    channel that published nothing, which are different claims.
    """
    if raw is None:
        return None
    s = raw.strip()
    if s.lower() in NO_DATA:
        return None
    # This file uses "." as the DECIMAL separator and no thousands separator.
    # The first version of this function stripped dots as thousands marks,
    # which turned a pace of 19.0 videos/month into 190 and put 45 of 70
    # channels in the "30+ per month" bucket. The report was well formatted
    # and completely wrong. Only strip separators the source actually uses.
    s = s.replace(",", "")
    try:
        return float(s)
    except ValueError:
        return None


def load(path):
    with open(path, encoding="utf-8-sig", newline="") as fh:
        rows = list(csv.DictReader(fh))
    if not rows:
        sys.exit(f"{path}: empty")
    missing = [c for c in REQUIRED if c not in rows[0]]
    if missing:
        sys.exit(f"{path}: missing required columns: {', '.join(missing)}")
    return rows


def measured(rows, col):
    """Split rows into (parsed values, count of rows with no data)."""
    vals, gaps = [], 0
    for r in rows:
        v = num(r.get(col))
        if v is None:
            gaps += 1
        else:
            vals.append((r, v))
    return vals, gaps


def gap_note(gaps, total):
    if not gaps:
        return ""
    return f"  _not measured: {gaps} of {total}_"


def section(title):
    return f"\n## {title}\n"


def report(rows, prev=None):
    out = []
    total = len(rows)
    w = out.append

    w(f"# Weekly report — {date.today().isoformat()}")
    w(f"\n{total} channels in the snapshot.")

    # ---- Activity ---------------------------------------------------------
    days, gaps = measured(rows, "Dias desde ultimo video")
    active = [r for r, v in days if v <= ACTIVE_DAYS]
    dormant = [r for r, v in days if v > DORMANT_DAYS]

    w(section("Published this week"))
    w(f"{len(active)} of {len(days)} measured channels published "
      f"in the last {ACTIVE_DAYS} days.")
    w(gap_note(gaps, total))

    w(section("Gone quiet"))
    w(f"{len(dormant)} channels have not published in {DORMANT_DAYS}+ days.")
    for r, v in sorted(((r, v) for r, v in days if v > DORMANT_DAYS),
                       key=lambda x: -x[1])[:5]:
        w(f"- {r['Canal']} — {int(v)} days")

    # ---- Pace vs growth ---------------------------------------------------
    w(section("Pace against growth"))
    pace, pace_gaps = measured(rows, "Ritmo (videos/mes, ultimos 15)")
    vel = {r["Handle"]: v for r, v in measured(rows, "Velocidad (subs/mes desde creacion)")[0]}
    paired = [(r, p, vel[r["Handle"]]) for r, p in pace if r["Handle"] in vel]

    if paired:
        fast = [t for t in paired if t[1] >= 30]
        slow = [t for t in paired if t[1] <= 10]

        def avg(g):
            return sum(t[2] for t in g) / len(g) if g else None

        af, as_ = avg(fast), avg(slow)
        w(f"30+ videos/month: {len(fast)} channels, {af:,.0f} subs/month average."
          if af else "30+ videos/month: none measured.")
        w(f"10 or fewer videos/month: {len(slow)} channels, {as_:,.0f} subs/month average."
          if as_ else "10 or fewer videos/month: none measured.")

        # Print the direction, never the adjective. An earlier version wrote
        # "the slower group grows 0.5x faster" — the ratio and the word
        # disagreed, and the word is what a reader remembers.
        if af and as_:
            hi, lo, who = (as_, af, "slower") if as_ > af else (af, as_, "faster")
            w(f"\n**On the average, the {who} group grows {hi / lo:.1f}x more.**")

        # The average and the ranking disagree here, so print both. Reporting
        # only one is the editorial decision the hand-written report used to
        # make silently, in favour of whatever the writer already believed.
        top = sorted(paired, key=lambda t: -t[2])[:3]
        w("\nTop 3 by subs/month, with their pace:")
        for r, pc, v in top:
            w(f"- {r['Canal']} — {pc:g} videos/month, {v:,.0f} subs/month")
        w("\n_The group average and this ranking point opposite ways. "
          "Both are in the file._")
    w(gap_note(pace_gaps, total))

    # ---- Faceless ---------------------------------------------------------
    w(section("Faceless"))
    fl = [r for r in rows if r["Faceless"].strip() == "Si"]
    fl_days = [(r, num(r["Dias desde ultimo video"])) for r in fl]
    fl_dead = [r for r, v in fl_days if v is not None and v > DORMANT_DAYS]
    w(f"{len(fl)} of {total} channels are fully faceless. "
      f"{len(fl_dead)} of those {len(fl)} are dormant.")

    # ---- Change -----------------------------------------------------------
    w(section("Change since last week"))
    if prev is None:
        w("REFUSED — no previous snapshot supplied.")
        w("\nSubscriber deltas and new entrants need a prior file.")
        w("There is no way to derive them from one observation.")
        w("\nRe-run with `--prev last-week.csv`.")
    else:
        before = {r["Handle"]: num(r["Suscriptores"]) for r in prev}
        moved, unmeasurable = [], 0
        for r in rows:
            now, then = num(r["Suscriptores"]), before.get(r["Handle"])
            if now is None or then is None:
                unmeasurable += 1
                continue
            if now != then:
                moved.append((r, now - then))
        for r, d in sorted(moved, key=lambda x: -abs(x[1]))[:10]:
            w(f"- {r['Canal']}: {d:+,.0f}")
        new = [r for r in rows if r["Handle"] not in before]
        w(f"\n{len(new)} new entrants. {unmeasurable} channels not comparable.")

    return "\n".join(out) + "\n"


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("snapshot")
    ap.add_argument("--prev", help="previous week's snapshot, for change metrics")
    a = ap.parse_args()
    prev = load(a.prev) if a.prev else None
    sys.stdout.write(report(load(a.snapshot), prev))


if __name__ == "__main__":
    main()
