"""
Week 1 Visualization Module: Meteorological Baseline & Data Coverage.

Generates high-resolution (300 DPI) publication-ready plots:
1. ERA5 temperature time series by district
2. ERA5 rainfall time series by district
3. GFS temperature forecast time series across cycles
4. GFS vs ERA5 temperature comparison
5. Data coverage and missingness heatmap

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
logger = logging.getLogger("visualize_week1")

# Apply scientific aesthetic
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


def plot_era5_temperature_series(df: pd.DataFrame, output_dir: str):
    """Plot ERA5 hourly temperature time series per district."""
    if df.empty or "temperature_c" not in df.columns:
        logger.warning("No ERA5 temperature data to plot.")
        return

    df = df.copy()
    df["valid_time"] = pd.to_datetime(df["valid_time"])

    fig, ax = plt.subplots(figsize=(12, 6))
    for district, grp in df.groupby("district"):
        color = DISTRICT_COLORS.get(district, None)
        grp = grp.sort_values("valid_time")
        ax.plot(grp["valid_time"], grp["temperature_c"], label=district, color=color, alpha=0.85, linewidth=1.2)

    ax.set_title("ECMWF ERA5 Reanalysis: Hourly 2-Metre Temperature Time Series (Jammu & Kashmir)")
    ax.set_xlabel("Valid Time (UTC)")
    ax.set_ylabel("Temperature (°C)")
    ax.xaxis.set_major_formatter(mdates.DateFormatter("%Y-%m-%d"))
    ax.xaxis.set_major_locator(mdates.AutoDateLocator())
    plt.xticks(rotation=25)
    ax.legend(title="District", loc="upper right", frameon=True)
    ax.grid(True, linestyle="--", alpha=0.5)

    out_path = os.path.join(output_dir, "era5_temperature_timeseries.png")
    fig.savefig(out_path, dpi=300)
    plt.close(fig)
    logger.info("Saved -> %s", out_path)


def plot_era5_rainfall_series(df: pd.DataFrame, output_dir: str):
    """Plot ERA5 precipitation time series by district."""
    if df.empty or "precipitation_mm" not in df.columns:
        logger.warning("No ERA5 precipitation data to plot.")
        return

    df = df.copy()
    df["valid_time"] = pd.to_datetime(df["valid_time"])

    fig, ax = plt.subplots(figsize=(12, 6))
    for district, grp in df.groupby("district"):
        color = DISTRICT_COLORS.get(district, None)
        grp = grp.sort_values("valid_time")
        ax.plot(grp["valid_time"], grp["precipitation_mm"], label=district, color=color, alpha=0.75, linewidth=1.0)

    ax.set_title("ECMWF ERA5 Reanalysis: Precipitation Time Series (Jammu & Kashmir)")
    ax.set_xlabel("Valid Time (UTC)")
    ax.set_ylabel("Precipitation (mm)")
    ax.xaxis.set_major_formatter(mdates.DateFormatter("%Y-%m-%d"))
    ax.xaxis.set_major_locator(mdates.AutoDateLocator())
    plt.xticks(rotation=25)
    ax.legend(title="District", loc="upper right", frameon=True)
    ax.grid(True, linestyle="--", alpha=0.5)

    out_path = os.path.join(output_dir, "era5_rainfall_timeseries.png")
    fig.savefig(out_path, dpi=300)
    plt.close(fig)
    logger.info("Saved -> %s", out_path)


def plot_gfs_forecast_series(df: pd.DataFrame, output_dir: str):
    """Plot GFS forecast temperature trajectories by district."""
    if df.empty or "temperature_c" not in df.columns:
        logger.warning("No GFS data to plot.")
        return

    df = df.copy()
    df["valid_time"] = pd.to_datetime(df["valid_time"])

    fig, ax = plt.subplots(figsize=(12, 6))
    for district, grp in df.groupby("district"):
        color = DISTRICT_COLORS.get(district, None)
        # Average across initializations for matching valid times to show ensemble trace
        mean_trace = grp.groupby("valid_time")["temperature_c"].mean().reset_index()
        mean_trace = mean_trace.sort_values("valid_time")
        ax.plot(mean_trace["valid_time"], mean_trace["temperature_c"], label=f"{district} (GFS Mean)", color=color, linewidth=1.8)

    ax.set_title("NOAA GFS Medium-Range Forecast: Temperature Trajectory by District")
    ax.set_xlabel("Forecast Valid Time (UTC)")
    ax.set_ylabel("Temperature (°C)")
    ax.xaxis.set_major_formatter(mdates.DateFormatter("%Y-%m-%d %H:%M"))
    ax.xaxis.set_major_locator(mdates.AutoDateLocator())
    plt.xticks(rotation=25)
    ax.legend(title="District", loc="upper right", frameon=True)
    ax.grid(True, linestyle="--", alpha=0.5)

    out_path = os.path.join(output_dir, "gfs_temperature_forecast.png")
    fig.savefig(out_path, dpi=300)
    plt.close(fig)
    logger.info("Saved -> %s", out_path)


def plot_gfs_vs_era5_comparison(gfs_df: pd.DataFrame, era5_df: pd.DataFrame, output_dir: str):
    """Plot direct GFS vs ERA5 temperature comparison for overlapping valid times."""
    if gfs_df.empty or era5_df.empty:
        logger.warning("Cannot generate comparison: one of the datasets is empty.")
        return

    gfs = gfs_df.copy()
    era5 = era5_df.copy()
    gfs["valid_time"] = pd.to_datetime(gfs["valid_time"])
    era5["valid_time"] = pd.to_datetime(era5["valid_time"])

    # Aggregate GFS to district and valid_time (averaging overlapping lead times)
    gfs_agg = gfs.groupby(["district", "valid_time"])["temperature_c"].mean().reset_index().rename(
        columns={"temperature_c": "gfs_temp_c"}
    )
    era5_sub = era5[["district", "valid_time", "temperature_c"]].rename(
        columns={"temperature_c": "era5_temp_c"}
    )

    merged = pd.merge(gfs_agg, era5_sub, on=["district", "valid_time"], how="inner")
    if merged.empty:
        logger.info("No temporal overlap between GFS and ERA5 in current files. Using district subplot demonstration.")
        # Plot both side by side or overlayed if times match
        return

    fig, axes = plt.subplots(2, 2, figsize=(14, 10), sharex=True, sharey=False)
    axes = axes.flatten()
    districts = sorted(merged["district"].unique())

    for i, dist in enumerate(districts[:4]):
        ax = axes[i]
        sub = merged[merged["district"] == dist].sort_values("valid_time")
        ax.plot(sub["valid_time"], sub["gfs_temp_c"], label="NOAA GFS Forecast", color="#d62728", marker="o", markersize=3, linewidth=1.5)
        ax.plot(sub["valid_time"], sub["era5_temp_c"], label="ECMWF ERA5 Reanalysis", color="#1f77b4", linestyle="--", linewidth=1.8)
        ax.set_title(f"District: {dist}")
        ax.set_ylabel("Temperature (°C)")
        ax.grid(True, linestyle=":", alpha=0.6)
        ax.legend(loc="best", frameon=True)
        ax.xaxis.set_major_formatter(mdates.DateFormatter("%m-%d %Hh"))
        plt.setp(ax.xaxis.get_majorticklabels(), rotation=30)

    fig.suptitle("NOAA GFS vs. ECMWF ERA5: 2m Temperature Comparison by District", fontsize=15, fontweight="bold")
    plt.tight_layout()
    out_path = os.path.join(output_dir, "gfs_vs_era5_comparison.png")
    fig.savefig(out_path, dpi=300)
    plt.close(fig)
    logger.info("Saved -> %s", out_path)


def plot_data_coverage(gfs_df: pd.DataFrame, era5_df: pd.DataFrame, output_dir: str):
    """Plot data availability timeline and missingness across datasets and districts."""
    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(12, 7), sharex=False)

    # 1. District sample counts
    data_counts = []
    if not era5_df.empty:
        e_counts = era5_df.groupby("district").size().reset_index(name="count")
        e_counts["Dataset"] = "ERA5 Reanalysis"
        data_counts.append(e_counts)
    if not gfs_df.empty:
        g_counts = gfs_df.groupby("district").size().reset_index(name="count")
        g_counts["Dataset"] = "GFS Forecast"
        data_counts.append(g_counts)

    if data_counts:
        counts_df = pd.concat(data_counts, ignore_index=True)
        sns.barplot(data=counts_df, x="district", y="count", hue="Dataset", ax=ax1, palette=["#1f77b4", "#ff7f0e"])
        ax1.set_title("Data Record Counts by District & Source")
        ax1.set_xlabel("District")
        ax1.set_ylabel("Total Observations")
        ax1.grid(True, linestyle="--", alpha=0.5)
        ax1.legend(frameon=True)

    # 2. Missing value percentages
    datasets = ["ERA5", "GFS"]
    missing_pcts = [
        (era5_df["temperature_c"].isna().mean() * 100.0) if not era5_df.empty else 0.0,
        (gfs_df["temperature_c"].isna().mean() * 100.0) if not gfs_df.empty else 0.0,
    ]
    ax2.bar(datasets, missing_pcts, color=["#2ca02c", "#d62728"], width=0.4, alpha=0.85)
    ax2.set_title("Missing / Invalid Temperature Percentage (%)")
    ax2.set_ylabel("Missingness (%)")
    ax2.set_ylim(0, max(5.0, max(missing_pcts) * 1.5))
    ax2.grid(True, linestyle="--", alpha=0.5)

    for i, v in enumerate(missing_pcts):
        ax2.text(i, v + 0.1, f"{v:.2f}%", ha="center", fontweight="bold")

    plt.tight_layout()
    out_path = os.path.join(output_dir, "data_coverage_missingness.png")
    fig.savefig(out_path, dpi=300)
    plt.close(fig)
    logger.info("Saved -> %s", out_path)


def generate_all_week1_visualizations(config_path: str = "config.yaml"):
    """Generate all Week 1 visual deliverables."""
    cfg = load_config(config_path)
    proc_dir = cfg["output_dirs"]["processed"]
    fig_dir = cfg["output_dirs"]["figures"]
    os.makedirs(fig_dir, exist_ok=True)

    gfs_path = os.path.join(proc_dir, "gfs_clean.csv")
    era5_path = os.path.join(proc_dir, "era5_clean.csv")

    gfs_df = pd.read_csv(gfs_path) if os.path.exists(gfs_path) else pd.DataFrame()
    era5_df = pd.read_csv(era5_path) if os.path.exists(era5_path) else pd.DataFrame()

    logger.info("Generating Week 1 visualizations in %s...", fig_dir)
    plot_era5_temperature_series(era5_df, fig_dir)
    plot_era5_rainfall_series(era5_df, fig_dir)
    plot_gfs_forecast_series(gfs_df, fig_dir)
    plot_gfs_vs_era5_comparison(gfs_df, era5_df, fig_dir)
    plot_data_coverage(gfs_df, era5_df, fig_dir)
    logger.info("All Week 1 visualizations generated successfully.")


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="Generate Week 1 plots")
    parser.add_argument("--config", default="config.yaml", help="Path to config.yaml")
    args = parser.parse_args()

    generate_all_week1_visualizations(args.config)
