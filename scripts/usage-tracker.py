#!/usr/bin/env python3
"""
Daily Claude Usage & Billing Report Generator
Scans OpenClaw session logs for token usage and cost data.
"""
import json, os, glob, sys
from datetime import datetime, timezone, timedelta
from pathlib import Path
from collections import defaultdict

JST = timezone(timedelta(hours=9))

def parse_date_arg():
    """Parse optional date argument (YYYY-MM-DD), default today JST."""
    if len(sys.argv) > 1:
        return datetime.strptime(sys.argv[1], "%Y-%m-%d").replace(tzinfo=JST)
    return datetime.now(JST)

def scan_sessions(target_date):
    """Scan all session jsonl files for usage entries on target_date."""
    base = os.path.expanduser("~/.openclaw/agents")
    pattern = os.path.join(base, "*", "sessions", "*.jsonl")
    
    day_start = target_date.replace(hour=0, minute=0, second=0, microsecond=0)
    day_end = day_start + timedelta(days=1)
    start_ms = int(day_start.timestamp() * 1000)
    end_ms = int(day_end.timestamp() * 1000)
    
    totals = defaultdict(lambda: {
        "input": 0, "output": 0, "cacheRead": 0, "cacheWrite": 0,
        "totalTokens": 0, "requests": 0,
        "cost_input": 0, "cost_output": 0, "cost_cacheRead": 0,
        "cost_cacheWrite": 0, "cost_total": 0
    })
    
    sessions_seen = set()
    
    for fpath in glob.glob(pattern):
        if fpath.endswith(".lock"):
            continue
        try:
            with open(fpath, "r") as f:
                for line in f:
                    try:
                        entry = json.loads(line.strip())
                        ts = entry.get("timestamp") or entry.get("ts", 0)
                        if isinstance(ts, str):
                            ts = int(datetime.fromisoformat(ts).timestamp() * 1000)
                        elif ts < 1e12:
                            ts = int(ts * 1000)
                        
                        if not (start_ms <= ts < end_ms):
                            continue
                        
                        msg = entry.get("message", {})
                        usage = msg.get("usage")
                        if not usage:
                            continue
                        
                        model = msg.get("model", "unknown")
                        cost = usage.get("cost", {})
                        
                        t = totals[model]
                        t["input"] += usage.get("input", 0)
                        t["output"] += usage.get("output", 0)
                        t["cacheRead"] += usage.get("cacheRead", 0)
                        t["cacheWrite"] += usage.get("cacheWrite", 0)
                        t["totalTokens"] += usage.get("totalTokens", 0)
                        t["requests"] += 1
                        t["cost_input"] += cost.get("input", 0)
                        t["cost_output"] += cost.get("output", 0)
                        t["cost_cacheRead"] += cost.get("cacheRead", 0)
                        t["cost_cacheWrite"] += cost.get("cacheWrite", 0)
                        t["cost_total"] += cost.get("total", 0)
                        
                        sessions_seen.add(os.path.basename(fpath).replace(".jsonl", ""))
                    except (json.JSONDecodeError, ValueError):
                        continue
        except (IOError, PermissionError):
            continue
    
    return dict(totals), len(sessions_seen)

def format_tokens(n):
    if n >= 1_000_000:
        return f"{n/1_000_000:.1f}M"
    elif n >= 1_000:
        return f"{n/1_000:.1f}k"
    return str(n)

def generate_report(target_date):
    date_str = target_date.strftime("%Y-%m-%d")
    totals, session_count = scan_sessions(target_date)
    
    if not totals:
        return f"# Claude Usage Report — {date_str}\n\nNo API usage recorded for this date.\n"
    
    lines = [
        f"# Claude Usage Report — {date_str}",
        f"",
        f"**Generated:** {datetime.now(JST).strftime('%Y-%m-%d %H:%M')} JST",
        f"**Active Sessions:** {session_count}",
        f"",
    ]
    
    grand = defaultdict(float)
    
    for model, t in sorted(totals.items()):
        cache_pct = (t["cacheRead"] / (t["cacheRead"] + t["input"] + t["cacheWrite"])) * 100 if (t["cacheRead"] + t["input"] + t["cacheWrite"]) > 0 else 0
        
        lines.extend([
            f"## {model}",
            f"",
            f"| Metric | Tokens | Cost |",
            f"|--------|--------|------|",
            f"| Input (new) | {format_tokens(t['input'])} | ${t['cost_input']:.4f} |",
            f"| Output | {format_tokens(t['output'])} | ${t['cost_output']:.4f} |",
            f"| Cache Read | {format_tokens(t['cacheRead'])} | ${t['cost_cacheRead']:.4f} |",
            f"| Cache Write | {format_tokens(t['cacheWrite'])} | ${t['cost_cacheWrite']:.4f} |",
            f"| **Total** | **{format_tokens(t['totalTokens'])}** | **${t['cost_total']:.4f}** |",
            f"",
            f"- Requests: {t['requests']}",
            f"- Cache hit rate: {cache_pct:.0f}%",
            f"",
        ])
        
        grand["tokens"] += t["totalTokens"]
        grand["cost"] += t["cost_total"]
        grand["requests"] += t["requests"]
    
    lines.extend([
        f"---",
        f"",
        f"## Daily Summary",
        f"",
        f"| | Value |",
        f"|--|-------|",
        f"| Total Tokens | {format_tokens(int(grand['tokens']))} |",
        f"| Total Cost | **${grand['cost']:.4f}** |",
        f"| API Requests | {int(grand['requests'])} |",
        f"| Models Used | {len(totals)} |",
        f"",
    ])
    
    # Monthly projection & budget tracking
    MONTHLY_BUDGET = 20.00
    day_of_month = target_date.day
    
    # Calculate month-to-date spend
    mtd_cost = 0
    for d in range(1, day_of_month + 1):
        check_date = target_date.replace(day=d)
        day_totals, _ = scan_sessions(check_date)
        for t in day_totals.values():
            mtd_cost += t["cost_total"]
    
    remaining = MONTHLY_BUDGET - mtd_cost
    pct_used = (mtd_cost / MONTHLY_BUDGET) * 100
    
    if day_of_month > 0:
        projected = mtd_cost * 30 / day_of_month if day_of_month > 1 else mtd_cost * 30

    lines.extend([
        f"",
        f"## 💰 Budget Tracker ($20/mo)",
        f"",
        f"| | Value |",
        f"|--|-------|",
        f"| Month-to-date | ${mtd_cost:.2f} |",
        f"| Remaining | ${remaining:.2f} |",
        f"| Used | {pct_used:.0f}% |",
        f"| Projected | ~${projected:.2f}/mo |",
        f"",
    ])
    
    if pct_used >= 90:
        lines.append(f"🔴 **WARNING: {pct_used:.0f}% of monthly budget used!**")
    elif pct_used >= 70:
        lines.append(f"🟡 **Heads up: {pct_used:.0f}% of monthly budget used.**")
    else:
        lines.append(f"🟢 Budget on track.")
    
    return "\n".join(lines)

def main():
    target = parse_date_arg()
    report = generate_report(target)
    
    date_str = target.strftime("%Y-%m-%d")
    out_dir = os.path.expanduser("~/.openclaw/workspace/reports")
    os.makedirs(out_dir, exist_ok=True)
    out_path = os.path.join(out_dir, f"usage-{date_str}.md")
    
    with open(out_path, "w") as f:
        f.write(report)
    
    print(report)
    print(f"\n---\nSaved to: {out_path}")

if __name__ == "__main__":
    main()
