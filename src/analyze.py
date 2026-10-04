from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd


ROOT = Path(__file__).resolve().parents[1]
RAW_DIR = ROOT / "data" / "raw"
PROCESSED_DIR = ROOT / "data" / "processed"
FIG_DIR = ROOT / "outputs" / "figures"

PROCESSED_DIR.mkdir(parents=True, exist_ok=True)
FIG_DIR.mkdir(parents=True, exist_ok=True)


def savefig(name: str):
    plt.tight_layout()
    plt.savefig(FIG_DIR / name, dpi=180, bbox_inches="tight")
    plt.close()


def load_data():
    results = pd.read_csv(RAW_DIR / "race_results_2024.csv")
    laps = pd.read_csv(RAW_DIR / "race_laps_2024.csv")

    laps["LapTime"] = pd.to_timedelta(laps["LapTime"], errors="coerce")
    laps["LapTimeSeconds"] = laps["LapTime"].dt.total_seconds()

    return results, laps


def clean_laps(laps: pd.DataFrame) -> pd.DataFrame:
    df = laps.copy()

    # Valid timed laps only.
    df = df.dropna(subset=["LapTimeSeconds", "Driver", "LapNumber"])

    # Extremely slow laps can be pit/in-lap/out-lap or abnormal laps.
    # For the main pace comparison, keep the middle 98% by lap time.
    low = df["LapTimeSeconds"].quantile(0.01)
    high = df["LapTimeSeconds"].quantile(0.99)
    df = df[df["LapTimeSeconds"].between(low, high)]

    return df


def analyze_average_finish(results):
    df = results.copy()
    df["Position"] = pd.to_numeric(df["Position"], errors="coerce")
    df = df.dropna(subset=["Position"])

    summary = (
        df.groupby("FullName", as_index=False)
        .agg(
            races=("Position", "count"),
            avg_finish=("Position", "mean"),
            points=("Points", "sum"),
        )
        .sort_values("avg_finish")
    )
    summary.to_csv(PROCESSED_DIR / "driver_finish_summary.csv", index=False)

    top = summary.head(15).sort_values("avg_finish", ascending=True)

    plt.figure(figsize=(10, 6))
    plt.barh(top["FullName"], top["avg_finish"])
    plt.gca().invert_yaxis()
    plt.xlabel("Average finishing position")
    plt.ylabel("Driver")
    plt.title("2024 F1: Average Finishing Position")
    savefig("01_average_finish.png")


def analyze_lap_pace(laps):
    summary = (
        laps.groupby("Driver", as_index=False)
        .agg(
            laps=("LapTimeSeconds", "count"),
            mean_lap_time=("LapTimeSeconds", "mean"),
            median_lap_time=("LapTimeSeconds", "median"),
            std_lap_time=("LapTimeSeconds", "std"),
        )
        .sort_values("mean_lap_time")
    )
    summary.to_csv(PROCESSED_DIR / "driver_lap_pace_summary.csv", index=False)

    top = summary.head(15).sort_values("mean_lap_time", ascending=True)

    plt.figure(figsize=(10, 6))
    plt.barh(top["Driver"], top["mean_lap_time"])
    plt.gca().invert_yaxis()
    plt.xlabel("Average lap time (seconds)")
    plt.ylabel("Driver")
    plt.title("2024 F1: Average Recorded Lap Time")
    savefig("02_average_lap_time.png")


def analyze_consistency(laps):
    summary = (
        laps.groupby("Driver", as_index=False)
        .agg(
            laps=("LapTimeSeconds", "count"),
            mean_lap_time=("LapTimeSeconds", "mean"),
            lap_time_std=("LapTimeSeconds", "std"),
        )
        .sort_values("lap_time_std")
    )
    summary.to_csv(PROCESSED_DIR / "driver_consistency_summary.csv", index=False)

    top = summary.head(15).sort_values("lap_time_std", ascending=True)

    plt.figure(figsize=(10, 6))
    plt.barh(top["Driver"], top["lap_time_std"])
    plt.gca().invert_yaxis()
    plt.xlabel("Lap-time standard deviation (seconds)")
    plt.ylabel("Driver")
    plt.title("2024 F1: Lap-Time Consistency")
    savefig("03_lap_time_consistency.png")


def analyze_tyres(laps):
    if "Compound" not in laps.columns:
        return

    tyre_counts = (
        laps["Compound"]
        .dropna()
        .value_counts()
        .rename_axis("Compound")
        .reset_index(name="LapCount")
    )
    tyre_counts.to_csv(PROCESSED_DIR / "tyre_usage_summary.csv", index=False)

    plt.figure(figsize=(8, 5))
    plt.bar(tyre_counts["Compound"], tyre_counts["LapCount"])
    plt.xlabel("Tyre compound")
    plt.ylabel("Number of recorded laps")
    plt.title("2024 F1: Recorded Lap Count by Tyre Compound")
    savefig("04_tyre_usage.png")


def analyze_points(results):
    df = results.copy()
    df["Points"] = pd.to_numeric(df["Points"], errors="coerce").fillna(0)

    summary = (
        df.groupby("FullName", as_index=False)
        .agg(points=("Points", "sum"))
        .sort_values("points", ascending=False)
        .head(15)
    )
    summary.to_csv(PROCESSED_DIR / "driver_points_summary.csv", index=False)

    plot_df = summary.sort_values("points", ascending=True)

    plt.figure(figsize=(10, 6))
    plt.barh(plot_df["FullName"], plot_df["points"])
    plt.xlabel("Championship points")
    plt.ylabel("Driver")
    plt.title("2024 F1: Championship Points")
    savefig("05_driver_points.png")


def main():
    results, laps = load_data()
    laps = clean_laps(laps)

    print(f"Race-result rows: {len(results):,}")
    print(f"Clean lap rows:    {len(laps):,}")

    analyze_average_finish(results)
    analyze_lap_pace(laps)
    analyze_consistency(laps)
    analyze_tyres(laps)
    analyze_points(results)

    print("\nAnalysis complete.")
    print(f"Figures: {FIG_DIR}")
    print(f"Tables:  {PROCESSED_DIR}")


if __name__ == "__main__":
    main()
