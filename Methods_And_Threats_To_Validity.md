# Methods and Threats to Validity

## Methods

### Study Objective
This proof-of-concept (PoC) evaluates whether the proposed CarOS-A2X architecture yields directional improvements over an OEM-like baseline on safety and mission-oriented autonomy metrics. The PoC is designed as a hypothesis-checking simulation study rather than a certification-grade validation.

### Experimental Design
We conduct a comparative Monte Carlo simulation between two primary configurations:
1. **Baseline OEM-like L2+ stack** (no hybrid fallback, no agentic mission layer).
2. **CarOS-A2X PoC stack** (confidence-aware policy, hybrid fallback planner, agentic mission support).

In addition, we run a four-arm ablation study:
1. Full CarOS-A2X.
2. Single-LLM variant.
3. No inheritance engine.
4. A2A-only (no MCP).

### Scenario Model
Each episode samples one scenario from a fixed set representing common and safety-critical contexts:
1. Urban unprotected left turn.
2. Highway lane change.
3. Construction zone.
4. Adverse weather.
5. Pedestrian-dense roads.

Each scenario includes parameterized difficulty, out-of-distribution (OOD) probability, and hazard probability. Stochastic sampling introduces run-to-run variability while preserving scenario priors.

### Policy and Failure Modeling
The simulation computes:
1. A policy confidence value conditioned on scenario complexity and OOD characteristics.
2. A per-mile intervention probability calibrated to 2025-scale intervention magnitudes.
3. Hybrid fallback behavior triggered under low confidence, hazard, or OOD indicators.
4. Mission completion probability with/without agentic bonuses.
5. Unprotected-left-turn success as a specific benchmark slice.

Primary outputs are:
1. **Interventions per 1,000 miles**.
2. **Critical event rate (%)**.
3. **Mission success (%)**.
4. **Unprotected-left-turn success (%)**.

### Execution and Reproducibility
All runs are deterministic per random seed. Multi-seed aggregation reports mean and population standard deviation.

Reproduction commands:
```bash
cd /mnt/chromeos/MyFiles/Downloads/caros_sim
python3 simulate_caros.py --episodes 500000 --seed 7
./run_benchmark.sh 120000 12
python3 run_ablation.py --episodes 120000 --runs 12 --seed 500 --outdir results
```

Code and artifacts:
1. Simulation core: `simulate_caros.py`
2. Benchmark wrapper: `run_benchmark.sh`
3. Ablation runner and exporters: `run_ablation.py`
4. Results: `results/ablation_results.csv`, `results/ablation_interventions.svg`, `results/ablation_mission_success.svg`

### Current Observed Pattern
Across repeated seeds, CarOS-A2X shows lower intervention rates and higher mission success than baseline. Ablation ordering is consistent with the architectural hypothesis: full stack performs best, and degraded variants reduce performance, especially A2A-only.

## Threats to Validity

### Internal Validity
1. **Model-form assumptions**: Intervention and mission models are hand-parameterized abstractions, not learned from full raw fleet telemetry.
2. **Coupled mechanisms**: Hybrid and agentic gains may be partially entangled in the simulator logic, which can amplify apparent combined effects.
3. **Calibration sensitivity**: Absolute values depend on selected coefficients; small coefficient changes can shift reported rates.

Mitigation: multi-seed aggregation, explicit ablations, transparent code, and retained parameter traceability.

### Construct Validity
1. **Proxy metrics**: “Intervention per 1k mi” and “mission success” are modeled proxies, not directly measured vehicle-controller outcomes.
2. **Mission abstraction**: Natural-language mission completion is represented probabilistically, not by end-to-end tool execution in live environments.

Mitigation: reporting this work strictly as PoC evidence; avoiding over-claims of production readiness.

### External Validity
1. **Synthetic environment gap**: The simulator cannot capture full real-world distribution shift, sensor artifacts, map drift, or adversarial road-user behavior.
2. **Hardware/latency omission**: Embedded constraints (compute contention, thermal throttling, network intermittency) are not fully represented.
3. **Geographic/legal variation**: Regulatory and driving-culture variation across countries is not explicitly modeled.

Mitigation: planned transition to closed-loop scenario engines (nuPlan/CARLA/Isaac) and audited on-road studies.

### Statistical Conclusion Validity
1. **Finite sample noise**: Although variance is reported, uncertainty intervals are not yet formalized as confidence intervals or hypothesis tests.
2. **Scenario prior selection**: Results depend on scenario weighting; alternate priors may alter aggregate outcomes.

Mitigation: publish scenario priors, report per-scenario metrics, and add confidence intervals plus bootstrap analyses in future work.

## Recommended Next Validation Steps
1. Run identical ablation protocol in closed-loop CARLA/nuPlan with standardized public scenario suites.
2. Add per-scenario confidence intervals and significance testing.
3. Perform stress tests for OOD-heavy distributions and adverse weather amplification.
4. Introduce latency-budget and fail-silent watchdog simulations tied to hardware profiles.
5. Reconcile simulated metrics with audited real-world logs under a preregistered evaluation protocol.

## Positioning Statement
This PoC provides **directional and architectural evidence** that the CarOS-A2X design is plausible and performance-improving under controlled stochastic simulation. It is not a substitute for formal safety case approval or real-world certification evidence.
