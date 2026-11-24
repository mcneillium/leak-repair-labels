"""Run with python leak_rule.py DATA_DIRECTORY --output results."""

import argparse
import json
import math
from pathlib import Path

import pandas as pd
import yaml

METERS = ["p227", "p235"]
TANK = "T1"
DIAMETER = 16
AREA = math.pi * (DIAMETER / 2) ** 2
NIGHT_START = 2
NIGHT_END = 4
STEP = pd.Timedelta(minutes=5)
WINDOWS = (3, 7)
TOLERANCE = 2
GRID = tuple(i / 2 for i in range(2, 81))
END = pd.Timestamp("2019-12-31 23:55")
CHECK_THRESHOLDS = (3, 10, 20, 34.5)


def read_year(folder, year, name):
    path = folder / f"{year}_{name}.csv"
    frame = pd.read_csv(path, sep=";", decimal=",", index_col="Timestamp", parse_dates=True)
    expected = pd.date_range(f"{year}-01-01", f"{year}-12-31 23:55", freq=STEP)
    if not frame.index.equals(expected) or frame.isna().any().any():
        raise ValueError(f"Incomplete readings or incorrect time grid in {path}")
    return frame.apply(pd.to_numeric, errors="raise")


def night_flow(inflow, level, area=AREA):
    days = pd.date_range(inflow.index.min().normalize(), inflow.index.max().normalize())
    start = days + pd.Timedelta(hours=NIGHT_START)
    stop = days + pd.Timedelta(hours=NIGHT_END)
    hours = NIGHT_END - NIGHT_START
    readings = inflow[(inflow.index.hour >= NIGHT_START) & (inflow.index.hour < NIGHT_END)]
    expected = pd.DatetimeIndex([t + i * STEP for t in start
                                 for i in range(int(pd.Timedelta(hours=hours) / STEP))])
    if not readings.index.equals(expected) or readings.isna().any():
        raise ValueError("A night has missing or misplaced inflow readings")
    opening = level.reindex(start)
    closing = level.reindex(stop)
    if opening.isna().any() or closing.isna().any():
        raise ValueError("Missing tank level at a night boundary")
    mean = readings.groupby(readings.index.normalize()).mean()
    return mean - area * (closing.to_numpy() - opening.to_numpy()) / hours


def drops(nights, window):
    before = nights.asfreq("D").rolling(window).mean()
    return (before - before.shift(-window)).dropna()


def flags(drop, window, threshold):
    peak = drop.asfreq("D").rolling(2 * window + 1, center=True, min_periods=1).max()
    return drop[(drop >= threshold) & drop.eq(peak.reindex(drop.index))]


def match(flag_days, repairs):
    candidates = []
    for day in flag_days:
        for pipe, end in repairs.items():
            gap = abs((day - end.normalize()).days)
            if gap <= TOLERANCE:
                candidates.append((gap, day, end.normalize(), pipe))
    matches = {}
    used = set()
    for _, day, _, pipe in sorted(candidates):
        if pipe not in matches and day not in used:
            matches[pipe] = day
            used.add(day)
    return matches


def scores(n_flags, n_repairs, found):
    return dict(flags=n_flags, repairs=n_repairs, found=found,
                precision=found / n_flags if n_flags else 0,
                recall=found / n_repairs if n_repairs else 0,
                f1=2 * found / (n_flags + n_repairs) if found else 0)


def choose_threshold(drop, window, repairs, grid=GRID):
    rows = []
    for threshold in grid:
        marked = flags(drop, window, threshold)
        row = scores(len(marked), len(repairs), len(match(marked.index, repairs)))
        rows.append(dict(threshold=threshold, **row))
    best = max(rows, key=lambda row: (row["f1"], row["threshold"]))
    return best["threshold"], rows


def report_repairs(folder):
    lines = (folder / "2018_Fixed_Leakages_Report.txt").read_text().splitlines()
    repairs = {}
    for line in lines:
        if line.startswith("-"):
            pipe, end = line[1:].split(",")
            repairs[pipe.strip()] = pd.Timestamp(end.strip())
    return repairs


def configuration(folder):
    rows = yaml.safe_load((folder / "dataset_configuration.yaml").read_text())["leakages"]
    leaks = []
    for row in filter(None, rows):
        pipe, _, end, _, kind, _ = map(str.strip, row.split(","))
        leaks.append((pipe, pd.Timestamp(end), kind))
    return pd.DataFrame(leaks, columns=["pipe", "end", "type"]).sort_values("end")


def evaluate(folder, year, series, thresholds, repairs):
    sizes = read_year(folder, year, "Leakages")
    rows = {}
    for pipe, end in repairs.items():
        rows[pipe] = dict(pipe=pipe, end=str(end), size=round(sizes.at[end - STEP, pipe], 2))
    summaries = {}
    for window, drop in series.items():
        marked = flags(drop, window, thresholds[window])
        marked = marked[marked.index.year == year]
        paired = match(marked.index, repairs)
        summary = scores(len(marked), len(repairs), len(paired))
        summary["flags_by_day"] = {str(day.date()): round(value, 2) for day, value in marked.items()}
        summaries[window] = summary
        for pipe, end in repairs.items():
            day = end.normalize()
            margin = pd.Timedelta(days=TOLERANCE)
            rows[pipe][f"drop_{window}"] = round(drop.loc[day - margin:day + margin].max(), 2)
            rows[pipe][f"flag_{window}"] = str(paired[pipe].date()) if pipe in paired else None
    return dict(windows=summaries, repairs=sorted(rows.values(), key=lambda row: row["end"]))


def run(folder, output):
    flow = read_year(folder, 2018, "SCADA_Flows")
    level = read_year(folder, 2018, "SCADA_Levels")[TANK]
    inflow = flow[METERS].sum(axis=1)
    print("Stage 1 rows (flows, levels):", len(flow), len(level))
    print("First and last:", flow.index[0], flow.index[-1])
    print("First meters and level:", *flow[METERS].iloc[0], level.iloc[0])
    print("First inflow, 15 June 03:00, annual mean:", round(inflow.iloc[0], 2),
          inflow.at[pd.Timestamp("2018-06-15 03:00")], round(inflow.mean(), 2))

    nights = night_flow(inflow, level)
    print("Stage 2 days and tank area:", len(nights), round(AREA, 2))
    first = inflow.loc["2018-01-01 02:00":"2018-01-01 03:55"].mean()
    print("First night mean, levels, filling rate:", round(first, 2),
          level.at[pd.Timestamp("2018-01-01 02:00")], level.at[pd.Timestamp("2018-01-01 04:00")],
          round(first - nights.iloc[0], 2))
    for day in ["01-01", "01-02", "01-03", "06-15", "12-31"]:
        print("Night flow:", day, round(nights[f"2018-{day}"], 2))
    print("Annual night mean:", round(nights.mean(), 2))
    print("Monday to Sunday:", nights.groupby(nights.index.weekday).mean().round(1).tolist())

    series = {w: drops(nights, w) for w in WINDOWS}
    for w, drop in series.items():
        print("Stage 3 window, valid days, first, last:", w, len(drop), drop.index[0], drop.index[-1])
        print("10 Jan, 10 Feb, 15 Jun:", [round(float(drop[f"2018-{d}"]), 2) for d in ("01-10", "02-10", "06-15")])
        for threshold in CHECK_THRESHOLDS:
            marked = flags(drop, w, threshold)
            print("Window, threshold, flags:", w, threshold, len(marked))
            if (w, threshold) in [(3, 34.5), (7, 10)]:
                print("Flag days:", marked.index.strftime("%Y-%m-%d").tolist())

    historical = report_repairs(folder)
    thresholds = {}
    grid = {}
    for w in WINDOWS:
        thresholds[w], grid[w] = choose_threshold(series[w], w, historical)
        for row in grid[w]:
            if row["threshold"] in CHECK_THRESHOLDS:
                print("Stage 4 window, threshold, flags, found, F1:", w, row["threshold"],
                      row["flags"], row["found"], round(row["f1"], 4))
    print("Fixed thresholds:", thresholds)

    # The joint configuration is opened only after both thresholds are fixed.
    leaks = configuration(folder)
    print("Leak counts:", len(leaks), leaks["type"].value_counts().to_dict())
    repaired = leaks[leaks["end"] < END]
    repairs = {}
    for year, group in repaired.groupby(repaired["end"].dt.year):
        repairs[year] = dict(zip(group["pipe"], group["end"]))
        print("Repairs:", year, group.to_string(index=False))
    if repairs[2018] != historical:
        raise ValueError("2018 report and configuration disagree")
    dev = evaluate(folder, 2018, series, thresholds, historical)
    print("2018 repair table:", pd.DataFrame(dev["repairs"]).to_string(index=False))

    next_flow = read_year(folder, 2019, "SCADA_Flows")[METERS].sum(axis=1)
    next_level = read_year(folder, 2019, "SCADA_Levels")[TANK]
    joined = night_flow(pd.concat([inflow, next_flow]), pd.concat([level, next_level]))
    series = {w: drops(joined, w) for w in WINDOWS}
    print("Stage 5 total days:", len(joined))
    for day in ["01-01", "02-03", "09-15"]:
        print("2019 night flow:", day, round(joined[f"2019-{day}"], 2))
    print("2019 mean:", round(joined.loc["2019"].mean(), 2))
    print("1 January drops:", [round(float(series[w]["2019-01-01"]), 2) for w in WINDOWS])
    test = evaluate(folder, 2019, series, thresholds, repairs[2019])
    for w, summary in test["windows"].items():
        print("2019 result:", w, summary)
    print("2019 repair table:", pd.DataFrame(test["repairs"]).to_string(index=False))
    output.mkdir(parents=True, exist_ok=True)
    result = dict(thresholds=thresholds, grid=grid, development=dev, test=test)
    (output / "study.json").write_text(json.dumps(result, indent=2, allow_nan=False) + "\n")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("data", type=Path)
    parser.add_argument("--output", type=Path, default=Path("results"))
    args = parser.parse_args()
    run(args.data, args.output)
