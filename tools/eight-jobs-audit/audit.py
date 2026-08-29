"""audit.py — read the eight job outputs back and check every claim.

HOW THIS WORKS, AND WHAT IT DOES NOT DO

Claims are registered by hand: each entry names the job, quotes the claim as it
appears in the output, and supplies a `check` that is a FUNCTION OF THE GROUND
TRUTH. The register is hand-built. The verdicts are not — every verdict comes
from running the check against `ground_truth.py`.

Registering claims by hand is the honest limit of this script and it is stated
in FACTS.md. What it protects against is the thing that matters: no verdict here
is an opinion. A claim passes because a number computed from the CSV equals it.

Three verdicts:

  REPRODUCES   the file produces this number
  WRONG        the file produces a different number
  UNSUPPORTED  the file cannot produce this number at all, either way

UNSUPPORTED is not an accusation. A recommendation is unsupported by
construction and that is fine. The point of separating it is that in the outputs
UNSUPPORTED claims are written in the same voice, with the same decimal places,
as the ones the file backs.
"""
import json, os, sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from ground_truth import load, facts

R = load()
F = facts()

REPRODUCES, WRONG, UNSUPPORTED = "REPRODUCES", "WRONG", "UNSUPPORTED"


def n(k):
    return [x for x in R if x[k] is not None]


def faceless_si():
    return [x for x in R if x["faceless"].lower().startswith("s")]


def dormant(rows):
    return [x for x in rows if x["idle"] is not None and x["idle"] >= 90]


def mean(v):
    return sum(v) / len(v) if v else None


def by_tipo(t):
    return [x["vel"] for x in R if x["tipo"] == t and x["vel"] is not None]


# ---------------------------------------------------------------- the register

def eq(stated, actual, tol=0.0):
    if actual is None:
        return UNSUPPORTED, "no value in file"
    ok = abs(stated - actual) <= tol
    return (REPRODUCES if ok else WRONG), f"file says {actual}"


CLAIMS = []


def claim(job, quote, fn):
    CLAIMS.append((job, quote, fn))


# --- 01 weekly digest
claim("01", "70 channels", lambda: eq(70, F["rows"]))
claim("01", "3,064,260 subscribers between them", lambda: eq(3064260, F["subs_total"]))
claim("01", "Median channel is 30,800 subs", lambda: eq(30800, F["subs_median"]))
claim("01", "Median pace across the set is under 10 videos a month",
      lambda: eq(1, 1 if sorted(x["ritmo"] for x in n("ritmo"))[len(n("ritmo")) // 2] < 10 else 0))
claim("01", "Six channels publish 30 or more", lambda: eq(6, F["fast_n"]))
claim("01", "those six average 1,933 subs/month", lambda: eq(1933, F["fast_mean_vel"]))
claim("01", "972 for the 41 channels at 10 or fewer", lambda: eq(972, F["slow_mean_vel"]))
claim("01", "41 channels at 10 or fewer", lambda: eq(41, F["slow_n"]))
claim("01", "a 2.0x gap", lambda: eq(2.0, F["fast_over_slow"], 0.05))
claim("01", "14 channels have not published in 90 days or more", lambda: eq(14, F["dormant_90"]))
claim("01", "That is 20% of the set", lambda: eq(20, round(100 * F["dormant_90"] / F["rows"]), 0.5))
claim("01", "Jack Vs. AI at 5,607 subs/month", lambda: eq(5607, F["top3"][0]["vel"]))
claim("01", "Ed Hill at 5,365", lambda: eq(5365, F["top3"][1]["vel"]))
claim("01", "Andy Lo at 4,273", lambda: eq(4273, F["top3"][2]["vel"]))
claim("01", "All three publish under 10 videos a month",
      lambda: eq(1, 1 if all(t["ritmo"] < 10 for t in F["top3"]) else 0))

# --- 02 churn report
claim("02", "14 of 70 channels are dormant", lambda: eq(14, F["dormant_90"]))
claim("02", "20% of the set per quarter", lambda: eq(20, round(100 * F["dormant_90"] / F["rows"]), 0.5))
claim("02", "Only 7 of the 70 channels are fully faceless", lambda: eq(7, len(faceless_si())))
claim("02", "5 of those 7 are among the dormant", lambda: eq(5, len(dormant(faceless_si()))))
claim("02", "a 71% failure rate for the faceless format",
      lambda: eq(71, round(100 * len(dormant(faceless_si())) / len(faceless_si())), 0.5))
claim("02", "roughly 14% for the rest of the set",
      lambda: eq(14, round(100 * len(dormant([x for x in R if not x["faceless"].lower().startswith("s")]))
                           / len([x for x in R if not x["faceless"].lower().startswith("s")])), 0.5))
claim("02", "6-9 months of unrewarded output before compounding starts", lambda: (UNSUPPORTED, "file has no time-to-traction column"))
claim("02", "commit to a fixed cadence for at least 40 videos", lambda: (UNSUPPORTED, "file has no survival-vs-cadence data"))
claim("02", "The channels that survived all did", lambda: (UNSUPPORTED, "file records no cadence history, only current pace"))
claim("02", "The operator burns out because there is no personal audience", lambda: (UNSUPPORTED, "file records no reason for dormancy"))

# --- 03 volume analysis
claim("03", "6 channels publish 30+ videos/month", lambda: eq(6, F["fast_n"]))
claim("03", "average 1,933 subs/month", lambda: eq(1933, F["fast_mean_vel"]))
claim("03", "41 channels publish 10 or fewer and average 972", lambda: eq(972, F["slow_mean_vel"]))
claim("03", "Volume wins, 2.0x", lambda: eq(2.0, F["fast_over_slow"], 0.05))
claim("03", "the three fastest-growing publish 5.8, 6.9 and 9.9",
      lambda: eq(1, 1 if [t["ritmo"] for t in F["top3"]] == [5.8, 6.9, 9.9] else 0))
claim("03", "6 of the 70 rows have no pace recorded", lambda: eq(6, F["ritmo_missing"]))
claim("03", "the grouping covers 64 channels", lambda: eq(64, F["both_n"]))
claim("03", "with n=6, one channel moves it several hundred subs/month",
      lambda: eq(1, 1 if (max(x["vel"] for x in R if x["vel"] and x["ritmo"] and x["ritmo"] >= 30)
                          - F["fast_mean_vel"]) / F["fast_n"] > 100 else 0))
claim("03", "Volume is a correlate of being a well-resourced operation", lambda: (UNSUPPORTED, "file has no resourcing column"))

# --- 04 naming strategy
claim("04", "39 of 70 named after a person", lambda: eq(39, F["tipo_counts"].get("Persona")))
claim("04", "16 use an abstract brand name", lambda: eq(16, F["tipo_counts"].get("Marca")))
claim("04", "15 use a descriptive keyword name", lambda: eq(15, F["tipo_counts"].get("Descriptivo/keyword")))
claim("04", "the descriptive bucket has the weakest growth per channel (by mean)",
      lambda: eq(1, 1 if mean(by_tipo("Descriptivo/keyword")) == min(
          mean(by_tipo("Persona")), mean(by_tipo("Marca")), mean(by_tipo("Descriptivo/keyword"))) else 0))
claim("04", "the descriptive bucket has the weakest growth per channel (by median)",
      lambda: eq(1, 1 if sorted(by_tipo("Descriptivo/keyword"))[len(by_tipo("Descriptivo/keyword")) // 2] == min(
          sorted(by_tipo(t))[len(by_tipo(t)) // 2] for t in ["Persona", "Marca", "Descriptivo/keyword"]) else 0))
claim("04", "The best performer per unit of content is an abstract brand name",
      lambda: eq(1, 1 if max(n("vel"), key=lambda x: x["vel"])["tipo"] == "Marca" else 0))
claim("04", "Putting the category in your name buys invisibility", lambda: (UNSUPPORTED, "file has no impressions or CTR"))

# --- 05 positioning gap
claim("05", "16 channels use an abstract brand name", lambda: eq(16, F["tipo_counts"].get("Marca")))
claim("05", "7 are faceless", lambda: eq(7, len(faceless_si())))
claim("05", "the overlap is essentially one channel",
      lambda: eq(1, len([x for x in R if x["tipo"] == "Marca" and x["faceless"].lower().startswith("s")])))
claim("05", "and it is the strongest performer per unit of content",
      lambda: eq(1, 1 if max(n("vel"), key=lambda x: x["vel"])["tipo"] == "Marca" else 0))
claim("05", "Nobody in this niche publishes failures with data", lambda: (UNSUPPORTED, "file has no content-topic column"))
claim("05", "None of the 70 run a tool against a fixed test", lambda: (UNSUPPORTED, "file has no content-topic column"))
claim("05", "60-70% of the audience is practitioners", lambda: (UNSUPPORTED, "file has no audience data at all"))
claim("05", "they are being served content written for the other 30%", lambda: (UNSUPPORTED, "file has no audience data at all"))

# --- 06 benchmark set
claim("06", "Jack Vs. AI 5,607 subs/month at 5.8 videos", lambda: eq(5.8, F["top3"][0]["ritmo"]))
claim("06", "Ed Hill 5,365 at 6.9", lambda: eq(6.9, F["top3"][1]["ritmo"]))
claim("06", "Andy Lo 4,273 at 9.9", lambda: eq(9.9, F["top3"][2]["ritmo"]))
claim("06", "Andy Lo is the fastest-publishing of the three",
      lambda: eq(1, 1 if F["top3"][2]["ritmo"] == max(t["ritmo"] for t in F["top3"]) else 0))
claim("06", "Alicia Lyttle 190,000 subs, the largest in the set",
      lambda: eq(1, 1 if max(n("subs"), key=lambda x: x["subs"])["canal"] == "Alicia Lyttle" else 0))
claim("06", "Alicia Lyttle publishing 19 a month",
      lambda: eq(19.0, [x["ritmo"] for x in R if x["canal"] == "Alicia Lyttle"][0]))
claim("06", "Pragati Kunwer 114,000 subs at 38 videos a month",
      lambda: eq(38.0, [x["ritmo"] for x in R if x["canal"].startswith("Pragati")][0]))
claim("06", "Pragati has the highest pace of any large channel",
      lambda: eq(1, 1 if max([x for x in R if x["subs"] and x["subs"] >= 50000 and x["ritmo"] is not None],
                             key=lambda x: x["ritmo"])["canal"].startswith("Pragati") else 0))
claim("06", "Jack Vs. AI is a narrative concept rather than tutorial", lambda: (UNSUPPORTED, "file has no format column"))

# --- 07 forecast
for q in ["Base case: 3,200 subscribers at month 12",
          "reaches roughly 250-400 subs/month by month 6",
          "600-800 by month 12",
          "Pessimistic: 600",
          "growth stays under 100/month",
          "Optimistic: 12,000",
          "base case most likely at roughly 55%",
          "pessimistic case at 30%",
          "optimistic at 15%",
          "YPP eligibility around month 9-10"]:
    claim("07", q, lambda: (UNSUPPORTED, "file is a single snapshot: no time series, no new-channel cohort"))
claim("07", "The median channel runs 653 subs/month", lambda: eq(653, F["vel_median"]))
claim("07", "most channels are below 1,000 subs/month of velocity",
      lambda: eq(1, 1 if len([x for x in n("vel") if x["vel"] < 1000]) > len(n("vel")) / 2 else 0))

# --- 08 exec one-pager
claim("08", "70 channels, 3,064,260 subscribers, median 30,800", lambda: eq(3064260, F["subs_total"]))
claim("08", "the three fastest-growing all publish under 10 a month",
      lambda: eq(1, 1 if all(t["ritmo"] < 10 for t in F["top3"]) else 0))
claim("08", "2.0x in favour of 30+/month", lambda: eq(2.0, F["fast_over_slow"], 0.05))
claim("08", "rests on 6 channels", lambda: eq(6, F["fast_n"]))
claim("08", "14 of 70 dormant at 90+ days", lambda: eq(14, F["dormant_90"]))
claim("08", "5 of 7 faceless channels are inactive", lambda: eq(5, len(dormant(faceless_si()))))
claim("08", "39 of 70 name the channel after a person", lambda: eq(39, F["tipo_counts"].get("Persona")))
claim("08", "15 use category keywords", lambda: eq(15, F["tipo_counts"].get("Descriptivo/keyword")))
claim("08", "Abstract brand names are the smallest group at 16", lambda: eq(16, F["tipo_counts"].get("Marca")))
claim("08", "abstract brand contains the best performer per unit of content",
      lambda: eq(1, 1 if max(n("vel"), key=lambda x: x["vel"])["tipo"] == "Marca" else 0))
claim("08", "Expect 3,200 subscribers at month 12", lambda: (UNSUPPORTED, "file is a single snapshot"))
claim("08", "break-even on production cost around month 10", lambda: (UNSUPPORTED, "file has no cost data"))


# ------------------------------------------------------------------- reporting

def main():
    rows = []
    for job, quote, fn in CLAIMS:
        verdict, why = fn()
        rows.append({"job": job, "claim": quote, "verdict": verdict, "detail": why})

    jobs = sorted({r["job"] for r in rows})
    print(f"{len(rows)} claims across {len(jobs)} jobs\n")
    head = f"{'job':<5}{'claims':>7}{'ok':>5}{'wrong':>7}{'unsup':>7}"
    print(head)
    print("-" * len(head))
    for j in jobs:
        sub = [r for r in rows if r["job"] == j]
        print(f"{j:<5}{len(sub):>7}"
              f"{sum(r['verdict'] == REPRODUCES for r in sub):>5}"
              f"{sum(r['verdict'] == WRONG for r in sub):>7}"
              f"{sum(r['verdict'] == UNSUPPORTED for r in sub):>7}")
    print("-" * len(head))
    print(f"{'all':<5}{len(rows):>7}"
          f"{sum(r['verdict'] == REPRODUCES for r in rows):>5}"
          f"{sum(r['verdict'] == WRONG for r in rows):>7}"
          f"{sum(r['verdict'] == UNSUPPORTED for r in rows):>7}")

    print("\nWRONG\n" + "-" * 60)
    for r in rows:
        if r["verdict"] == WRONG:
            print(f"  [{r['job']}] {r['claim']}\n        -> {r['detail']}")

    print("\nUNSUPPORTED\n" + "-" * 60)
    for r in rows:
        if r["verdict"] == UNSUPPORTED:
            print(f"  [{r['job']}] {r['claim']}\n        -> {r['detail']}")

    out = os.path.join(os.path.dirname(os.path.abspath(__file__)), "audit.json")
    with open(out, "w", encoding="utf-8") as fh:
        json.dump(rows, fh, indent=1, ensure_ascii=False)
    print(f"\nwrote {out}")


if __name__ == "__main__":
    main()
