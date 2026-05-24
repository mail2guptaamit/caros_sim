# CarOS-A2X Theory Simulator (Proof of Concept)

This is a lightweight Monte Carlo simulator to test the *directional validity* of your CarOS-A2X theory.

It models three core ideas from your paper:
- `SuperPilot-like policy`: confidence-driven driving performance.
- `Hybrid planner fallback`: recovery when policy confidence is low or scenario is OOD.
- `Agentic mission layer`: improved natural-language mission completion.

## Files
- `simulate_caros.py`: main simulator.
- `run_benchmark.sh`: repeats simulation across seeds and reports average gains/std-dev.

## Run
```bash
cd /mnt/chromeos/MyFiles/Downloads/caros_sim
python3 simulate_caros.py --episodes 50000 --seed 7
```

## Multi-run benchmark
```bash
cd /mnt/chromeos/MyFiles/Downloads/caros_sim
./run_benchmark.sh 15000 12
```

## Ablation study (Table-7 style)
```bash
cd /mnt/chromeos/MyFiles/Downloads/caros_sim
python3 run_ablation.py --episodes 120000 --runs 12 --seed 500
```

## Generate episode-level dataset (thousands+ rows)
```bash
cd /mnt/chromeos/MyFiles/Downloads/caros_sim
python3 generate_episode_dataset.py --episodes 10000 --runs 12 --seed 500 --out results/episode_level_dataset.csv
```

Row count formula:
- `rows = 4 configs x runs x episodes`
- Example above creates `4 x 12 x 10000 = 480000` data rows.

## Current observed results (example)
From one 500k-episode run:
- Baseline interventions: `0.78 / 1k mi`
- CarOS interventions: `0.33 / 1k mi`
- Intervention reduction: `57.54%`
- Mission success gain: `+10.10 points`
- Unprotected left-turn gain: `+4.90 points`

From 12-run aggregate (120k each):
- Avg intervention reduction: `52.74%` (std `10.48`)
- Avg mission gain: `+10.00` points (std `0.19`)
- Avg left-turn gain: `+5.03` points (std `0.29`)

## Important scientific note
This is not a real-vehicle validation and not a replacement for CARLA/Isaac/nuPlan closed-loop testing. It is a hypothesis-checking simulator to verify that your architecture assumptions can produce the claimed trend.

## Next extension for stronger evidence
- Replace synthetic scenario dynamics with CARLA/nuPlan trajectories.
- Connect ROS 2 planner node behavior and latency budgets.
- Add confidence-interval testing and ablation studies (disable one module at a time).
