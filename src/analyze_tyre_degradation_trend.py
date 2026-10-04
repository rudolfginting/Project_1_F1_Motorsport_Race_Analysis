from pathlib import Path

import matplotlib.pyplot as plt
import pandas as pd


ROOT = Path(__file__).resolve().parents[1]

PROCESSED_DIR = ROOT / "data" / "processed"
FIG_DIR = ROOT / "outputs" / "figures"

FIG_DIR.mkdir(parents=True, exist_ok=True)


INPUT_FILE = (
    PROCESSED_DIR
    / "controlled_tyre_age_relative_pace.csv"
)

OUTPUT_FILE = (
    PROCESSED_DIR
    / "tyre_degradation_trend.csv"
)

FIGURE_FILE = (
    FIG_DIR
    / "11_tyre_degradation_trend.png"
)


def load_data():
    df = pd.read_csv(INPUT_FILE)

    # Pastikan tipe data benar
    df["TyreLife"] = pd.to_numeric(
        df["TyreLife"],
        errors="coerce"
    )

    df["mean_relative_pace"] = pd.to_numeric(
        df["mean_relative_pace"],
        errors="coerce"
    )

    df["laps"] = pd.to_numeric(
        df["laps"],
        errors="coerce"
    )

    df = df.dropna(
        subset=[
            "Compound",
            "TyreLife",
            "mean_relative_pace",
            "laps",
        ]
    )

    return df


def calculate_trend(df):
    results = []

    for compound, group in df.groupby("Compound"):

        # Gunakan hanya compound dengan
        # minimal 5 titik TyreLife.
        if len(group) < 5:
            continue

        x = group["TyreLife"]
        y = group["mean_relative_pace"]

        # Regresi linear:
        # y = slope*x + intercept
        slope, intercept = __import__(
            "numpy"
        ).polyfit(x, y, 1)

        correlation = x.corr(y)

        results.append(
            {
                "Compound": compound,
                "TyreLife_points": len(group),
                "slope_seconds_per_lap": slope,
                "intercept": intercept,
                "correlation": correlation,
                "min_TyreLife": x.min(),
                "max_TyreLife": x.max(),
            }
        )

    results = pd.DataFrame(results)

    results = results.sort_values(
        "slope_seconds_per_lap"
    )

    return results


def save_results(results):
    results.to_csv(
        OUTPUT_FILE,
        index=False
    )


def create_plot(df, results):

    plt.figure(figsize=(8, 5))

    for compound in results["Compound"]:

        data = df[
            df["Compound"] == compound
        ].sort_values("TyreLife")

        plt.scatter(
            data["TyreLife"],
            data["mean_relative_pace"],
            s=20,
            alpha=0.5,
            label=f"{compound} data"
        )

        result = results[
            results["Compound"] == compound
        ].iloc[0]

        x_min = data["TyreLife"].min()
        x_max = data["TyreLife"].max()

        x_line = pd.Series(
            [x_min, x_max]
        )

        y_line = (
            result["slope_seconds_per_lap"]
            * x_line
            + result["intercept"]
        )

        plt.plot(
            x_line,
            y_line,
            linewidth=2,
            label=(
                f"{compound} trend "
                f"({result['slope_seconds_per_lap']:.4f} s/lap)"
            )
        )

    plt.axhline(
        0,
        linewidth=1
    )

    plt.xlabel(
        "Tyre life (laps)"
    )

    plt.ylabel(
        "Mean relative pace (seconds)"
    )

    plt.title(
        "2024 F1: Relative Pace Trend vs Tyre Age"
    )

    plt.legend()

    plt.tight_layout()

    plt.savefig(
        FIGURE_FILE,
        dpi=120
    )

    plt.close()


def main():

    df = load_data()

    print(
        f"Loaded rows: {len(df):,}"
    )

    results = calculate_trend(df)

    save_results(results)

    create_plot(
        df,
        results
    )

    print(
        "\nTyre degradation trend:"
    )

    print(
        results.to_string(
            index=False
        )
    )

    print("\nSaved:")

    print(OUTPUT_FILE)

    print(FIGURE_FILE)


if __name__ == "__main__":
    main()