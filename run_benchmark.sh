#!/usr/bin/env bash
set -euo pipefail

EPISODES="${1:-20000}"
RUNS="${2:-10}"

printf "episodes_per_run=%s runs=%s\n" "$EPISODES" "$RUNS"

python3 - <<'PY' "$EPISODES" "$RUNS"
import subprocess
import sys
import re
import statistics

episodes = int(sys.argv[1])
runs = int(sys.argv[2])

intrv = []
mission = []
lt = []

for i in range(runs):
    cmd = ["python3", "simulate_caros.py", "--episodes", str(episodes), "--seed", str(100 + i)]
    out = subprocess.check_output(cmd, text=True)
    m1 = re.search(r"Intervention reduction: ([0-9.]+)%", out)
    m2 = re.search(r"Mission success gain\s+: ([0-9.]+) points", out)
    m3 = re.search(r"Left-turn gain\s+: ([0-9.]+) points", out)
    intrv.append(float(m1.group(1)))
    mission.append(float(m2.group(1)))
    lt.append(float(m3.group(1)))

print("avg_intervention_reduction_pct", round(statistics.mean(intrv), 3))
print("std_intervention_reduction_pct", round(statistics.pstdev(intrv), 3))
print("avg_mission_gain_points", round(statistics.mean(mission), 3))
print("std_mission_gain_points", round(statistics.pstdev(mission), 3))
print("avg_left_turn_gain_points", round(statistics.mean(lt), 3))
print("std_left_turn_gain_points", round(statistics.pstdev(lt), 3))
PY
