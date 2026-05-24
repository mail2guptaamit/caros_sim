# CarOS-A2X PoC: Step-by-Step (Problem, Steps, Outcomes, Proof)

## 1) Problem Statement

Current autonomy stacks often face two gaps:
1. **Safety robustness gap**: intervention frequency rises under difficult, OOD, or hazard-heavy conditions.
2. **Mission-intelligence gap**: natural-language mission completion is usually disconnected from low-level driving policy quality.

The PoC goal is to test whether the CarOS-A2X architecture direction can reduce interventions while improving mission completion in a controlled simulation setting.

## 2) PoC Objective

Demonstrate **directional evidence** that the CarOS-A2X design improves key metrics compared with weaker variants and an OEM-like baseline in Monte Carlo simulation.

This PoC is not intended to claim production readiness or certification-level safety proof.

## 3) Architecture Hypothesis

CarOS-A2X combines three ideas:
1. **Confidence-aware policy behavior**
2. **Hybrid fallback planner** for recovery under low confidence/OOD/hazards
3. **Agentic mission layer** to improve mission completion outcomes

Hypothesis: combining these modules gives better aggregate performance than removing any one of them.

## 4) Experimental Configurations

The ablation study uses four configurations:
1. `CarOS-A2X (Theory PoC)` (full stack)
2. `Single LLM (Claude only)`
3. `No inheritance engine`
4. `A2A-only (no MCP)`

## 5) Scenario Model

Each episode samples one scenario type:
1. Urban unprotected left turn
2. Highway lane change
3. Construction zone
4. Adverse weather
5. Pedestrian-dense roads

Each scenario includes difficulty, OOD probability, and hazard probability.

## 6) Episode Logic (Per Simulation Episode)

For each episode the simulator performs:
1. Sample scenario and compute policy confidence.
2. Compute intervention/failure probability from difficulty, OOD, hazard, and confidence.
3. Apply hybrid fallback recovery (if enabled).
4. Compute mission success probability (with/without agentic bonus).
5. Track left-turn success when scenario is unprotected-left-turn.

## 7) Metrics

Primary metrics:
1. `interventions_per_1k`
2. `critical_rate_pct`
3. `mission_success_pct`
4. `left_turn_success_pct`

## 8) Data Generation Workflow

### A) Aggregated ablation output
```bash
python3 run_ablation.py --episodes 120000 --runs 12 --seed 500 --outdir results
```

### B) Episode-level raw dataset (thousands to hundreds of thousands of rows)
```bash
python3 generate_episode_dataset.py --episodes 10000 --runs 12 --seed 500 --out results/episode_level_dataset.csv
```

Row count formula:
- `rows = 4 configs x runs x episodes`

Example:
- `4 x 12 x 10000 = 480000` rows

## 9) Visual Analysis Added

Using `results/episode_level_dataset_sample.csv`, the following visuals are generated:
1. `results/poc_interventions_points.svg`
2. `results/poc_mission_points.svg`
3. `results/poc_tradeoff_scatter.svg`
4. `results/poc_summary_from_sample.csv`

These include run-level data points and variability, not only single-point means.

## 10) Observed Outcomes (From Sample Dataset)

From `results/poc_summary_from_sample.csv`:
1. Full CarOS-A2X has highest mission success (`71.13%` in sample).
2. A2A-only has lowest mission success (`50.30%` in sample).
3. CarOS-A2X intervention rate in sample is lower than the other non-full variants.

Interpretation: observed ranking aligns with the architecture hypothesis in this PoC setting.

## 11) What This PoC Proves

This PoC **does prove**:
1. The architecture is directionally plausible under controlled stochastic simulation.
2. Module ablations produce expected degradation trends.
3. The workflow is reproducible with deterministic seeds and explicit scripts.

## 12) What This PoC Does Not Prove

This PoC **does not prove**:
1. Real-world safety certification readiness.
2. Guaranteed sim-to-real transfer.
3. Robustness under real hardware/latency/regulatory constraints.

## 13) Recommended Next Steps for Stronger IEEE Evidence

1. Compute confidence intervals and statistical significance on full episode-level dataset.
2. Report per-scenario breakdown (not only global averages).
3. Re-run the same protocol in closed-loop environments (CARLA/nuPlan/Isaac).
4. Add sensitivity analysis over scenario priors and coefficient calibration.
5. Validate against audited real-world logs where feasible.

## 14) Bottom-Line Positioning

This work should be presented as a **hypothesis-checking and directional-evidence PoC** with reproducible simulation artifacts, not as a claim of production deployment or certified safety.
