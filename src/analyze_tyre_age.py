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

    laps["TyreLife"] = pd.to_numeric(
        laps["TyreLife"],
        errors="coerce",
    )

    return laps


def clean_laps(laps):
    df = laps.copy()

    df = df.dropna(
        subset=[
            "Driver",
            "Compound",
            "TyreLife",
            "LapTimeSeconds",
        ]
    )

    # Remove unrealistic tyre-life values.
    df = df[df["TyreLife"] > 0]

    # Remove extremely slow laps.
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
                "LapTimeSeconds",
                "count",
            ),
            mean_lap_time=(
                "LapTimeSeconds",
                "mean",
            ),
            median_lap_time=(
                "LapTimeSeconds",
                "median",
            ),
        )
        .sort_values(
            [
                "Compound",
                "TyreLife",
            ]
        )
    )

    summary.to_csv(
        PROCESSED_DIR
        / "tyre_age_pace_summary.csv",
        index=False,
    )

    return summary


def plot_tyre_age(summary):
    plt.figure(figsize=(9, 6))

    compounds = summary[
        "Compound"
    ].dropna().unique()

    for compound in compounds:
        data = summary[
            summary["Compound"] == compound
        ]

        # Ignore very small samples.
        data = data[
            data["laps"] >= 20
        ]

        plt.plot(
            data["TyreLife"],
            data["mean_lap_time"],
            marker="o",
            label=compound,
        )

    plt.xlabel(
        "Tyre age (laps)"
    )

    plt.ylabel(
        "Mean lap time (seconds)"
    )

    plt.title(
        "2024 F1: Lap Pace by Tyre Age"
    )

    plt.legend()

    plt.tight_layout()

    plt.savefig(
        FIG_DIR
        / "08_tyre_age_pace.png",
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

    summary = summarize_tyre_age(
        laps
    )

    plot_tyre_age(
        summary
    )

    print(
        "\nAnalysis complete."
    )

    print(
        "\nTyre age summary:"
    )

    print(
        summary.head(30).to_string(
            index=False
        )
    )

    print(
        "\nFiles created:"
    )

    print(
        PROCESSED_DIR
        / "tyre_age_pace_summary.csv"
    )

    print(
        FIG_DIR
        / "08_tyre_age_pace.png"
    )


if __name__ == "__main__":
    main()