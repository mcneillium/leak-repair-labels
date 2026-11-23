"""Steps shared by the two scripts."""

import json
from pathlib import Path

import pandas as pd

from lrl.data import INFLOW_METERS, TANK, read_leaks, read_scada, read_years, repairs, tank_area
from lrl.nightflow import night_flow


RULES = {"3-day": 3, "7-day": 7}


def night_series(folder, years):
    flows = read_years(folder, "Flows", years)
    levels = read_years(folder, "Levels", years)
    area = tank_area(folder)
    return night_flow(flows, levels, INFLOW_METERS, TANK, area)


def repairs_in_year(folder, year):
    fixed = repairs(read_leaks(folder))
    return fixed[fixed["end"].dt.year == year].reset_index(drop=True)


def leak_size_at_repair(folder, year, fixed):
    """Leak flow in cubic metres an hour at the last time step before each repair."""
    leak_flows = read_scada(Path(folder) / f"{year}_Leakages.csv")
    sizes = []
    for pipe, end in zip(fixed["pipe"], fixed["end"]):
        before_end = leak_flows.loc[:end - pd.Timedelta(minutes=5), pipe]
        sizes.append(float(before_end.iloc[-1]))
    return sizes


def repair_table(fixed, sizes, found_numbers, drop):
    rows = []
    for number, row in fixed.iterrows():
        nearby = drop.loc[row["repair_day"] - pd.Timedelta(days=2):row["repair_day"] + pd.Timedelta(days=2)]
        entry = {
            "pipe": row["pipe"],
            "kind": row["kind"],
            "repaired": str(row["end"]),
            "leak_m3h_at_repair": round(sizes[number], 2),
            "largest_drop_within_2_days_m3h": round(float(nearby.max()), 2),
            "found": number in found_numbers,
        }
        rows.append(entry)
    return rows


def save_json(path, content):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(content, indent=2) + "\n")
