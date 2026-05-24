#!/usr/bin/env python3
import argparse
import csv
import os
import random
from typing import List

from run_ablation import make_ablation_configs
from simulate_caros import run_episode


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Generate episode-level dataset for CarOS-A2X ablation configs"
    )
    parser.add_argument("--episodes", type=int, default=5000, help="Episodes per run")
    parser.add_argument("--runs", type=int, default=12, help="Number of runs per configuration")
    parser.add_argument("--seed", type=int, default=500, help="Starting seed")
    parser.add_argument("--out", type=str, default="results/episode_level_dataset.csv", help="Output CSV path")
    args = parser.parse_args()

    os.makedirs(os.path.dirname(args.out) or ".", exist_ok=True)

    configs = make_ablation_configs()
    total_rows = 0

    with open(args.out, "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(
            [
                "configuration",
                "run_id",
                "seed",
                "episode_idx",
                "intervention",
                "critical",
                "mission_success",
                "left_turn_present",
                "left_turn_success",
            ]
        )

        for cfg in configs:
            for run_id in range(args.runs):
                seed = args.seed + run_id
                rng = random.Random(seed)
                for episode_idx in range(args.episodes):
                    row = run_episode(cfg, rng)
                    w.writerow(
                        [
                            cfg.name,
                            run_id,
                            seed,
                            episode_idx,
                            int(row["intervention"]),
                            int(row["critical"]),
                            int(row["mission_success"]),
                            int(row["left_turn_present"]),
                            int(row["left_turn_success"]),
                        ]
                    )
                    total_rows += 1

    print(f"Wrote {total_rows} rows to {args.out}")
    print(f"Rows formula: configs({len(configs)}) x runs({args.runs}) x episodes({args.episodes})")


if __name__ == "__main__":
    main()
