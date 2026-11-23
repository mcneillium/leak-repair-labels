"""Loading the L-Town files."""

import math
import re
from pathlib import Path

import pandas as pd

INFLOW_METERS = ["p227", "p235"]
TANK = "T1"
DATASET_END = pd.Timestamp("2019-12-31 23:55")


def read_scada(path):
    """Read one SCADA csv (semicolon separated, decimal commas) indexed by time."""
    table = pd.read_csv(path, sep=";", decimal=",", parse_dates=["Timestamp"])
    table = table.set_index("Timestamp")
    if table.isna().any().any():
        raise ValueError(f"Missing values in {path}")
    return table


def read_years(folder, kind, years):
    """Join the yearly files of one kind (Flows or Levels) end to end."""
    folder = Path(folder)
    parts = [read_scada(folder / f"{year}_SCADA_{kind}.csv") for year in years]
    return pd.concat(parts).sort_index()


def tank_area(folder):
    """Plan area of the tank in square metres, from the diameter in the network file."""
    text = (Path(folder) / "L-TOWN.inp").read_text(errors="ignore")
    section = re.search(r"\[TANKS\](.*?)\n\[", text, re.S).group(1)
    for line in section.splitlines():
        fields = line.split()
        if fields and fields[0] == TANK:
            diameter = float(fields[5])
            return math.pi * (diameter / 2) ** 2
    raise ValueError("Tank not found in L-TOWN.inp")


def read_leaks(folder):
    """One row per leak: pipe, start, end, type. Times are those used to make the data."""
    lines = (Path(folder) / "dataset_configuration.yaml").read_text().splitlines()
    rows = []
    for line in lines:
        found = re.match(r"\s*-\s*(p\d+)\s*,(.*)", line)
        if not found:
            continue
        fields = [field.strip() for field in found.group(2).split(",")]
        if len(fields) < 5:
            continue
        row = {
            "pipe": found.group(1),
            "start": pd.Timestamp(fields[0]),
            "end": pd.Timestamp(fields[1]),
            "kind": fields[3],
        }
        rows.append(row)
    return pd.DataFrame(rows)


def repairs(leaks):
    """Leaks that were repaired before the dataset ends."""
    fixed = leaks[leaks["end"] < DATASET_END].copy()
    fixed["repair_day"] = fixed["end"].dt.normalize()
    return fixed.sort_values("end").reset_index(drop=True)
