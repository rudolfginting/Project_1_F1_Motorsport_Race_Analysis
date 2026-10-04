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
    plt.savefig(FIG_DIR / name, dpi=120)
    plt.close()


def load_and_clean():
    laps = pd.read_csv(RAW_DIR / "race_laps_2024.csv")

    laps["LapTime"] = pd.to_timedelta(
        laps["LapTime"],
        errors="coerce"
    )
    laps["LapTimeSeconds"] = laps["LapTime"].dt.total_seconds()

    # Normalisasi nama event
    laps["EventName"] = (
        laps["EventName"]
        .astype(str)
        .str.replace(r"\s+", " ", regex=True)
        .str.strip()
    )

    # Data minimum yang dibutuhkan
    df = laps.dropna(
        subset=[
            "EventName",
            "Driver",
            "LapNumber",
            "LapTimeSeconds",
            "Compound",
            "TyreLife",
        ]
    ).copy()

    # Hanya lap dengan waktu yang masuk akal
    low = df["LapTimeSeconds"].quantile(0.01)
    high = df["LapTimeSeconds"].quantile(0.99)

    df = df[
        df["LapTimeSeconds"].between(low, high)
    ].copy()

    # Hindari pit entry / exit
    if "PitOutTime" in df.columns:
        df = df[df["PitOutTime"].isna()]

    if "PitInTime" in df.columns:
        df = df[df["PitInTime"].isna()]

    return df


def calculate_controlled_relative_pace(df):
    """
    Untuk setiap race + lap:
    - hitung jumlah pembalap
    - hanya gunakan lap dengan >= 5 pembalap
    - median pembalap lain dihitung tanpa memasukkan
      pembalap yang sedang dianalisis
    - relative pace = waktu pembalap - median pembalap lain
    """

    group_cols = ["EventName", "LapNumber"]

    # Jumlah pembalap pada setiap race + lap
    driver_count = (
        df.groupby(group_cols)["Driver"]
        .nunique()
        .rename("DriverCount")
        .reset_index()
    )

    df = df.merge(
        driver_count,
        on=group_cols,
        how="left"
    )

    # Minimal 5 pembalap pada lap yang sama
    df = df[df["DriverCount"] >= 5].copy()

    # Total lap time seluruh pembalap
    group_sum = (
        df.groupby(group_cols)["LapTimeSeconds"]
        .transform("sum")
    )

    # Median pembalap lain.
    # Untuk menghindari memasukkan waktu pembalap itu sendiri,
    # kita gunakan median dari seluruh pembalap lain secara eksplisit.
    def calculate_other_median(group):
        values = group["LapTimeSeconds"].tolist()
        drivers = group["Driver"].tolist()

        medians = []

        for i in range(len(values)):
            other_values = [
                values[j]
                for j in range(len(values))
                if j != i
            ]

            medians.append(
                pd.Series(other_values).median()
            )

        group = group.copy()
        group["OtherDriverMedian"] = medians
        return group

    df = (
        df.groupby(group_cols, group_keys=False)
        .apply(calculate_other_median)
        .reset_index(drop=True)
    )

    df["RelativeLapTime"] = (
        df["LapTimeSeconds"]
        - df["OtherDriverMedian"]
    )

    return df


def summarize(df):
    summary = (
        df.groupby(
            ["Compound", "TyreLife"],
            as_index=False
        )
        .agg(
            laps=("RelativeLapTime", "count"),
            mean_relative_pace=("RelativeLapTime", "mean"),
            median_relative_pace=("RelativeLapTime", "median"),
            std_relative_pace=("RelativeLapTime", "std"),
        )
    )

    # Minimal sample agar titik dengan data sangat sedikit
    # tidak terlalu memengaruhi interpretasi.
    summary = summary[
        summary["laps"] >= 20
    ].copy()

    summary = summary.sort_values(
        ["Compound", "TyreLife"]
    )

    summary.to_csv(
        PROCESSED_DIR /
        "controlled_tyre_age_relative_pace.csv",
        index=False
    )

    return summary


def plot(summary):
    plt.figure(figsize=(8, 5))

    for compound in summary["Compound"].dropna().unique():

        data = summary[
            summary["Compound"] == compound
        ].sort_values("TyreLife")

        plt.plot(
            data["TyreLife"],
            data["mean_relative_pace"],
            marker="o",
            markersize=3,
            label=compound
        )

    plt.axhline(0, linewidth=1)

    plt.xlabel("Tyre life (laps)")
    plt.ylabel(
        "Relative lap time vs other drivers (seconds)"
    )

    plt.title(
        "2024 F1: Controlled Relative Pace vs Tyre Age"
    )

    plt.legend()
    savefig("10_controlled_tyre_age_relative_pace.png")


def main():
    df = load_and_clean()

    print(f"Raw lap rows: {len(pd.read_csv(RAW_DIR / 'race_laps_2024.csv')):,}")
    print(f"Clean lap rows: {len(df):,}")

    df = calculate_controlled_relative_pace(df)

    print(
        f"Comparable lap observations: {len(df):,}"
    )

    summary = summarize(df)

    plot(summary)

    print("\nAnalysis complete.")
    print("\nControlled tyre-age relative pace:")
    print(summary.head(50).to_string(index=False))

    print("\nSaved:")
    print(
        PROCESSED_DIR /
        "controlled_tyre_age_relative_pace.csv"
    )
    print(
        FIG_DIR /
        "10_controlled_tyre_age_relative_pace.png"
    )


if __name__ == "__main__":
    main()