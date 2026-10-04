from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd


ROOT = Path(__file__).resolve().parents[1]

PROCESSED_DIR = ROOT / "data" / "processed"
FIG_DIR = ROOT / "outputs" / "figures"

PROCESSED_DIR.mkdir(parents=True, exist_ok=True)
FIG_DIR.mkdir(parents=True, exist_ok=True)


INPUT_FILE = PROCESSED_DIR / "controlled_tyre_age_relative_pace.csv"
OUTPUT_FILE = PROCESSED_DIR / "weighted_tyre_degradation_trend.csv"
FIGURE_FILE = FIG_DIR / "12_weighted_tyre_degradation_trend.png"


def weighted_correlation(x, y, weights):
    """
    Menghitung weighted Pearson correlation.
    """

    x = np.asarray(x, dtype=float)
    y = np.asarray(y, dtype=float)
    weights = np.asarray(weights, dtype=float)

    mean_x = np.average(x, weights=weights)
    mean_y = np.average(y, weights=weights)

    cov_xy = np.average(
        (x - mean_x) * (y - mean_y),
        weights=weights,
    )

    var_x = np.average(
        (x - mean_x) ** 2,
        weights=weights,
    )

    var_y = np.average(
        (y - mean_y) ** 2,
        weights=weights,
    )

    if var_x == 0 or var_y == 0:
        return np.nan

    return cov_xy / np.sqrt(var_x * var_y)


def weighted_linear_regression(x, y, weights):
    """
    Weighted linear regression:

        y = slope * x + intercept

    Weight berasal dari jumlah lap pada setiap TyreLife.
    """

    x = np.asarray(x, dtype=float)
    y = np.asarray(y, dtype=float)
    weights = np.asarray(weights, dtype=float)

    # np.polyfit menggunakan sqrt(weight) secara internal
    slope, intercept = np.polyfit(
        x,
        y,
        1,
        w=np.sqrt(weights),
    )

    return slope, intercept


def analyze():
    df = pd.read_csv(INPUT_FILE)

    print(f"Loaded rows: {len(df):,}")

    required_columns = [
        "Compound",
        "TyreLife",
        "laps",
        "mean_relative_pace",
    ]

    missing = [
        column
        for column in required_columns
        if column not in df.columns
    ]

    if missing:
        raise ValueError(
            f"Missing required columns: {missing}"
        )

    df = df.dropna(
        subset=required_columns
    )

    results = []

    for compound, group in df.groupby("Compound"):

        group = group.sort_values("TyreLife").copy()

        x = group["TyreLife"].to_numpy()
        y = group["mean_relative_pace"].to_numpy()
        weights = group["laps"].to_numpy()

        # Minimal data check
        if len(group) < 3:
            continue

        slope, intercept = weighted_linear_regression(
            x,
            y,
            weights,
        )

        correlation = weighted_correlation(
            x,
            y,
            weights,
        )

        results.append(
            {
                "Compound": compound,
                "TyreLife_points": len(group),
                "total_laps": int(weights.sum()),
                "slope_seconds_per_lap": slope,
                "intercept": intercept,
                "weighted_correlation": correlation,
                "min_TyreLife": x.min(),
                "max_TyreLife": x.max(),
            }
        )

    summary = pd.DataFrame(results)

    summary = summary.sort_values(
        "slope_seconds_per_lap"
    )

    summary.to_csv(
        OUTPUT_FILE,
        index=False,
    )

    print("\nWeighted tyre degradation trend:")
    print(summary.to_string(index=False))

    # -------------------------
    # Plot
    # -------------------------

    plt.figure(figsize=(9, 6))

    for compound, group in df.groupby("Compound"):

        group = group.sort_values("TyreLife")

        x = group["TyreLife"].to_numpy()
        y = group["mean_relative_pace"].to_numpy()
        weights = group["laps"].to_numpy()

        if len(group) < 3:
            continue

        slope, intercept = weighted_linear_regression(
            x,
            y,
            weights,
        )

        predicted = slope * x + intercept

        plt.plot(
            x,
            predicted,
            label=compound,
        )

    plt.axhline(
        0,
        linewidth=1,
        linestyle="--",
    )

    plt.xlabel("Tyre life (laps)")
    plt.ylabel(
        "Weighted relative pace (seconds)"
    )

    plt.title(
        "2024 F1: Weighted Tyre-Age Relative Pace Trend"
    )

    plt.legend()
    plt.tight_layout()

    plt.savefig(
        FIGURE_FILE,
        dpi=120,
    )

    plt.close()

    print("\nSaved:")
    print(OUTPUT_FILE)
    print(FIGURE_FILE)


if __name__ == "__main__":
    analyze()