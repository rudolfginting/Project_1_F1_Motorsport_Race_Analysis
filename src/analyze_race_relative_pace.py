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
    plt.savefig(
        FIG_DIR / name,
        dpi=120,
    )
    plt.close()


def load_data():
    laps = pd.read_csv(
        RAW_DIR / "race_laps_2024.csv"
    )

    laps["LapTime"] = pd.to_timedelta(
        laps["LapTime"],
        errors="coerce",
    )

    laps["LapTimeSeconds"] = (
        laps["LapTime"].dt.total_seconds()
    )

    return laps


def clean_laps(laps):
    df = laps.copy()

    df = df.dropna(
        subset=[
            "EventName",
            "Driver",
            "LapNumber",
            "LapTimeSeconds",
        ]
    )

    # Normalize race names.
    df["EventName"] = (
        df["EventName"]
        .astype(str)
        .str.replace(
            r"\s+",
            " ",
            regex=True,
        )
        .str.strip()
    )

    # Convert lap number to integer.
    df["LapNumber"] = pd.to_numeric(
        df["LapNumber"],
        errors="coerce",
    )

    df = df.dropna(
        subset=["LapNumber"]
    )

    df["LapNumber"] = (
        df["LapNumber"].astype(int)
    )

    # Remove extreme lap times.
    low = df["LapTimeSeconds"].quantile(0.01)
    high = df["LapTimeSeconds"].quantile(0.99)

    df = df[
        df["LapTimeSeconds"].between(
            low,
            high,
        )
    ]

    # Remove pit entry / exit laps.
    df = df[
        df["PitInTime"].isna()
        & df["PitOutTime"].isna()
    ]

    return df


def calculate_relative_pace(laps):
    df = laps.copy()

    race_lap_median = (
        df.groupby(
            [
                "EventName",
                "LapNumber",
            ]
        )["LapTimeSeconds"]
        .median()
        .rename("RaceLapMedian")
        .reset_index()
    )

    df = df.merge(
        race_lap_median,
        on=[
            "EventName",
            "LapNumber",
        ],
        how="left",
    )

    df["RelativeLapTime"] = (
        df["LapTimeSeconds"]
        - df["RaceLapMedian"]
    )

    return df


def summarize_by_race(df):
    summary = (
        df.groupby(
            [
                "EventName",
                "Driver",
            ],
            as_index=False,
        )
        .agg(
            laps=(
                "RelativeLapTime",
                "count",
            ),
            mean_relative_pace=(
                "RelativeLapTime",
                "mean",
            ),
            median_relative_pace=(
                "RelativeLapTime",
                "median",
            ),
        )
    )

    summary.to_csv(
        PROCESSED_DIR
        / "race_driver_relative_pace.csv",
        index=False,
    )

    return summary


def create_driver_race_matrix(summary):
    matrix = summary.pivot(
        index="EventName",
        columns="Driver",
        values="mean_relative_pace",
    )

    matrix.to_csv(
        PROCESSED_DIR
        / "race_relative_pace_matrix.csv"
    )

    return matrix


def plot_race_relative_pace(summary):
    # Select drivers with substantial data.
    driver_counts = (
        summary.groupby("Driver")["laps"]
        .sum()
        .sort_values(ascending=False)
    )

    top_drivers = driver_counts.head(8).index

    plot_df = summary[
        summary["Driver"].isin(top_drivers)
    ]

    plt.figure(figsize=(10, 6))

    for driver in top_drivers:
        driver_data = plot_df[
            plot_df["Driver"] == driver
        ]

        plt.plot(
            driver_data["EventName"],
            driver_data["mean_relative_pace"],
            marker="o",
            label=driver,
        )

    plt.axhline(
        0,
        linewidth=1,
    )

    plt.xlabel("Grand Prix")
    plt.ylabel(
        "Mean relative lap time (seconds)"
    )

    plt.title(
        "2024 F1: Race-by-Race Relative Pace"
    )

    plt.xticks(
        rotation=60,
        ha="right",
    )

    plt.legend()

    plt.tight_layout()

    savefig(
        "07_race_by_race_relative_pace.png"
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

    summary = summarize_by_race(
        relative_laps
    )

    create_driver_race_matrix(
        summary
    )

    plot_race_relative_pace(
        summary
    )

    print(
        "\nAnalysis complete."
    )

    print(
        "\nRace-by-race relative pace:"
    )

    print(
        summary.head(20).to_string(
            index=False
        )
    )

    print(
        "\nFiles created:"
    )

    print(
        PROCESSED_DIR
        / "race_driver_relative_pace.csv"
    )

    print(
        PROCESSED_DIR
        / "race_relative_pace_matrix.csv"
    )

    print(
        FIG_DIR
        / "07_race_by_race_relative_pace.png"
    )


if __name__ == "__main__":
    main()