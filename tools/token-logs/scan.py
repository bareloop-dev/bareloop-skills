"""scan.py — read Claude Code's own session logs and report where the tokens went.

Claude Code writes one JSONL per session under ~/.claude/projects/<slug>/.
Every assistant message carries a `usage` block from the API itself:

    input_tokens                  sent uncached, billed 1x
    cache_creation_input_tokens   written to cache, billed 2x
    cache_read_input_tokens       read from cache, billed 0.1x
    output_tokens                 generated, billed at the output rate

That is real billing data, not an estimate. This script aggregates it. It reads
only; it never writes to the log directory.

    python scan.py            summary
    python scan.py --json     machine-readable, for the audit

Nothing here needs a tokenizer: the counts come from the API. `tiktoken` is used
only to measure the SIZE OF WHAT THE USER TYPED, which the logs record as text
rather than as a count.
"""
import json
import os
import sys
from collections import defaultdict

ROOT = os.path.expanduser("~/.claude/projects")

# Anthropic's published multipliers relative to the base input rate.
W_INPUT, W_WRITE, W_READ = 1.0, 2.0, 0.1


def sessions():
    for proj in sorted(os.listdir(ROOT)):
        d = os.path.join(ROOT, proj)
        if not os.path.isdir(d):
            continue
        for fn in sorted(os.listdir(d)):
            if fn.endswith(".jsonl"):
                yield proj, os.path.join(d, fn)


def read(path):
    """Yield parsed lines, skipping anything malformed. Logs are appended to
    live, so a truncated last line is normal and is not an error."""
    with open(path, encoding="utf-8", errors="replace") as fh:
        for line in fh:
            line = line.strip()
            if not line:
                continue
            try:
                yield json.loads(line)
            except ValueError:
                continue


def user_text(d):
    """The text a human actually typed. Tool results and attachments ride in
    user-role messages too, and counting those as 'what you typed' is the
    mistake that makes the headline claim look truer than it is."""
    m = d.get("message") or {}
    if m.get("role") != "user":
        return ""
    c = m.get("content")
    if isinstance(c, str):
        return c
    out = []
    for part in c or []:
        if not isinstance(part, dict):
            continue
        if part.get("type") == "text":
            t = part.get("text") or ""
            # System reminders and tool results are injected, not typed.
            if t.startswith("<system-reminder>"):
                continue
            out.append(t)
    return "\n".join(out)


def main():
    enc = None
    try:
        import tiktoken
        enc = tiktoken.get_encoding("cl100k_base")
    except Exception:
        pass

    tot = defaultdict(float)
    per_session = []
    per_project = defaultdict(lambda: defaultdict(float))
    starts = []          # first request of each session = the startup context
    models = defaultdict(int)
    n_sessions = 0

    for proj, path in sessions():
        s = defaultdict(float)
        first = None
        typed_chars = 0
        typed_tokens = 0
        reqs = 0

        for d in read(path):
            t = d.get("type")
            if t == "user":
                txt = user_text(d)
                if txt:
                    typed_chars += len(txt)
                    if enc:
                        typed_tokens += len(enc.encode(txt))
            elif t == "assistant":
                m = d.get("message") or {}
                u = m.get("usage")
                if not u:
                    continue
                reqs += 1
                if m.get("model"):
                    models[m["model"]] += 1
                inp = u.get("input_tokens", 0) or 0
                wr = u.get("cache_creation_input_tokens", 0) or 0
                rd = u.get("cache_read_input_tokens", 0) or 0
                out = u.get("output_tokens", 0) or 0
                s["input"] += inp
                s["write"] += wr
                s["read"] += rd
                s["output"] += out
                if first is None:
                    first = {"input": inp, "write": wr, "read": rd,
                             "context": inp + wr + rd}

        if not reqs:
            continue
        n_sessions += 1
        s["requests"] = reqs
        s["typed_chars"] = typed_chars
        s["typed_tokens"] = typed_tokens
        s["billed"] = s["input"] * W_INPUT + s["write"] * W_WRITE + s["read"] * W_READ
        s["sent"] = s["input"] + s["write"] + s["read"]
        per_session.append({"project": proj, "file": os.path.basename(path), **s})
        for k, v in s.items():
            tot[k] += v
            per_project[proj][k] += v
        if first:
            starts.append(first)

    tot["sessions"] = n_sessions

    if "--json" in sys.argv:
        json.dump({"totals": dict(tot),
                   "sessions": per_session,
                   "starts": starts,
                   "projects": {k: dict(v) for k, v in per_project.items()},
                   "models": dict(models)},
                  sys.stdout, indent=1)
        return

    fmt = lambda n: f"{n:,.0f}"
    print(f"sessions {n_sessions}  ·  requests {fmt(tot['requests'])}  "
          f"·  projects {len(per_project)}")
    print()
    print("INPUT TOKENS SENT (what the API received)")
    sent = tot["sent"]
    for k, label in (("input", "uncached (1x)"), ("write", "cache write (2x)"),
                     ("read", "cache read (0.1x)")):
        print(f"  {label:<20} {fmt(tot[k]):>15}  {100*tot[k]/sent:5.1f} %")
    print(f"  {'total sent':<20} {fmt(sent):>15}")
    print()
    print("BILLED INPUT UNITS (after the multipliers)")
    b = tot["billed"]
    for k, w, label in (("input", W_INPUT, "uncached"),
                        ("write", W_WRITE, "cache write"),
                        ("read", W_READ, "cache read")):
        print(f"  {label:<20} {fmt(tot[k]*w):>15}  {100*tot[k]*w/b:5.1f} %")
    print(f"  {'total billed':<20} {fmt(b):>15}")
    print(f"  output tokens        {fmt(tot['output']):>15}   (billed separately)")
    print()
    print("WHAT THE HUMAN TYPED")
    print(f"  characters           {fmt(tot['typed_chars']):>15}")
    print(f"  tokens (cl100k)      {fmt(tot['typed_tokens']):>15}")
    print(f"  as share of sent     {100*tot['typed_tokens']/sent:14.3f} %")
    print(f"  as share of billed   {100*tot['typed_tokens']/b:14.3f} %")
    print()
    if starts:
        ctx = sorted(x["context"] for x in starts)
        mid = ctx[len(ctx) // 2]
        print("STARTUP CONTEXT (first request of each session)")
        print(f"  sessions measured    {len(ctx):>15}")
        print(f"  median               {fmt(mid):>15}")
        print(f"  min / max            {fmt(ctx[0]):>7} / {fmt(ctx[-1]):>7}")
    print()
    print("CACHE")
    print(f"  read / sent          {100*tot['read']/sent:14.1f} %")
    print(f"  write / sent         {100*tot['write']/sent:14.1f} %")
    ratio = tot["read"] / tot["write"] if tot["write"] else 0
    print(f"  reads per write      {ratio:14.2f}")
    print()
    print("MODELS")
    for m, n in sorted(models.items(), key=lambda kv: -kv[1]):
        print(f"  {m:<28} {fmt(n):>10} requests")


if __name__ == "__main__":
    main()
