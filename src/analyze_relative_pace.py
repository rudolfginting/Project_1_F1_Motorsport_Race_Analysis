from pathlib import Path

import matplotlib.pyplot as plt
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
    laps = pd.read_csv(RAW_DIR / "race_laps_2024.csv")

    laps["LapTime"] = pd.to_timedelta(
        laps["LapTime"],
        errors="coerce"
    )

    laps["LapTimeSeconds"] = laps["LapTime"].dt.total_seconds()

    return laps


def clean_laps(laps):
    df = laps.copy()

    # Keep rows with the information required for the analysis.
    df = df.dropna(
        subset=[
            "EventName",
            "Driver",
            "LapNumber",
            "LapTimeSeconds",
        ]
    )

    # Remove extremely slow abnormal laps.
    low = df["LapTimeSeconds"].quantile(0.01)
    high = df["LapTimeSeconds"].quantile(0.99)

    df = df[
        df["LapTimeSeconds"].between(low, high)
    ]

    # Exclude pit entry and pit exit laps when timestamps exist.
    df = df[
        df["PitInTime"].isna()
        & df["PitOutTime"].isna()
    ]

    return df


def calculate_relative_pace(laps):
    df = laps.copy()

    # Normalize event names so that accidental spacing differences
    # do not create separate races.
    df["EventName"] = (
        df["EventName"]
        .astype(str)
        .str.replace(r"\s+", " ", regex=True)
        .str.strip()
    )

    # Convert lap number to integer.
    df["LapNumber"] = pd.to_numeric(
        df["LapNumber"],
        errors="coerce"
    )

    df = df.dropna(subset=["LapNumber"])

    df["LapNumber"] = df["LapNumber"].astype(int)

    # Calculate the median lap time for each race and lap number.
    race_lap_median = (
        df.groupby(
            ["EventName", "LapNumber"]
        )["LapTimeSeconds"]
        .median()
        .rename("RaceLapMedian")
        .reset_index()
    )

    df = df.merge(
        race_lap_median,
        on=["EventName", "LapNumber"],
        how="left",
    )

    # Difference from the median of the same race lap.
    df["RelativeLapTime"] = (
        df["LapTimeSeconds"]
        - df["RaceLapMedian"]
    )

    return df


def summarize_driver_pace(df):
    summary = (
        df.groupby("Driver", as_index=False)
        .agg(
            laps=("RelativeLapTime", "count"),
            mean_relative_pace=("RelativeLapTime", "mean"),
            median_relative_pace=("RelativeLapTime", "median"),
            std_relative_pace=("RelativeLapTime", "std"),
        )
        .sort_values("mean_relative_pace")
    )

    summary.to_csv(
        PROCESSED_DIR / "driver_relative_pace_summary.csv",
        index=False,
    )

    return summary


def plot_relative_pace(summary):
    top = (
        summary
        .head(15)
        .sort_values(
            "mean_relative_pace",
            ascending=True,
        )
    )

    plt.figure(figsize=(10, 6))

    plt.barh(
        top["Driver"],
        top["mean_relative_pace"],
    )

    plt.axvline(
        0,
        linewidth=1,
    )

    plt.xlabel(
        "Mean relative lap time (seconds)"
    )

    plt.ylabel("Driver")

    plt.title(
        "2024 F1: Race-Relative Lap Pace"
    )

    savefig(
        "06_race_relative_pace.png"
    )


def main():
    laps = load_data()

    print(
        f"Raw lap rows: {len(laps):,}"
    )

    laps = clean_laps(laps)

    print(
        f"Clean lap rows: {len(laps):,}"
    )

    relative_laps = calculate_relative_pace(
        laps
    )

    summary = summarize_driver_pace(
        relative_laps
    )

    plot_relative_pace(summary)

    print("\nAnalysis complete.")

    print(
        "\nTop relative pace:"
    )

    print(
        summary.head(15).to_string(
            index=False
        )
    )

    print(
        f"\nTable: "
        f"{PROCESSED_DIR / 'driver_relative_pace_summary.csv'}"
    )

    print(
        f"Figure: "
        f"{FIG_DIR / '06_race_relative_pace.png'}"
    )


if __name__ == "__main__":
    main()
