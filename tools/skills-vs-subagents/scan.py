#!/usr/bin/env python3
"""
Skills vs subagents, measured from Claude Code's own session logs.

Claude Code writes one JSONL per session under ~/.claude/projects/<slug>/.
Every assistant message carries the API's own `usage` block, so these are
billing counts, not estimates.

Read-only. This script never writes to the log directory.

    python logs/scan.py            # the summary
    python logs/scan.py --json     # machine-readable
"""
import json, glob, os, sys, collections

# Billing multipliers. Uncached input 1x, cache write 2x, cache read 0.1x.
W_IN, W_WRITE, W_READ = 1.0, 2.0, 0.1

LOGS = os.path.expanduser("~/.claude/projects")


def usage_of(rec):
    u = rec.get("message", {}).get("usage") or {}
    return (
        u.get("input_tokens", 0) or 0,
        u.get("cache_creation_input_tokens", 0) or 0,
        u.get("cache_read_input_tokens", 0) or 0,
        u.get("output_tokens", 0) or 0,
    )


def billed(i, w, r):
    return i * W_IN + w * W_WRITE + r * W_READ


class Acc:
    __slots__ = ("turns", "i", "w", "r", "o")

    def __init__(self):
        self.turns = self.i = self.w = self.r = self.o = 0

    def add(self, i, w, r, o):
        self.turns += 1
        self.i += i; self.w += w; self.r += r; self.o += o

    @property
    def sent(self):
        return self.i + self.w + self.r

    @property
    def billed(self):
        return billed(self.i, self.w, self.r)

    def d(self):
        return {"turns": self.turns, "input": self.i, "cache_write": self.w,
                "cache_read": self.r, "output": self.o,
                "sent": self.sent, "billed": round(self.billed, 1)}


def episodes_and_runs(sessions_recs):
    """Skill residency episodes and subagent runs, walked in session order.

    A skill "episode" is a contiguous run of main-context turns carrying the
    same attributionSkill: the span the skill was resident and being re-read.
    A subagent "run" is all sidechain turns sharing one agentId.
    """
    import statistics as st
    eps, runs = [], collections.defaultdict(lambda: [0, 0.0, 0])
    main_turn, side_turn = [], []
    for recs in sessions_recs.values():
        name, turns, bill = None, 0, 0.0
        for d in recs:
            i, w, r, o = usage_of(d)
            b = billed(i, w, r)
            if d.get("isSidechain"):
                side_turn.append(b)
                a = runs[d.get("agentId")]
                a[0] += 1; a[1] += b; a[2] += o
                continue
            main_turn.append(b)
            sk = d.get("attributionSkill")
            if sk:
                if sk != name:
                    if name:
                        eps.append((name, turns, bill))
                    name, turns, bill = sk, 0, 0.0
                turns += 1; bill += b
            elif name:
                eps.append((name, turns, bill)); name = None
        if name:
            eps.append((name, turns, bill))
    return eps, runs, main_turn, side_turn


def scan():
    files = sorted(glob.glob(os.path.join(LOGS, "**", "*.jsonl"), recursive=True))
    if not files:
        sys.exit(f"no session logs under {LOGS}")

    main, side = Acc(), Acc()
    sessions_recs = collections.defaultdict(list)
    per_skill = collections.defaultdict(Acc)
    skill_calls = collections.Counter()      # Skill tool invocations
    agent_calls = collections.Counter()      # Agent tool invocations
    agent_ids = set()
    sessions, projects = set(), set()
    requests = 0
    # per-session: turns after the first Skill call, to measure the re-read tail
    sess_turns = collections.Counter()
    sess_first_skill = {}

    for f in files:
        projects.add(os.path.basename(os.path.dirname(f)))
        for line in open(f, encoding="utf-8", errors="replace"):
            try:
                d = json.loads(line)
            except ValueError:
                continue
            sid = d.get("sessionId")
            if sid:
                sessions.add(sid)

            # tool invocations, from the assistant's tool_use blocks
            if d.get("type") == "assistant":
                content = d.get("message", {}).get("content") or []
                if isinstance(content, list):
                    for b in content:
                        if isinstance(b, dict) and b.get("type") == "tool_use":
                            n = b.get("name")
                            if n == "Skill":
                                skill_calls[(b.get("input") or {}).get("skill", "?")] += 1
                            elif n == "Agent":
                                agent_calls[(b.get("input") or {}).get(
                                    "subagent_type", "general-purpose")] += 1

                requests += 1
                sessions_recs[sid].append(d)
                u = usage_of(d)
                if d.get("isSidechain"):
                    side.add(*u)
                    if d.get("agentId"):
                        agent_ids.add(d["agentId"])
                else:
                    main.add(*u)
                    sess_turns[sid] += 1
                    sk = d.get("attributionSkill")
                    if sk:
                        per_skill[sk].add(*u)
                        if sid not in sess_first_skill:
                            sess_first_skill[sid] = sess_turns[sid]

    eps, runs, main_turn, side_turn = episodes_and_runs(sessions_recs)
    import statistics as st

    def stats(xs):
        return {"n": len(xs), "median": round(st.median(xs), 1),
                "mean": round(st.mean(xs), 1), "max": round(max(xs), 1)} if xs else {}

    ep_turns = [e[1] for e in eps]; ep_bill = [e[2] for e in eps]
    run_turns = [v[0] for v in runs.values()]; run_bill = [v[1] for v in runs.values()]
    by_skill = collections.defaultdict(lambda: [0, 0, 0.0])
    for n, t, b in eps:
        x = by_skill[n]; x[0] += 1; x[1] += t; x[2] += b

    return {
        "corpus": {
            "projects": len(projects),
            "sessions": len(sessions),
            "assistant_requests": requests,
            "log_files": len(files),
        },
        "main_context": main.d(),
        "subagent_context": side.d(),
        "skill_invocations": sum(skill_calls.values()),
        "agent_invocations": sum(agent_calls.values()),
        "distinct_agent_runs": len(agent_ids),
        "skills_by_name": {k: v for k, v in skill_calls.most_common()},
        "agents_by_type": dict(agent_calls),
        "per_skill_turns": {k: v.d() for k, v in
                            sorted(per_skill.items(),
                                   key=lambda kv: -kv[1].turns)},
        "skill_episodes": {
            "count": len(eps),
            "turns_resident": stats(ep_turns),
            "billed_per_episode": stats(ep_bill),
        },
        "subagent_runs": {
            "count": len(runs),
            "turns_per_run": stats(run_turns),
            "billed_per_run": stats(run_bill),
        },
        "per_turn_billed": {
            "main_context": stats(main_turn),
            "subagent_context": stats(side_turn),
        },
        "by_skill_episodes": {
            k: {"episodes": v[0], "turns": v[1], "billed": round(v[2], 1)}
            for k, v in sorted(by_skill.items(), key=lambda kv: -kv[1][2])
        },
    }


def main():
    r = scan()
    if "--json" in sys.argv:
        print(json.dumps(r, indent=2))
        return

    c, m, s = r["corpus"], r["main_context"], r["subagent_context"]
    n_sk, n_ag = r["skill_invocations"], r["agent_invocations"]

    print("CORPUS")
    print(f"  {c['sessions']} sessions, {c['projects']} projects, "
          f"{c['assistant_requests']:,} assistant requests")
    print()
    print("INVOCATIONS")
    print(f"  Skill tool   {n_sk:>6}")
    print(f"  Agent tool   {n_ag:>6}   ({r['distinct_agent_runs']} distinct runs)")
    print()
    print("WHERE THE TOKENS LANDED")
    hdr = f"  {'':<18}{'turns':>8}{'sent':>16}{'billed':>16}{'output':>12}"
    print(hdr)
    print(f"  {'main context':<18}{m['turns']:>8}{m['sent']:>16,}"
          f"{int(m['billed']):>16,}{m['output']:>12,}")
    print(f"  {'subagent context':<18}{s['turns']:>8}{s['sent']:>16,}"
          f"{int(s['billed']):>16,}{s['output']:>12,}")
    tot_sent = m["sent"] + s["sent"]
    print(f"  subagent share of tokens sent: "
          f"{100.0 * s['sent'] / tot_sent:.2f} %")
    print()
    if n_ag:
        print(f"  per subagent invocation: {s['turns']/n_ag:.1f} turns, "
              f"{s['sent']/n_ag:,.0f} sent, {s['billed']/n_ag:,.0f} billed")
    print()
    ep, rn, pt = r["skill_episodes"], r["subagent_runs"], r["per_turn_billed"]
    print("THE COMPARISON, PER UNIT OF USE")
    print(f"  {'':<26}{'skill episode':>16}{'subagent run':>16}")
    print(f"  {'count':<26}{ep['count']:>16}{rn['count']:>16}")
    print(f"  {'turns (median)':<26}{ep['turns_resident']['median']:>16,.0f}"
          f"{rn['turns_per_run']['median']:>16,.0f}")
    print(f"  {'billed (median)':<26}{ep['billed_per_episode']['median']:>16,.0f}"
          f"{rn['billed_per_run']['median']:>16,.0f}")
    print(f"  {'billed/turn (median)':<26}{pt['main_context']['median']:>16,.0f}"
          f"{pt['subagent_context']['median']:>16,.0f}")
    print()

    print("SKILL TURNS BY SKILL  (turns where the skill was loaded in context)")
    for k, v in list(r["per_skill_turns"].items())[:10]:
        print(f"  {k:<34}{v['turns']:>6} turns{v['sent']:>16,} sent"
              f"{int(v['billed']):>14,} billed")


if __name__ == "__main__":
    main()
