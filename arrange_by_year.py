import csv
import os
from collections import defaultdict

INPUT_FILE = "Rainfall.csv"
OUTPUT_SUMMARY = "rainfall_by_station_year_1990_onwards.csv"
OUTPUT_DIR = "station_by_year_1990_onwards"
START_YEAR = 1990


def parse_precip(value):
    """Return float precip or None if missing/invalid."""
    if value is None:
        return None
    value = value.strip()
    if value == "":
        return None
    try:
        return float(value)
    except ValueError:
        return None


def main():
    base_dir = os.path.dirname(os.path.abspath(__file__))
    input_path = os.path.join(base_dir, INPUT_FILE)

    # station_id -> {metadata, year -> list of precip values}
    stations = {}
    station_order = []

    with open(input_path, newline="") as f:
        reader = csv.DictReader(f)
        for row in reader:
            try:
                year = int(row["Year"])
            except (ValueError, KeyError):
                continue

            if year < START_YEAR:
                continue

            sid = row["StationId"].strip()
            precip = parse_precip(row.get("PRECIP"))

            if sid not in stations:
                stations[sid] = {
                    "Station_Name": row.get("Station_Name", "").strip(),
                    "Lat": row.get("Lat", "").strip(),
                    "Lon": row.get("Lon", "").strip(),
                    "Elev": row.get("Elev", "").strip(),
                    "years": defaultdict(list),
                }
                station_order.append(sid)

            if precip is not None:
                stations[sid]["years"][year].append(precip)

    station_order.sort()

    # Build summary rows arranged by station, then year
    summary_rows = []
    for sid in station_order:
        info = stations[sid]
        for year in sorted(info["years"]):
            vals = info["years"][year]
            total = sum(vals)
            mean = total / len(vals)
            maximum = max(vals)
            rainy = sum(1 for v in vals if v > 0)
            dry = len(vals) - rainy
            summary_rows.append({
                "StationId": sid,
                "Station_Name": info["Station_Name"],
                "Lat": info["Lat"],
                "Lon": info["Lon"],
                "Elev": info["Elev"],
                "Year": year,
                "N_obs": len(vals),
                "Total_Precip_mm": round(total, 2),
                "Mean_Daily_Precip_mm": round(mean, 3),
                "Max_Daily_Precip_mm": round(maximum, 2),
                "Rainy_Days": rainy,
                "Dry_Days": dry,
            })

    # Write summary CSV
    summary_path = os.path.join(base_dir, OUTPUT_SUMMARY)
    fieldnames = [
        "StationId", "Station_Name", "Lat", "Lon", "Elev", "Year",
        "N_obs", "Total_Precip_mm", "Mean_Daily_Precip_mm",
        "Max_Daily_Precip_mm", "Rainy_Days", "Dry_Days",
    ]
    with open(summary_path, "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(summary_rows)

    print(f"Summary written to {summary_path}")
    print(f"Stations: {len(station_order)}")
    print(f"Station-year records: {len(summary_rows)}")
    print(f"Year range: {START_YEAR} - {max(r['Year'] for r in summary_rows)}")

    # Write per-station daily CSV files arranged by year
    os.makedirs(os.path.join(base_dir, OUTPUT_DIR), exist_ok=True)
    per_station_count = 0
    with open(input_path, newline="") as f:
        reader = csv.DictReader(f)
        fieldnames = reader.fieldnames
        station_files = {}
        station_writers = {}
        current_sid = None

        # Pre-sort rows by (StationId, Year, Month, Day) is not stream-friendly;
        # instead, buffer per station then write sorted.
        buffered = defaultdict(list)
        for row in reader:
            try:
                year = int(row["Year"])
            except (ValueError, KeyError):
                continue
            if year < START_YEAR:
                continue
            sid = row["StationId"].strip()
            buffered[sid].append(row)

        for sid in sorted(buffered):
            rows = buffered[sid]
            rows.sort(key=lambda r: (int(r["Year"]), int(r["Month"]), int(r["Day"])))
            out_path = os.path.join(base_dir, OUTPUT_DIR, f"{sid}.csv")
            with open(out_path, "w", newline="") as out:
                writer = csv.DictWriter(out, fieldnames=fieldnames)
                writer.writeheader()
                writer.writerows(rows)
            per_station_count += 1

    print(f"Per-station files written to {OUTPUT_DIR}/ ({per_station_count} files)")


if __name__ == "__main__":
    main()
