#!/usr/bin/env python3
import argparse
import csv
import os
import statistics
from typing import Dict, List, Tuple

from simulate_caros import CAROS_A2X, StackConfig, run_sim


def save_bar_svg(
    path: str,
    title: str,
    y_label: str,
    labels: List[str],
    means: List[float],
    stds: List[float],
) -> None:
    width = 1200
    height = 700
    left = 100
    right = 40
    top = 90
    bottom = 220
    plot_w = width - left - right
    plot_h = height - top - bottom
    n = len(labels)
    ymax = max((m + s for m, s in zip(means, stds)), default=1.0)
    ymax = ymax * 1.20 if ymax > 0 else 1.0
    bar_w = plot_w / max(1, n) * 0.56
    gap = plot_w / max(1, n)

    def y_to_px(v: float) -> float:
        return top + plot_h - (v / ymax) * plot_h

    lines: List[str] = []
    lines.append(f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}">')
    lines.append('<rect x="0" y="0" width="100%" height="100%" fill="white"/>')
    lines.append(
        f'<text x="{width/2:.0f}" y="42" text-anchor="middle" font-family="Arial" font-size="28">{title}</text>'
    )
    lines.append(
        f'<text x="{left-65}" y="{top + plot_h/2:.0f}" transform="rotate(-90 {left-65},{top + plot_h/2:.0f})" '
        f'text-anchor="middle" font-family="Arial" font-size="18">{y_label}</text>'
    )
    lines.append(f'<line x1="{left}" y1="{top}" x2="{left}" y2="{top+plot_h}" stroke="#333" stroke-width="2"/>')
    lines.append(
        f'<line x1="{left}" y1="{top+plot_h}" x2="{left+plot_w}" y2="{top+plot_h}" stroke="#333" stroke-width="2"/>'
    )

    for i in range(6):
        v = ymax * i / 5.0
        y = y_to_px(v)
        lines.append(
            f'<line x1="{left}" y1="{y:.1f}" x2="{left+plot_w}" y2="{y:.1f}" stroke="#d9d9d9" stroke-width="1"/>'
        )
        lines.append(
            f'<text x="{left-12}" y="{y+5:.1f}" text-anchor="end" font-family="Arial" font-size="14">{v:.2f}</text>'
        )

    colors = ["#2f5597", "#4f81bd", "#7aa5d2", "#9dc3e6"]
    for i, (label, mean, std) in enumerate(zip(labels, means, stds)):
        cx = left + gap * i + gap / 2
        x = cx - bar_w / 2
        y = y_to_px(mean)
        h = top + plot_h - y
        color = colors[i % len(colors)]
        lines.append(f'<rect x="{x:.1f}" y="{y:.1f}" width="{bar_w:.1f}" height="{h:.1f}" fill="{color}"/>')
        ey1 = y_to_px(mean + std)
        ey2 = y_to_px(max(0.0, mean - std))
        lines.append(f'<line x1="{cx:.1f}" y1="{ey1:.1f}" x2="{cx:.1f}" y2="{ey2:.1f}" stroke="#111" stroke-width="2"/>')
        lines.append(
            f'<line x1="{cx-10:.1f}" y1="{ey1:.1f}" x2="{cx+10:.1f}" y2="{ey1:.1f}" stroke="#111" stroke-width="2"/>'
        )
        lines.append(
            f'<line x1="{cx-10:.1f}" y1="{ey2:.1f}" x2="{cx+10:.1f}" y2="{ey2:.1f}" stroke="#111" stroke-width="2"/>'
        )
        lines.append(
            f'<text x="{cx:.1f}" y="{top+plot_h+26}" text-anchor="middle" font-family="Arial" font-size="14" '
            f'transform="rotate(18 {cx:.1f},{top+plot_h+26})">{label}</text>'
        )
        lines.append(
            f'<text x="{cx:.1f}" y="{y-10:.1f}" text-anchor="middle" font-family="Arial" font-size="13">{mean:.2f}</text>'
        )

    lines.append("</svg>")
    with open(path, "w", encoding="utf-8") as f:
        f.write("\n".join(lines))


def make_ablation_configs() -> List[StackConfig]:
    full = CAROS_A2X
    single_llm = StackConfig(
        name="Single LLM (Claude only)",
        base_intervention_rate=0.00044,
        confidence_noise=0.09,
        hybrid_enabled=True,
        hybrid_recovery_rate=0.50,
        agentic_enabled=True,
        mission_success_bonus=0.03,
    )
    no_inheritance = StackConfig(
        name="No inheritance engine",
        base_intervention_rate=0.00046,
        confidence_noise=0.09,
        hybrid_enabled=True,
        hybrid_recovery_rate=0.46,
        agentic_enabled=True,
        mission_success_bonus=0.02,
    )
    a2a_only = StackConfig(
        name="A2A-only (no MCP)",
        base_intervention_rate=0.00050,
        confidence_noise=0.11,
        hybrid_enabled=False,
        hybrid_recovery_rate=0.0,
        agentic_enabled=True,
        mission_success_bonus=-0.10,
    )
    return [full, single_llm, no_inheritance, a2a_only]


def run_multi_seed(cfg: StackConfig, episodes: int, runs: int, seed: int) -> Dict[str, float]:
    rows = [run_sim(cfg, episodes, seed + i) for i in range(runs)]
    return {
        "interventions_per_1k_mean": statistics.mean(r["interventions_per_1k"] for r in rows),
        "interventions_per_1k_std": statistics.pstdev(r["interventions_per_1k"] for r in rows),
        "mission_success_pct_mean": statistics.mean(r["mission_success_pct"] for r in rows),
        "mission_success_pct_std": statistics.pstdev(r["mission_success_pct"] for r in rows),
    }


def main() -> None:
    parser = argparse.ArgumentParser(description="CarOS-A2X ablation runner")
    parser.add_argument("--episodes", type=int, default=120000)
    parser.add_argument("--runs", type=int, default=10)
    parser.add_argument("--seed", type=int, default=500)
    parser.add_argument("--outdir", type=str, default="results")
    args = parser.parse_args()

    os.makedirs(args.outdir, exist_ok=True)

    configs = make_ablation_configs()
    results: List[Tuple[StackConfig, Dict[str, float]]] = []
    for cfg in configs:
        results.append((cfg, run_multi_seed(cfg, args.episodes, args.runs, args.seed)))

    print("=== Ablation Study ===")
    print(f"episodes_per_run={args.episodes} runs={args.runs} seed_start={args.seed}")
    print("")
    print("Configuration | Intervention Rate (/1k mi) | Mission Success (%)")
    print("-" * 67)
    for cfg, r in results:
        intrv = f"{r['interventions_per_1k_mean']:.2f} +/- {r['interventions_per_1k_std']:.2f}"
        mission = f"{r['mission_success_pct_mean']:.2f} +/- {r['mission_success_pct_std']:.2f}"
        print(f"{cfg.name} | {intrv} | {mission}")

    csv_path = os.path.join(args.outdir, "ablation_results.csv")
    with open(csv_path, "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(
            [
                "configuration",
                "interventions_per_1k_mean",
                "interventions_per_1k_std",
                "mission_success_pct_mean",
                "mission_success_pct_std",
                "episodes_per_run",
                "runs",
                "seed_start",
            ]
        )
        for cfg, r in results:
            w.writerow(
                [
                    cfg.name,
                    round(r["interventions_per_1k_mean"], 6),
                    round(r["interventions_per_1k_std"], 6),
                    round(r["mission_success_pct_mean"], 6),
                    round(r["mission_success_pct_std"], 6),
                    args.episodes,
                    args.runs,
                    args.seed,
                ]
            )
    print("")
    print(f"CSV exported: {csv_path}")

    labels = [cfg.name for cfg, _ in results]
    intrv_mean = [r["interventions_per_1k_mean"] for _, r in results]
    intrv_std = [r["interventions_per_1k_std"] for _, r in results]
    mission_mean = [r["mission_success_pct_mean"] for _, r in results]
    mission_std = [r["mission_success_pct_std"] for _, r in results]

    try:
        import matplotlib.pyplot as plt  # type: ignore
    except Exception as e:
        p1 = os.path.join(args.outdir, "ablation_interventions.svg")
        p2 = os.path.join(args.outdir, "ablation_mission_success.svg")
        save_bar_svg(
            path=p1,
            title="CarOS-A2X Ablation: Intervention Rate",
            y_label="Interventions per 1k miles",
            labels=labels,
            means=intrv_mean,
            stds=intrv_std,
        )
        save_bar_svg(
            path=p2,
            title="CarOS-A2X Ablation: Mission Success",
            y_label="Mission success (%)",
            labels=labels,
            means=mission_mean,
            stds=mission_std,
        )
        print(f"Matplotlib unavailable ({e}); exported SVG plots instead.")
        print(f"Plot exported: {p1}")
        print(f"Plot exported: {p2}")
        return

    # Plot 1: Intervention rate
    fig1, ax1 = plt.subplots(figsize=(10.5, 5.5))
    ax1.bar(range(len(labels)), intrv_mean, yerr=intrv_std, capsize=5)
    ax1.set_xticks(range(len(labels)))
    ax1.set_xticklabels(labels, rotation=15, ha="right")
    ax1.set_ylabel("Interventions per 1k miles")
    ax1.set_title("CarOS-A2X Ablation: Intervention Rate")
    ax1.grid(axis="y", linestyle="--", alpha=0.35)
    fig1.tight_layout()
    p1 = os.path.join(args.outdir, "ablation_interventions.png")
    fig1.savefig(p1, dpi=300)
    plt.close(fig1)

    # Plot 2: Mission success
    fig2, ax2 = plt.subplots(figsize=(10.5, 5.5))
    ax2.bar(range(len(labels)), mission_mean, yerr=mission_std, capsize=5)
    ax2.set_xticks(range(len(labels)))
    ax2.set_xticklabels(labels, rotation=15, ha="right")
    ax2.set_ylabel("Mission success (%)")
    ax2.set_title("CarOS-A2X Ablation: Mission Success")
    ax2.grid(axis="y", linestyle="--", alpha=0.35)
    fig2.tight_layout()
    p2 = os.path.join(args.outdir, "ablation_mission_success.png")
    fig2.savefig(p2, dpi=300)
    plt.close(fig2)

    print(f"Plot exported: {p1}")
    print(f"Plot exported: {p2}")


if __name__ == "__main__":
    main()
