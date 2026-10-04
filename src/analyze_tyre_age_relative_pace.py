from pathlib import Path

import matplotlib.pyplot as plt
import pandas as pd


ROOT = Path(__file__).resolve().parents[1]
RAW_DIR = ROOT / "data" / "raw"
PROCESSED_DIR = ROOT / "data" / "processed"
FIG_DIR = ROOT / "outputs" / "figures"

PROCESSED_DIR.mkdir(parents=True, exist_ok=True)
FIG_DIR.mkdir(parents=True, exist_ok=True)


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

    laps["LapNumber"] = pd.to_numeric(
        laps["LapNumber"],
        errors="coerce",
    )

    laps["TyreLife"] = pd.to_numeric(
        laps["TyreLife"],
        errors="coerce",
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
            "Compound",
            "TyreLife",
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

    df["LapNumber"] = (
        df["LapNumber"]
        .astype(int)
    )

    df["TyreLife"] = (
        df["TyreLife"]
        .astype(int)
    )

    # Keep realistic tyre ages.
    df = df[
        df["TyreLife"] > 0
    ]

    # Remove extreme lap times.
    low = df["LapTimeSeconds"].quantile(0.01)
    high = df["LapTimeSeconds"].quantile(0.99)

    df = df[
        df["LapTimeSeconds"].between(
            low,
            high,
        )
    ]

    # Exclude pit entry / exit laps.
    df = df[
        df["PitInTime"].isna()
        & df["PitOutTime"].isna()
    ]

    return df


def calculate_relative_pace(laps):
    df = laps.copy()

    # Median for each race and lap number.
    race_lap_median = (
        df.groupby(
            [
                "EventName",
                "LapNumber",
            ]
        )["LapTimeSeconds"]
        .median()
        .rename(
            "RaceLapMedian"
        )
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


def summarize_tyre_age(df):
    summary = (
        df.groupby(
            [
                "Compound",
                "TyreLife",
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
            std_relative_pace=(
                "RelativeLapTime",
                "std",
            ),
        )
    )

    # Minimum sample size.
    summary = summary[
        summary["laps"] >= 20
    ]

    summary = summary.sort_values(
        [
            "Compound",
            "TyreLife",
        ]
    )

    summary.to_csv(
        PROCESSED_DIR
        / "tyre_age_relative_pace_summary.csv",
        index=False,
    )

    return summary


def plot_tyre_age(summary):
    plt.figure(figsize=(10, 6))

    compounds = (
        summary["Compound"]
        .dropna()
        .unique()
    )

    for compound in compounds:

        data = summary[
            summary["Compound"] == compound
        ]

        plt.plot(
            data["TyreLife"],
            data["mean_relative_pace"],
            marker="o",
            label=compound,
        )

    plt.axhline(
        0,
        linewidth=1,
    )

    plt.xlabel(
        "Tyre age (laps)"
    )

    plt.ylabel(
        "Mean relative lap time (seconds)"
    )

    plt.title(
        "2024 F1: Relative Pace vs Tyre Age"
    )

    plt.legend()

    plt.tight_layout()

    plt.savefig(
        FIG_DIR
        / "09_tyre_age_relative_pace.png",
        dpi=120,
    )

    plt.close()


def main():

    laps = load_data()

    print(
        f"Raw lap rows: {len(laps):,}"
    )

    laps = clean_laps(laps)

    print(
        f"Clean lap rows: {len(laps):,}"
    )

    relative_laps = (
        calculate_relative_pace(laps)
    )

    summary = (
        summarize_tyre_age(
            relative_laps
        )
    )

    plot_tyre_age(
        summary
    )

    print(
        "\nAnalysis complete."
    )

    print(
        "\nTyre age relative pace:"
    )

    print(
        summary.head(50).to_string(
            index=False
        )
    )

    print(
        "\nFiles created:"
    )

    print(
        PROCESSED_DIR
        / "tyre_age_relative_pace_summary.csv"
    )

    print(
        FIG_DIR
        / "09_tyre_age_relative_pace.png"
    )


if __name__ == "__main__":
    main()