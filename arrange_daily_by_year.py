import csv
import os
from collections import defaultdict

INPUT_FILE = "Rainfall.csv"
OUTPUT_FILE = "rainfall_daily_1990_onwards.csv"
START_YEAR = 1990


def main():
    base_dir = os.path.dirname(os.path.abspath(__file__))
    input_path = os.path.join(base_dir, INPUT_FILE)

    # Buffer rows by station, filtered to 1990 onwards
    buffered = defaultdict(list)
    fieldnames = None

    with open(input_path, newline="") as f:
        reader = csv.DictReader(f)
        fieldnames = reader.fieldnames
        for row in reader:
            try:
                year = int(row["Year"])
            except (ValueError, KeyError, TypeError):
                continue
            if year < START_YEAR:
                continue
            sid = (row.get("StationId") or "").strip()
            buffered[sid].append(row)

    output_path = os.path.join(base_dir, OUTPUT_FILE)
    total_rows = 0

    with open(output_path, "w", newline="") as out:
        writer = csv.DictWriter(out, fieldnames=fieldnames)
        writer.writeheader()

        for sid in sorted(buffered):
            rows = buffered[sid]
            # Sort chronologically within each station: Year, Month, Day
            rows.sort(key=lambda r: (
                int(r["Year"]) if r.get("Year", "").isdigit() else 0,
                int(r["Month"]) if r.get("Month", "").isdigit() else 0,
                int(r["Day"]) if r.get("Day", "").isdigit() else 0,
            ))
            writer.writerows(rows)
            total_rows += len(rows)

    print(f"Written: {output_path}")
    print(f"Stations: {len(buffered)}")
    print(f"Daily rows (1990 onwards): {total_rows}")
    print(f"Columns: {fieldnames}")


if __name__ == "__main__":
    main()
