"""
Week 4 Visualizations Module: Reliability Scoring & Spatiotemporal Analysis.

Generates publication-quality (300 DPI) plots:
1. Reliability Score vs Lead Day (by District & Regional Mean)
2. District-wise Reliability Comparison (Bar Chart)
3. District x Lead Day Reliability Heatmap
4. Sensitivity Analysis: Reliability Score vs Error Tolerance Scale
5. Sensitivity Analysis: Reliability Score vs Confidence Parameter k

Outputs saved to outputs/week4/figures/
"""

import os
import logging
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import yaml

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s"
)
logger = logging.getLogger("visualize_week4")

plt.style.use("seaborn-v0_8-whitegrid" if "seaborn-v0_8-whitegrid" in plt.style.available else "default")
plt.rcParams.update({
    "font.sans-serif": "DejaVu Sans",
    "font.size": 11,
    "axes.titlesize": 13,
    "axes.titleweight": "bold",
    "axes.labelsize": 11,
    "axes.labelweight": "semibold",
    "xtick.labelsize": 10,
    "ytick.labelsize": 10,
    "figure.titlesize": 14,
    "figure.titleweight": "bold",
    "legend.fontsize": 10,
    "figure.autolayout": True,
})

DISTRICT_COLORS = {
    "Srinagar": "#1f77b4",  # Steel Blue
    "Jammu": "#d62728",     # Crimson
    "Anantnag": "#2ca02c",  # Forest Green
    "Baramulla": "#ff7f0e", # Amber Orange
}


def load_config(config_path: str = "config.yaml") -> dict:
    with open(config_path, "r", encoding="utf-8") as f:
        return yaml.safe_load(f)


def plot_reliability_vs_lead_day(rel_df: pd.DataFrame, out_path: str):
    """Plot reliability score R vs lead day across target districts."""
    fig, ax = plt.subplots(figsize=(9, 5.5), dpi=300)

    for dist, grp in rel_df.groupby("district"):
        color = DISTRICT_COLORS.get(dist, None)
        ax.plot(
            grp["lead_day"], grp["reliability_score_R"],
            marker="o", linewidth=2.2, label=dist, color=color, markersize=7
        )

    # Regional average
    mean_by_lead = rel_df.groupby("lead_day")["reliability_score_R"].mean().reset_index()
    ax.plot(
        mean_by_lead["lead_day"], mean_by_lead["reliability_score_R"],
        marker="s", linestyle="--", color="#111111", linewidth=2.5,
        label="Regional Mean (All Districts)", markersize=8
    )

    ax.set_title("Empirical Forecast Reliability Score (R) vs Lead Day", pad=12)
    ax.set_xlabel("Forecast Lead Day")
    ax.set_ylabel("Reliability Index R ∈ [0, 1]")
    ax.set_ylim(-0.05, 1.05)
    ax.set_xticks(sorted(rel_df["lead_day"].unique()))
    ax.grid(True, linestyle="--", alpha=0.6)
    ax.legend(frameon=True, facecolor="white", edgecolor="none", loc="best")

    os.makedirs(os.path.dirname(out_path), exist_ok=True)
    plt.savefig(out_path, dpi=300)
    plt.close(fig)
    logger.info("Saved -> %s", out_path)


def plot_district_reliability_bar(rel_df: pd.DataFrame, out_path: str):
    """Bar chart comparing overall reliability across districts."""
    fig, ax = plt.subplots(figsize=(8, 5), dpi=300)

    dist_means = rel_df.groupby("district")["reliability_score_R"].mean().reset_index()
    dist_means = dist_means.sort_values("reliability_score_R", ascending=False)

    colors = [DISTRICT_COLORS.get(d, "#333333") for d in dist_means["district"]]
    bars = ax.bar(dist_means["district"], dist_means["reliability_score_R"], color=colors, width=0.45, alpha=0.9)

    ax.set_title("Mean Estimated Forecast Reliability by District", pad=12)
    ax.set_xlabel("Target District (Jammu & Kashmir)")
    ax.set_ylabel("Mean Reliability Index R")
    ax.set_ylim(0, 1.05)
    ax.grid(True, linestyle="--", alpha=0.6)

    for bar in bars:
        h = bar.get_height()
        ax.annotate(f"{h:.3f}",
                    xy=(bar.get_x() + bar.get_width() / 2, h),
                    xytext=(0, 4), textcoords="offset points",
                    ha="center", va="bottom", fontweight="bold", fontsize=10)

    os.makedirs(os.path.dirname(out_path), exist_ok=True)
    plt.savefig(out_path, dpi=300)
    plt.close(fig)
    logger.info("Saved -> %s", out_path)


def plot_spatiotemporal_heatmap(rel_df: pd.DataFrame, out_path: str):
    """Heatmap of District x Lead Day reliability scores."""
    fig, ax = plt.subplots(figsize=(9, 6), dpi=300)

    pivot_table = rel_df.pivot(index="district", columns="lead_day", values="reliability_score_R")

    sns.heatmap(
        pivot_table, annot=True, fmt=".3f", cmap="YlGnBu",
        vmin=0.0, vmax=1.0, cbar_kws={"label": "Reliability Index R ∈ [0, 1]"},
        linewidths=1.0, linecolor="white", ax=ax
    )

    ax.set_title("Spatiotemporal Reliability Heatmap (District × Lead Day)", pad=14)
    ax.set_xlabel("Forecast Lead Day")
    ax.set_ylabel("District")

    os.makedirs(os.path.dirname(out_path), exist_ok=True)
    plt.savefig(out_path, dpi=300)
    plt.close(fig)
    logger.info("Saved -> %s", out_path)


def plot_sensitivity_curves(sens_df: pd.DataFrame, out_tolerance_path: str, out_k_path: str):
    """Plot sensitivity curves for error tolerance scale and confidence parameter k."""
    if sens_df.empty:
        return

    # 1. Sensitivity vs Error Tolerance Scale (fixed k=10)
    sub_k10 = sens_df[sens_df["k_value"] == 10.0]
    if not sub_k10.empty:
        fig, ax = plt.subplots(figsize=(8, 5.5), dpi=300)
        for escale, grp in sub_k10.groupby("error_scale"):
            ax.plot(
                grp["lead_day"], grp["reliability_score_R"],
                marker="o", linewidth=2.0, label=f"Tolerance = {escale:.1f} °C"
            )
        ax.set_title("Sensitivity Analysis: Reliability Score vs Error Tolerance Scale (k=10)", pad=12)
        ax.set_xlabel("Forecast Lead Day")
        ax.set_ylabel("Reliability Index R")
        ax.set_ylim(0, 1.05)
        ax.set_xticks(sorted(sub_k10["lead_day"].unique()))
        ax.grid(True, linestyle="--", alpha=0.6)
        ax.legend(frameon=True, facecolor="white", edgecolor="none")

        os.makedirs(os.path.dirname(out_tolerance_path), exist_ok=True)
        plt.savefig(out_tolerance_path, dpi=300)
        plt.close(fig)
        logger.info("Saved -> %s", out_tolerance_path)

    # 2. Sensitivity vs Confidence Parameter k (fixed tolerance=2.0)
    sub_t2 = sens_df[sens_df["error_scale"] == 2.0]
    if not sub_t2.empty:
        fig, ax = plt.subplots(figsize=(8, 5.5), dpi=300)
        for kval, grp in sub_t2.groupby("k_value"):
            ax.plot(
                grp["lead_day"], grp["reliability_score_R"],
                marker="s", linewidth=2.0, label=f"Smoothing k = {kval:.0f}"
            )
        ax.set_title("Sensitivity Analysis: Reliability Score vs Sample Smoothing Parameter k", pad=12)
        ax.set_xlabel("Forecast Lead Day")
        ax.set_ylabel("Reliability Index R")
        ax.set_ylim(0, 1.05)
        ax.set_xticks(sorted(sub_t2["lead_day"].unique()))
        ax.grid(True, linestyle="--", alpha=0.6)
        ax.legend(frameon=True, facecolor="white", edgecolor="none")

        os.makedirs(os.path.dirname(out_k_path), exist_ok=True)
        plt.savefig(out_k_path, dpi=300)
        plt.close(fig)
        logger.info("Saved -> %s", out_k_path)


def generate_all_week4_visualizations(config_path: str = "config.yaml"):
    """Generate all Week 4 figures from outputs/week4 CSVs."""
    cfg = load_config(config_path)
    w4_dir = cfg["output_dirs"].get("week4", "outputs/week4")
    fig_dir = cfg["output_dirs"].get("week4_figures", "outputs/week4/figures")
    os.makedirs(fig_dir, exist_ok=True)

    rel_path = os.path.join(w4_dir, "reliability_table.csv")
    sens_path = os.path.join(w4_dir, "sensitivity_analysis.csv")

    if not os.path.exists(rel_path):
        logger.warning("Week 4 reliability_table.csv missing. Skipping Week 4 plots.")
        return

    rel_df = pd.read_csv(rel_path)
    sens_df = pd.read_csv(sens_path) if os.path.exists(sens_path) else pd.DataFrame()

    logger.info("Generating Week 4 visualizations into %s...", fig_dir)

    plot_reliability_vs_lead_day(rel_df, os.path.join(fig_dir, "reliability_vs_lead_day.png"))
    plot_district_reliability_bar(rel_df, os.path.join(fig_dir, "district_reliability_comparison.png"))
    plot_spatiotemporal_heatmap(rel_df, os.path.join(fig_dir, "spatiotemporal_reliability_heatmap.png"))
    plot_sensitivity_curves(
        sens_df,
        os.path.join(fig_dir, "sensitivity_error_tolerance.png"),
        os.path.join(fig_dir, "sensitivity_smoothing_k.png")
    )
    logger.info("Week 4 visualizations successfully generated.")


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="Generate Week 4 Visualizations")
    parser.add_argument("--config", default="config.yaml", help="Path to config.yaml")
    args = parser.parse_args()

    generate_all_week4_visualizations(args.config)
