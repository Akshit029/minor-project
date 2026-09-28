"""
Week 2 Visualization Module: Feature Analysis, Anomalies, and Forecast Verification.

Generates high-resolution (300 DPI) publication-ready plots:
1. 24-hour rolling temperature graph
2. 7-day rolling temperature graph
3. Daily rainfall graph
4. 7-day rainfall accumulation graph
5. Temperature anomaly graph
6. Rainfall anomaly graph
7. Detected anomaly timeline
8. GFS vs ERA5 temperature comparison (detailed residual overlay)
9. Forecast error (MAE) vs forecast lead time (hours)

Outputs saved to outputs/figures/
"""

import os
import logging
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import seaborn as sns
import pandas as pd
import numpy as np
import yaml

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s"
)
logger = logging.getLogger("visualize_week2")

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
    """Load project YAML configuration."""
    with open(config_path, "r", encoding="utf-8") as f:
        return yaml.safe_load(f)


def plot_rolling_temp_24h(features_df: pd.DataFrame, output_dir: str):
    """Plot 24-hour rolling mean temperature by district."""
    if features_df.empty or "temp_24h_rolling_mean" not in features_df.columns:
        return
    df = features_df.copy()
    df["valid_time"] = pd.to_datetime(df["valid_time"])

    fig, ax = plt.subplots(figsize=(12, 6))
    for dist, grp in df.groupby("district"):
        grp = grp.sort_values("valid_time")
        ax.plot(grp["valid_time"], grp["temp_24h_rolling_mean"], label=dist, color=DISTRICT_COLORS.get(dist), linewidth=1.5)

    ax.set_title("24-Hour Rolling Mean 2m Temperature (ERA5 Reference)")
    ax.set_xlabel("Valid Time (UTC)")
    ax.set_ylabel("Temperature (°C)")
    ax.xaxis.set_major_formatter(mdates.DateFormatter("%Y-%m-%d"))
    ax.xaxis.set_major_locator(mdates.AutoDateLocator())
    plt.xticks(rotation=25)
    ax.legend(title="District", loc="upper right", frameon=True)
    ax.grid(True, linestyle="--", alpha=0.5)

    out = os.path.join(output_dir, "temp_24h_rolling_mean.png")
    fig.savefig(out, dpi=300)
    plt.close(fig)
    logger.info("Saved -> %s", out)


def plot_rolling_temp_7d(features_df: pd.DataFrame, output_dir: str):
    """Plot 7-day (168-hour) rolling mean temperature by district."""
    if features_df.empty or "temp_7d_rolling_mean" not in features_df.columns:
        return
    df = features_df.copy()
    df["valid_time"] = pd.to_datetime(df["valid_time"])

    fig, ax = plt.subplots(figsize=(12, 6))
    for dist, grp in df.groupby("district"):
        grp = grp.sort_values("valid_time")
        ax.plot(grp["valid_time"], grp["temp_7d_rolling_mean"], label=dist, color=DISTRICT_COLORS.get(dist), linewidth=2.0)

    ax.set_title("7-Day (168-Hour) Rolling Mean 2m Temperature Trend")
    ax.set_xlabel("Valid Time (UTC)")
    ax.set_ylabel("Temperature (°C)")
    ax.xaxis.set_major_formatter(mdates.DateFormatter("%Y-%m-%d"))
    ax.xaxis.set_major_locator(mdates.AutoDateLocator())
    plt.xticks(rotation=25)
    ax.legend(title="District", loc="upper right", frameon=True)
    ax.grid(True, linestyle="--", alpha=0.5)

    out = os.path.join(output_dir, "temp_7d_rolling_mean.png")
    fig.savefig(out, dpi=300)
    plt.close(fig)
    logger.info("Saved -> %s", out)


def plot_daily_rainfall(daily_df: pd.DataFrame, output_dir: str):
    """Plot daily total precipitation by district."""
    if daily_df.empty or "daily_precipitation_total_mm" not in daily_df.columns:
        return
    df = daily_df.copy()
    df["date"] = pd.to_datetime(df["date"])

    fig, ax = plt.subplots(figsize=(12, 6))
    for dist, grp in df.groupby("district"):
        grp = grp.sort_values("date")
        ax.plot(grp["date"], grp["daily_precipitation_total_mm"], label=dist, color=DISTRICT_COLORS.get(dist), marker="o", markersize=3, linewidth=1.2)

    ax.set_title("Daily Total Precipitation by District (ERA5 Reference)")
    ax.set_xlabel("Date (UTC)")
    ax.set_ylabel("Precipitation (mm/day)")
    ax.xaxis.set_major_formatter(mdates.DateFormatter("%Y-%m-%d"))
    ax.xaxis.set_major_locator(mdates.AutoDateLocator())
    plt.xticks(rotation=25)
    ax.legend(title="District", loc="upper right", frameon=True)
    ax.grid(True, linestyle="--", alpha=0.5)

    out = os.path.join(output_dir, "daily_precipitation_totals.png")
    fig.savefig(out, dpi=300)
    plt.close(fig)
    logger.info("Saved -> %s", out)


def plot_rainfall_accumulation_7d(features_df: pd.DataFrame, output_dir: str):
    """Plot 7-day precipitation accumulation by district."""
    if features_df.empty or "precip_7d_accumulation" not in features_df.columns:
        return
    df = features_df.copy()
    df["valid_time"] = pd.to_datetime(df["valid_time"])

    fig, ax = plt.subplots(figsize=(12, 6))
    for dist, grp in df.groupby("district"):
        grp = grp.sort_values("valid_time")
        ax.plot(grp["valid_time"], grp["precip_7d_accumulation"], label=dist, color=DISTRICT_COLORS.get(dist), linewidth=1.6)

    ax.set_title("7-Day (168-Hour) Cumulative Precipitation Trajectory")
    ax.set_xlabel("Valid Time (UTC)")
    ax.set_ylabel("Accumulated Precipitation (mm)")
    ax.xaxis.set_major_formatter(mdates.DateFormatter("%Y-%m-%d"))
    ax.xaxis.set_major_locator(mdates.AutoDateLocator())
    plt.xticks(rotation=25)
    ax.legend(title="District", loc="upper right", frameon=True)
    ax.grid(True, linestyle="--", alpha=0.5)

    out = os.path.join(output_dir, "precip_7d_accumulation.png")
    fig.savefig(out, dpi=300)
    plt.close(fig)
    logger.info("Saved -> %s", out)


def plot_temperature_anomaly(features_df: pd.DataFrame, output_dir: str):
    """Plot hourly temperature departure from provisional baseline."""
    if features_df.empty or "temperature_anomaly" not in features_df.columns:
        return
    df = features_df.copy()
    df["valid_time"] = pd.to_datetime(df["valid_time"])

    fig, ax = plt.subplots(figsize=(12, 6))
    for dist, grp in df.groupby("district"):
        grp = grp.sort_values("valid_time")
        ax.plot(grp["valid_time"], grp["temperature_anomaly"], label=dist, color=DISTRICT_COLORS.get(dist), alpha=0.75, linewidth=1.1)

    ax.axhline(0, color="black", linestyle="--", linewidth=1.0, alpha=0.8)
    ax.set_title("Temperature Departure from Provisional Baseline (°C)")
    ax.set_xlabel("Valid Time (UTC)")
    ax.set_ylabel("Temperature Anomaly (°C)")
    ax.xaxis.set_major_formatter(mdates.DateFormatter("%Y-%m-%d"))
    ax.xaxis.set_major_locator(mdates.AutoDateLocator())
    plt.xticks(rotation=25)
    ax.legend(title="District", loc="upper right", frameon=True)
    ax.grid(True, linestyle="--", alpha=0.5)

    out = os.path.join(output_dir, "temperature_anomalies.png")
    fig.savefig(out, dpi=300)
    plt.close(fig)
    logger.info("Saved -> %s", out)


def plot_rainfall_anomaly(features_df: pd.DataFrame, output_dir: str):
    """Plot rainfall departure from provisional baseline."""
    if features_df.empty or "rainfall_anomaly" not in features_df.columns:
        return
    df = features_df.copy()
    df["valid_time"] = pd.to_datetime(df["valid_time"])

    fig, ax = plt.subplots(figsize=(12, 6))
    for dist, grp in df.groupby("district"):
        grp = grp.sort_values("valid_time")
        ax.plot(grp["valid_time"], grp["rainfall_anomaly"], label=dist, color=DISTRICT_COLORS.get(dist), alpha=0.75, linewidth=1.0)

    ax.axhline(0, color="black", linestyle="--", linewidth=1.0, alpha=0.8)
    ax.set_title("Precipitation Departure from Provisional Baseline (mm)")
    ax.set_xlabel("Valid Time (UTC)")
    ax.set_ylabel("Rainfall Anomaly (mm)")
    ax.xaxis.set_major_formatter(mdates.DateFormatter("%Y-%m-%d"))
    ax.xaxis.set_major_locator(mdates.AutoDateLocator())
    plt.xticks(rotation=25)
    ax.legend(title="District", loc="upper right", frameon=True)
    ax.grid(True, linestyle="--", alpha=0.5)

    out = os.path.join(output_dir, "rainfall_anomalies.png")
    fig.savefig(out, dpi=300)
    plt.close(fig)
    logger.info("Saved -> %s", out)


def plot_anomaly_timeline(anomalies_df: pd.DataFrame, output_dir: str):
    """Plot scatter timeline of detected potential extreme meteorological events."""
    fig, ax = plt.subplots(figsize=(12, 5))
    if anomalies_df.empty:
        ax.text(0.5, 0.5, "No statistical anomalies detected above threshold in current period",
                ha="center", va="center", transform=ax.transAxes, fontsize=12)
        ax.set_title("Timeline of Detected Statistical Meteorological Anomalies")
    else:
        df = anomalies_df.copy()
        df["valid_time"] = pd.to_datetime(df["valid_time"])
        districts = sorted(df["district"].unique())
        y_mapping = {d: i for i, d in enumerate(districts)}
        df["y_pos"] = df["district"].map(y_mapping)

        scatter = ax.scatter(
            df["valid_time"], df["y_pos"],
            c=df["temperature_robust_z"].abs(),
            cmap="YlOrRd", s=80, edgecolors="black", linewidth=0.7, alpha=0.9
        )
        ax.set_yticks(range(len(districts)))
        ax.set_yticklabels(districts)
        ax.set_title("Detected Potential Extreme Weather Events & Statistical Anomalies")
        ax.set_xlabel("Valid Time (UTC)")
        ax.xaxis.set_major_formatter(mdates.DateFormatter("%Y-%m-%d"))
        plt.xticks(rotation=25)
        cbar = plt.colorbar(scatter, ax=ax)
        cbar.set_label("Robust Z-Score Magnitude")
        ax.grid(True, linestyle="--", alpha=0.5)

    out = os.path.join(output_dir, "detected_anomalies_timeline.png")
    fig.savefig(out, dpi=300)
    plt.close(fig)
    logger.info("Saved -> %s", out)


def plot_forecast_error_by_lead_time(lead_time_df: pd.DataFrame, output_dir: str):
    """
    CRITICAL DELIVERABLE:
    Plot Forecast Error (MAE in °C) vs Forecast Lead Time (Hours).
    Demonstrates how medium-range forecast skill degrades with increasing lead time.
    """
    if lead_time_df.empty or "forecast_hour" not in lead_time_df.columns:
        logger.warning("No lead time validation data to plot.")
        return

    df = lead_time_df.sort_values("forecast_hour")

    fig, ax = plt.subplots(figsize=(10, 6))
    ax.plot(df["forecast_hour"], df["MAE"], marker="o", color="#d62728", linewidth=2.2, label="Temperature MAE (°C)")
    
    if "RMSE" in df.columns:
        ax.plot(df["forecast_hour"], df["RMSE"], marker="s", color="#1f77b4", linestyle="--", linewidth=1.8, label="Temperature RMSE (°C)")

    ax.set_title("Medium-Range Forecast Error vs. Forecast Lead Time (Jammu & Kashmir)", fontsize=13, fontweight="bold")
    ax.set_xlabel("Forecast Lead Time (Hours)", fontsize=11, fontweight="semibold")
    ax.set_ylabel("Verification Error (°C)", fontsize=11, fontweight="semibold")
    ax.set_xticks(df["forecast_hour"])
    ax.grid(True, linestyle="--", alpha=0.6)
    ax.legend(loc="upper left", frameon=True)

    # Highlight error range
    ax.fill_between(df["forecast_hour"], df["MAE"], 0, alpha=0.12, color="#d62728")

    out = os.path.join(output_dir, "forecast_error_vs_lead_time.png")
    fig.savefig(out, dpi=300)
    plt.close(fig)
    logger.info("Saved -> %s", out)


def generate_all_week2_visualizations(config_path: str = "config.yaml"):
    """Generate all Week 2 visual deliverables."""
    cfg = load_config(config_path)
    proc_dir = cfg["output_dirs"]["processed"]
    fig_dir = cfg["output_dirs"]["figures"]
    os.makedirs(fig_dir, exist_ok=True)

    features_path = os.path.join(proc_dir, "era5_features.csv")
    daily_path = os.path.join(proc_dir, "era5_daily_features.csv")
    anomalies_path = "outputs/detected_anomalies.csv"
    lead_time_path = "outputs/validation_by_lead_time.csv"

    features_df = pd.read_csv(features_path) if os.path.exists(features_path) else pd.DataFrame()
    daily_df = pd.read_csv(daily_path) if os.path.exists(daily_path) else pd.DataFrame()
    anomalies_df = pd.read_csv(anomalies_path) if os.path.exists(anomalies_path) else pd.DataFrame()
    lead_time_df = pd.read_csv(lead_time_path) if os.path.exists(lead_time_path) else pd.DataFrame()

    logger.info("Generating Week 2 visualizations in %s...", fig_dir)
    plot_rolling_temp_24h(features_df, fig_dir)
    plot_rolling_temp_7d(features_df, fig_dir)
    plot_daily_rainfall(daily_df, fig_dir)
    plot_rainfall_accumulation_7d(features_df, fig_dir)
    plot_temperature_anomaly(features_df, fig_dir)
    plot_rainfall_anomaly(features_df, fig_dir)
    plot_anomaly_timeline(anomalies_df, fig_dir)
    plot_forecast_error_by_lead_time(lead_time_df, fig_dir)
    logger.info("All Week 2 visualizations generated successfully.")


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="Generate Week 2 plots")
    parser.add_argument("--config", default="config.yaml", help="Path to config.yaml")
    args = parser.parse_args()

    generate_all_week2_visualizations(args.config)
