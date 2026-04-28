#!/usr/bin/env python3
import json
import re
import sys

data = json.load(open("build/metrics.json"))

baselines = {}
try:
    with open("specs/performance_baselines.toml") as f:
        for m in re.finditer(r"\[baselines\.(\S+?)\]\s+cold_median\s*=\s*([\d.]+)", f.read()):
            baselines[m.group(1)] = float(m.group(2))
except Exception:
    pass

print("| Example | Wall Time (s) | Baseline (s) | Delta | PDF Size | Status |")
print("|---------|---------------|-------------|-------|----------|--------|")

regressions = []
for ex in data.get("examples", []):
    status = ":white_check_mark:" if ex["success"] else ":x:"
    size_kb = ex.get("pdf_size_bytes", 0) / 1024
    name = ex["name"]
    wall = ex.get("wall_time_s") or 0
    size_kb = ex.get("pdf_size_bytes", 0) or 0
    name = ex["name"]

    if name in baselines:
        baseline = baselines[name]
        delta = wall - baseline
        delta_str = f"{delta:+.1f}s"
        if baseline > 0 and delta / baseline > 0.5:
            status = ":warning:"
            regressions.append((name, wall, baseline, delta))
    else:
        baseline = None
        delta_str = "N/A"

    wall_str = f"{wall:.1f}" if wall else "FAIL"
    bl_str = f"{baseline:.1f}" if baseline else "N/A"
    print(f"| {name} | {wall_str} | {bl_str:>8} | {delta_str:>6} | {size_kb:.0f} KB | {status} |")

s = data.get("summary", {})
print()
print(f"**Total:** {s.get('total_time_s', 0):.1f}s across {s.get('total', 0)} examples ({s.get('successful', 0)} successful)")

if regressions:
    print()
    print("### :warning: Performance Regressions Detected")
    print()
    print("| Example | Current (s) | Baseline (s) | Delta |")
    print("|---------|-------------|---------------|-------|")
    for name, wall, baseline, delta in regressions:
        print(f"| {name} | {wall:.1f} | {baseline:.1f} | {delta:+.1f}s |")
    print()
    print("Regressions are flagged when current time exceeds baseline by > 50%.")
    print("Baselines are in `specs/performance_baselines.toml`.")
    sys.exit(1)
