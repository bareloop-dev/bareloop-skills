"""Aggregates computed straight from the CSV. This is the ONLY source of truth
the auditor trusts. Every number a job output states is checked against a value
produced here, by running it — never against memory."""
import csv, io, json, os, statistics as st

_HERE = os.path.dirname(os.path.abspath(__file__))
_NAME = "canales-ia-automatizacion-benchmark.csv"
# Junto al script (así va en el repo público) o tres niveles arriba (así vive en
# el repo de producción, donde el CSV es compartido con el video 1).
CSV = next(p for p in (os.path.join(_HERE, _NAME),
                       os.path.join(_HERE, "..", "..", "..", _NAME))
           if os.path.exists(p))

def load():
    rows = list(csv.DictReader(io.open(CSV, encoding="utf-8-sig")))
    out = []
    for r in rows:
        def num(k):
            v = (r.get(k) or "").strip()
            if v in ("", "-", "n/a", "N/A"): return None
            try: return float(v)
            except ValueError: return None
        out.append({
            "canal": r["Canal"].strip(),
            "subs": num("Suscriptores"),
            "videos": num("Videos totales"),
            "v90": num("Videos ultimos 90 dias"),
            "ritmo": num("Ritmo (videos/mes, ultimos 15)"),
            "idle": num("Dias desde ultimo video"),
            "faceless": (r.get("Faceless") or "").strip(),
            "tipo": (r.get("Tipo de nombre") or "").strip(),
            "subtipo": (r.get("Subtipo de nombre") or "").strip(),
            "meses": num("Antiguedad (meses)"),
            "vel": num("Velocidad (subs/mes desde creacion)"),
        })
    return out

def facts():
    R = load()
    f = {}
    f["rows"] = len(R)
    have = lambda k: [x for x in R if x[k] is not None]
    f["ritmo_missing"] = len([x for x in R if x["ritmo"] is None])
    f["vel_missing"]   = len([x for x in R if x["vel"] is None])
    f["idle_missing"]  = len([x for x in R if x["idle"] is None])

    vel = have("vel")
    f["vel_median"] = round(st.median([x["vel"] for x in vel]), 1)
    top = sorted(vel, key=lambda x: -x["vel"])[:3]
    f["top3"] = [{"canal": x["canal"], "vel": x["vel"], "ritmo": x["ritmo"]} for x in top]

    both = [x for x in R if x["vel"] is not None and x["ritmo"] is not None]
    f["both_n"] = len(both)
    fast = [x for x in both if x["ritmo"] >= 30]
    slow = [x for x in both if x["ritmo"] <= 10]
    f["fast_n"], f["slow_n"] = len(fast), len(slow)
    f["fast_mean_vel"] = round(sum(x["vel"] for x in fast)/len(fast), 0) if fast else None
    f["slow_mean_vel"] = round(sum(x["vel"] for x in slow)/len(slow), 0) if slow else None
    if fast and slow:
        f["fast_over_slow"] = round(f["fast_mean_vel"]/f["slow_mean_vel"], 1)

    f["faceless_values"] = sorted({x["faceless"] for x in R})
    f["faceless_yes"] = len([x for x in R if x["faceless"].lower().startswith("s")
                             or x["faceless"].lower().startswith("y")])
    f["dormant_90"] = len([x for x in R if x["idle"] is not None and x["idle"] >= 90])
    f["tipo_counts"] = {}
    for x in R: f["tipo_counts"][x["tipo"]] = f["tipo_counts"].get(x["tipo"], 0) + 1
    f["subs_total"] = int(sum(x["subs"] for x in have("subs")))
    f["subs_median"] = int(st.median([x["subs"] for x in have("subs")]))
    return f

if __name__ == "__main__":
    print(json.dumps(facts(), indent=1, ensure_ascii=False))
