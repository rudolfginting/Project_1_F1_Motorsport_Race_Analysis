from pathlib import Path
import time

import fastf1
import pandas as pd


YEAR = 2024
MAX_RACES = None  # Set to 3 while testing, then change to None for the full season.

ROOT = Path(__file__).resolve().parents[1]
CACHE_DIR = ROOT / ".fastf1-cache"
RAW_DIR = ROOT / "data" / "raw"

CACHE_DIR.mkdir(exist_ok=True)
RAW_DIR.mkdir(parents=True, exist_ok=True)

fastf1.Cache.enable_cache(str(CACHE_DIR))


def main():
    schedule = fastf1.get_event_schedule(YEAR, include_testing=False)

    if MAX_RACES is not None:
        schedule = schedule.head(MAX_RACES)

    all_results = []
    all_laps = []

    print(f"Downloading {len(schedule)} race weekends from {YEAR}...")

    for _, event in schedule.iterrows():
        round_number = int(event["RoundNumber"])
        event_name = event["EventName"]

        print(f"\n[{round_number}] {event_name}")

        try:
            session = fastf1.get_session(YEAR, round_number, "R")
            session.load(
                laps=True,
                telemetry=False,
                weather=False,
                messages=False,
            )

            results = session.results.copy()
            results["Year"] = YEAR
            results["RoundNumber"] = round_number
            results["EventName"] = event_name

            result_columns = [
                "Year", "RoundNumber", "EventName",
                "Abbreviation", "FullName", "TeamName",
                "Position", "GridPosition", "Points",
                "Status", "Laps"
            ]
            result_columns = [c for c in result_columns if c in results.columns]
            all_results.append(results[result_columns])

            laps = session.laps.copy()
            if not laps.empty:
                laps["Year"] = YEAR
                laps["RoundNumber"] = round_number
                laps["EventName"] = event_name
                all_laps.append(laps)

            print(f"  results: {len(results)} rows | laps: {len(laps)} rows")

        except Exception as exc:
            print(f"  SKIPPED: {exc}")

        time.sleep(1)

    if not all_results:
        raise RuntimeError("No race results were downloaded.")

    results_df = pd.concat(all_results, ignore_index=True)
    results_df.to_csv(RAW_DIR / "race_results_2024.csv", index=False)

    if all_laps:
        laps_df = pd.concat(all_laps, ignore_index=True)
        # Keep the columns needed for this beginner/intermediate analysis.
        wanted = [
            "Year", "RoundNumber", "EventName",
            "Driver", "DriverNumber", "Team",
            "LapNumber", "LapTime", "Stint",
            "Compound", "TyreLife", "FreshTyre",
            "TrackStatus", "PitOutTime", "PitInTime",
            "IsPersonalBest"
        ]
        wanted = [c for c in wanted if c in laps_df.columns]
        laps_df[wanted].to_csv(RAW_DIR / "race_laps_2024.csv", index=False)
        print(f"\nSaved {len(laps_df)} lap rows.")
    else:
        print("\nNo lap data was saved.")

    print("\nDone.")
    print(f"Results: {RAW_DIR / 'race_results_2024.csv'}")
    print(f"Laps:    {RAW_DIR / 'race_laps_2024.csv'}")


if __name__ == "__main__":
    main()
