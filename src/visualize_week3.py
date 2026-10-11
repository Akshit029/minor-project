"""
Week 3 Visualizations Module: Forecast Error Analysis & Bias Correction.

Generates publication-quality (300 DPI) visualizations:
1. MAE vs Lead Day (District Comparison)
2. RMSE vs Lead Day
3. Forecast Bias vs Lead Day
4. District-wise Signed Error Distributions (Boxplots)
5. District-wise Absolute Error Distributions
6. Before vs After Bias-Correction Comparison
7. GFS Forecast vs ERA5 Reference Scatterplot with 1:1 Reference Line

Outputs saved to outputs/week3/figures/
"""

import os
import logging
from typing import Optional
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import yaml

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s"
)
logger = logging.getLogger("visualize_week3")

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


def plot_metric_vs_lead_day(
    dist_lead_df: pd.DataFrame,
    lead_df: pd.DataFrame,
    metric: str,
    unit: str,
    title: str,
    out_path: str
):
    """Plot metric (MAE, RMSE, Bias) versus lead day with district comparison and regional mean."""
    fig, ax = plt.subplots(figsize=(10, 6), dpi=300)

    # Plot district lines
    if not dist_lead_df.empty and metric in dist_lead_df.columns:
        for dist, grp in dist_lead_df.groupby("district"):
            color = DISTRICT_COLORS.get(dist, None)
            ax.plot(
                grp["lead_day"], grp[metric],
                marker="o", linewidth=2.2, label=dist, color=color, markersize=7
            )

    # Plot regional aggregate line
    if not lead_df.empty and metric in lead_df.columns:
        ax.plot(
            lead_df["lead_day"], lead_df[metric],
            marker="s", linestyle="--", color="#111111", linewidth=2.5,
            label="Regional Mean (All Districts)", markersize=8
        )

    if metric == "Bias":
        ax.axhline(0, color="gray", linestyle=":", linewidth=1.5, alpha=0.8, label="Zero Bias (Ideal)")

    ax.set_title(title, pad=12)
    ax.set_xlabel("Forecast Lead Day")
    ax.set_ylabel(f"{metric} ({unit})")
    ax.set_xticks(sorted(lead_df["lead_day"].unique()) if not lead_df.empty else [1])
    ax.grid(True, linestyle="--", alpha=0.6)
    ax.legend(frameon=True, facecolor="white", edgecolor="none", loc="best")

    os.makedirs(os.path.dirname(out_path), exist_ok=True)
    plt.savefig(out_path, dpi=300)
    plt.close(fig)
    logger.info("Saved -> %s", out_path)


def plot_district_error_boxplots(matched_df: pd.DataFrame, out_path: str):
    """Plot district-wise signed error distributions (forecast - reference) using boxplots with scatter overlay."""
    fig, ax = plt.subplots(figsize=(9, 6), dpi=300)

    districts = sorted(matched_df["district"].unique())
    palette = [DISTRICT_COLORS.get(d, "#333333") for d in districts]

    sns.boxplot(
        data=matched_df, x="district", y="error", hue="district", legend=False,
        palette=palette, ax=ax, width=0.45, showcaps=True, boxprops=dict(alpha=0.85)
    )
    sns.stripplot(
        data=matched_df, x="district", y="error",
        color="black", alpha=0.4, size=5, jitter=0.15, ax=ax
    )

    ax.axhline(0, color="crimson", linestyle="--", linewidth=1.5, alpha=0.8, label="Zero Bias Baseline")
    ax.set_title("Forecast Signed Error Distribution by District (GFS - ERA5)", pad=12)
    ax.set_xlabel("Target District (Jammu & Kashmir)")
    ax.set_ylabel("Signed Temperature Error (°C)")
    ax.grid(True, linestyle="--", alpha=0.6)
    ax.legend(loc="upper right")

    os.makedirs(os.path.dirname(out_path), exist_ok=True)
    plt.savefig(out_path, dpi=300)
    plt.close(fig)
    logger.info("Saved -> %s", out_path)


def plot_district_abs_error_boxplots(matched_df: pd.DataFrame, out_path: str):
    """Plot district-wise absolute error distributions."""
    fig, ax = plt.subplots(figsize=(9, 6), dpi=300)

    districts = sorted(matched_df["district"].unique())
    palette = [DISTRICT_COLORS.get(d, "#333333") for d in districts]

    sns.boxplot(
        data=matched_df, x="district", y="absolute_error", hue="district", legend=False,
        palette=palette, ax=ax, width=0.45, showcaps=True, boxprops=dict(alpha=0.85)
    )
    sns.stripplot(
        data=matched_df, x="district", y="absolute_error",
        color="black", alpha=0.4, size=5, jitter=0.15, ax=ax
    )

    ax.set_title("Forecast Absolute Error Distribution by District (|GFS - ERA5|)", pad=12)
    ax.set_xlabel("Target District (Jammu & Kashmir)")
    ax.set_ylabel("Absolute Temperature Error (°C)")
    ax.grid(True, linestyle="--", alpha=0.6)

    os.makedirs(os.path.dirname(out_path), exist_ok=True)
    plt.savefig(out_path, dpi=300)
    plt.close(fig)
    logger.info("Saved -> %s", out_path)


def plot_bias_correction_comparison(test_eval_df: pd.DataFrame, out_path: str):
    """Bar chart comparing MAE, RMSE, and Bias before and after bias correction on held-out test data."""
    fig, ax = plt.subplots(figsize=(8, 5.5), dpi=300)

    metrics = ["MAE", "RMSE", "Bias"]
    x = np.arange(len(metrics))
    width = 0.35

    # Robust stage matching
    raw_sub = test_eval_df[test_eval_df["stage"].str.contains("Uncorrected", case=False, na=False)]
    corr_sub = test_eval_df[test_eval_df["stage"].str.contains("Corrected", case=False, na=False)]

    if raw_sub.empty or corr_sub.empty:
        logger.warning("Could not find both Uncorrected and Corrected stages in test_eval_df. Skipping comparison plot.")
        plt.close(fig)
        return

    raw_vals = [float(raw_sub[m].iloc[0]) for m in metrics]
    corr_vals = [float(corr_sub[m].iloc[0]) for m in metrics]

    label_raw = raw_sub["stage"].iloc[0]
    label_corr = corr_sub["stage"].iloc[0]

    rects1 = ax.bar(x - width/2, raw_vals, width, label=label_raw, color="#d95f02", alpha=0.9)
    rects2 = ax.bar(x + width/2, corr_vals, width, label=label_corr, color="#1b9e77", alpha=0.9)

    ax.set_title("Held-Out Verification: Before vs After Bias Correction", pad=12)
    ax.set_ylabel("Error Metric (°C)")
    ax.set_xticks(x)
    ax.set_xticklabels(metrics, fontweight="semibold")
    ax.axhline(0, color="gray", linestyle=":", linewidth=1.2)
    ax.grid(True, linestyle="--", alpha=0.6)
    ax.legend(frameon=True, facecolor="white", edgecolor="none")

    # Add value labels
    for rect in list(rects1) + list(rects2):
        height = rect.get_height()
        va = "bottom" if height >= 0 else "top"
        ax.annotate(f"{height:.2f}",
                    xy=(rect.get_x() + rect.get_width() / 2, height),
                    xytext=(0, 3 if height >= 0 else -8),
                    textcoords="offset points",
                    ha="center", va=va, fontsize=9, fontweight="bold")

    os.makedirs(os.path.dirname(out_path), exist_ok=True)
    plt.savefig(out_path, dpi=300)
    plt.close(fig)
    logger.info("Saved -> %s", out_path)


def plot_forecast_vs_reference_scatter(matched_df: pd.DataFrame, out_path: str):
    """Scatterplot of GFS Forecast vs ERA5 Reference with 1:1 line."""
    fig, ax = plt.subplots(figsize=(8, 8), dpi=300)

    districts = sorted(matched_df["district"].unique())
    for dist in districts:
        sub = matched_df[matched_df["district"] == dist]
        color = DISTRICT_COLORS.get(dist, None)
        ax.scatter(
            sub["reference_value"], sub["forecast_value"],
            color=color, label=dist, alpha=0.75, s=60, edgecolors="white", linewidth=0.5
        )

    # 1:1 line
    min_val = min(matched_df["reference_value"].min(), matched_df["forecast_value"].min()) - 2
    max_val = max(matched_df["reference_value"].max(), matched_df["forecast_value"].max()) + 2
    ax.plot([min_val, max_val], [min_val, max_val], "k--", linewidth=1.8, label="1:1 Perfect Verification Line")

    ax.set_xlim(min_val, max_val)
    ax.set_ylim(min_val, max_val)
    ax.set_title("GFS 2m Temperature Forecast vs ECMWF ERA5 Reanalysis Reference", pad=12)
    ax.set_xlabel("ERA5 Reanalysis Reference Temperature (°C)")
    ax.set_ylabel("GFS Forecast Temperature (°C)")
    ax.grid(True, linestyle="--", alpha=0.6)
    ax.legend(frameon=True, facecolor="white", edgecolor="none", loc="upper left")

    os.makedirs(os.path.dirname(out_path), exist_ok=True)
    plt.savefig(out_path, dpi=300)
    plt.close(fig)
    logger.info("Saved -> %s", out_path)


def generate_all_week3_visualizations(config_path: str = "config.yaml"):
    """Generate all Week 3 figures from pipeline outputs."""
    cfg = load_config(config_path)
    w3_dir = cfg["output_dirs"].get("week3", "outputs/week3")
    fig_dir = cfg["output_dirs"].get("week3_figures", "outputs/week3/figures")
    os.makedirs(fig_dir, exist_ok=True)

    matched_path = os.path.join(w3_dir, "matched_validation_dataset.csv")
    lead_path = os.path.join(w3_dir, "lead_day_metrics.csv")
    dist_lead_path = os.path.join(w3_dir, "district_lead_metrics.csv")
    eval_path = os.path.join(w3_dir, "bias_correction_eval.csv")

    if not os.path.exists(matched_path) or not os.path.exists(lead_path):
        logger.warning("Week 3 CSV outputs missing. Skipping Week 3 visualizations.")
        return

    matched_df = pd.read_csv(matched_path)
    lead_df = pd.read_csv(lead_path)
    dist_lead_df = pd.read_csv(dist_lead_path) if os.path.exists(dist_lead_path) else pd.DataFrame()
    eval_df = pd.read_csv(eval_path) if os.path.exists(eval_path) else pd.DataFrame()

    logger.info("Generating Week 3 visualizations into %s...", fig_dir)

    # 1. MAE vs Lead Day
    plot_metric_vs_lead_day(
        dist_lead_df, lead_df, "MAE", "°C",
        "Forecast Mean Absolute Error (MAE) vs Lead Day across Districts",
        os.path.join(fig_dir, "mae_vs_lead_day.png")
    )

    # 2. RMSE vs Lead Day
    plot_metric_vs_lead_day(
        dist_lead_df, lead_df, "RMSE", "°C",
        "Forecast Root Mean Squared Error (RMSE) vs Lead Day across Districts",
        os.path.join(fig_dir, "rmse_vs_lead_day.png")
    )

    # 3. Bias vs Lead Day
    plot_metric_vs_lead_day(
        dist_lead_df, lead_df, "Bias", "°C",
        "Forecast Mean Bias Error vs Lead Day across Districts (GFS - ERA5)",
        os.path.join(fig_dir, "bias_vs_lead_day.png")
    )

    # 4. District Signed Error Boxplots
    plot_district_error_boxplots(matched_df, os.path.join(fig_dir, "district_error_distribution.png"))

    # 5. District Absolute Error Boxplots
    plot_district_abs_error_boxplots(matched_df, os.path.join(fig_dir, "district_abs_error_distribution.png"))

    # 6. Bias Correction Comparison
    if not eval_df.empty:
        plot_bias_correction_comparison(eval_df, os.path.join(fig_dir, "bias_correction_comparison.png"))

    # 7. Scatterplot with 1:1 line
    plot_forecast_vs_reference_scatter(matched_df, os.path.join(fig_dir, "forecast_vs_reference_scatter.png"))

    logger.info("Week 3 visualizations successfully generated.")


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="Generate Week 3 Visualizations")
    parser.add_argument("--config", default="config.yaml", help="Path to config.yaml")
    args = parser.parse_args()

    generate_all_week3_visualizations(args.config)
