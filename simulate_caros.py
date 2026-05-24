#!/usr/bin/env python3
import argparse
import dataclasses
import math
import random
import statistics
from typing import Dict, List


@dataclasses.dataclass
class Scenario:
    name: str
    difficulty: float
    ood_prob: float
    hazard_prob: float


SCENARIOS = [
    Scenario("urban_unprotected_left", difficulty=0.75, ood_prob=0.12, hazard_prob=0.15),
    Scenario("highway_lane_change", difficulty=0.35, ood_prob=0.04, hazard_prob=0.06),
    Scenario("construction_zone", difficulty=0.80, ood_prob=0.18, hazard_prob=0.18),
    Scenario("adverse_weather", difficulty=0.70, ood_prob=0.20, hazard_prob=0.14),
    Scenario("pedestrian_dense", difficulty=0.85, ood_prob=0.22, hazard_prob=0.20),
]


@dataclasses.dataclass
class StackConfig:
    name: str
    base_intervention_rate: float
    confidence_noise: float
    hybrid_enabled: bool
    hybrid_recovery_rate: float
    agentic_enabled: bool
    mission_success_bonus: float


BASELINE_OEM = StackConfig(
    name="Baseline OEM-like L2+",
    base_intervention_rate=0.00052,
    confidence_noise=0.12,
    hybrid_enabled=False,
    hybrid_recovery_rate=0.0,
    agentic_enabled=False,
    mission_success_bonus=0.0,
)

CAROS_A2X = StackConfig(
    name="CarOS-A2X (Theory PoC)",
    base_intervention_rate=0.00040,
    confidence_noise=0.07,
    hybrid_enabled=True,
    hybrid_recovery_rate=0.62,
    agentic_enabled=True,
    mission_success_bonus=0.10,
)


def clamp(v: float, lo: float, hi: float) -> float:
    return max(lo, min(hi, v))


def policy_confidence(config: StackConfig, sc: Scenario, rng: random.Random) -> float:
    # Higher difficulty and OOD reduce confidence.
    nominal = 1.0 - (0.60 * sc.difficulty + 0.40 * sc.ood_prob)
    noisy = nominal + rng.gauss(0.0, config.confidence_noise)
    return clamp(noisy, 0.0, 1.0)


def run_episode(config: StackConfig, rng: random.Random) -> Dict[str, float]:
    sc = rng.choice(SCENARIOS)
    confidence = policy_confidence(config, sc, rng)

    hazard = rng.random() < sc.hazard_prob
    ood = rng.random() < sc.ood_prob

    # Per-mile intervention model calibrated to 2025-era intervention scales.
    fail_prob = (
        config.base_intervention_rate
        + 0.00075 * sc.difficulty
        + (0.00055 if ood else 0.0)
        + (0.00025 if hazard else 0.0)
        - 0.00065 * confidence
    )
    fail_prob = clamp(fail_prob, 0.00001, 0.02)

    policy_failed = rng.random() < fail_prob
    intervention = policy_failed
    critical = False

    # Hybrid planner fallback.
    if config.hybrid_enabled and policy_failed:
        fallback_trigger = confidence < 0.47 or ood or hazard
        if fallback_trigger:
            recovered = rng.random() < config.hybrid_recovery_rate
            if recovered:
                intervention = False
            else:
                critical = hazard and rng.random() < 0.012
        else:
            critical = hazard and rng.random() < 0.02
    else:
        critical = policy_failed and hazard and rng.random() < 0.03

    # Mission completion model for natural-language tasks.
    mission_base = 0.70 - 0.28 * sc.difficulty + 0.20 * confidence
    if config.agentic_enabled:
        mission_base += config.mission_success_bonus
    mission_success = rng.random() < clamp(mission_base, 0.05, 0.99)

    # Specific benchmark: unprotected left turn success.
    left_turn_success = None
    if sc.name == "urban_unprotected_left":
        lt_base = 0.78 + 0.18 * confidence - 0.10 * (1.0 if ood else 0.0)
        if config.hybrid_enabled:
            lt_base += 0.05
        left_turn_success = rng.random() < clamp(lt_base, 0.0, 0.999)

    return {
        "intervention": 1.0 if intervention else 0.0,
        "critical": 1.0 if critical else 0.0,
        "mission_success": 1.0 if mission_success else 0.0,
        "left_turn_present": 1.0 if left_turn_success is not None else 0.0,
        "left_turn_success": 1.0 if left_turn_success else 0.0,
    }


def run_sim(config: StackConfig, episodes: int, seed: int) -> Dict[str, float]:
    rng = random.Random(seed)
    rows = [run_episode(config, rng) for _ in range(episodes)]

    interventions = sum(r["intervention"] for r in rows)
    criticals = sum(r["critical"] for r in rows)
    mission = sum(r["mission_success"] for r in rows)

    lt_rows = [r for r in rows if r["left_turn_present"] > 0]
    lt_total = len(lt_rows)
    lt_success = sum(r["left_turn_success"] for r in lt_rows)

    return {
        "episodes": episodes,
        "interventions_per_1k": 1000.0 * interventions / episodes,
        "critical_rate_pct": 100.0 * criticals / episodes,
        "mission_success_pct": 100.0 * mission / episodes,
        "left_turn_success_pct": 100.0 * lt_success / max(1, lt_total),
        "left_turn_n": lt_total,
    }


def percent_improvement(old: float, new: float) -> float:
    if math.isclose(old, 0.0):
        return 0.0
    return 100.0 * (old - new) / old


def main() -> None:
    parser = argparse.ArgumentParser(description="CarOS-A2X theory simulator")
    parser.add_argument("--episodes", type=int, default=30000)
    parser.add_argument("--seed", type=int, default=42)
    args = parser.parse_args()

    baseline = run_sim(BASELINE_OEM, args.episodes, args.seed)
    caros = run_sim(CAROS_A2X, args.episodes, args.seed + 1)

    print("=== Simulation Summary ===")
    print(f"Episodes per stack: {args.episodes}")
    print("")

    def print_stack(name: str, m: Dict[str, float]) -> None:
        print(name)
        print(f"  interventions_per_1k      : {m['interventions_per_1k']:.2f}")
        print(f"  critical_event_rate_pct   : {m['critical_rate_pct']:.3f}%")
        print(f"  mission_success_pct       : {m['mission_success_pct']:.2f}%")
        print(f"  left_turn_success_pct     : {m['left_turn_success_pct']:.2f}% (n={int(m['left_turn_n'])})")

    print_stack(BASELINE_OEM.name, baseline)
    print("")
    print_stack(CAROS_A2X.name, caros)
    print("")

    intrv_gain = percent_improvement(baseline["interventions_per_1k"], caros["interventions_per_1k"])
    mission_gain = caros["mission_success_pct"] - baseline["mission_success_pct"]
    lt_gain = caros["left_turn_success_pct"] - baseline["left_turn_success_pct"]

    print("=== Delta (CarOS vs Baseline) ===")
    print(f"Intervention reduction: {intrv_gain:.2f}%")
    print(f"Mission success gain : {mission_gain:.2f} points")
    print(f"Left-turn gain       : {lt_gain:.2f} points")


if __name__ == "__main__":
    main()
