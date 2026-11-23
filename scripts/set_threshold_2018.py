"""Choose each rule's threshold on 2018. Reads no 2019 file."""

import sys

from lrl.rule import THRESHOLD_GRID, choose_threshold, drops, flags, in_year, score
from lrl.study import RULES, leak_size_at_repair, night_series, repair_table, repairs_in_year, save_json

DEVELOPMENT_YEAR = 2018


def one_rule(night, fixed, sizes, window):
    drop = drops(night, window)
    repair_days = list(fixed["repair_day"])
    threshold, f1 = choose_threshold(drop, repair_days, DEVELOPMENT_YEAR, THRESHOLD_GRID, window)
    flag_days = in_year(flags(drop, threshold, window), DEVELOPMENT_YEAR)
    result = score(flag_days, repair_days)
    curve = []
    for value in THRESHOLD_GRID:
        candidate_days = in_year(flags(drop, value, window), DEVELOPMENT_YEAR)
        candidate = score(candidate_days, repair_days)
        point = {"threshold": float(value), "flags": candidate["flags"], "found": candidate["found"], "f1": round(candidate["f1"], 4)}
        curve.append(point)
    return {
        "window_days": window,
        "threshold_m3h": threshold,
        "repairs": result["repairs"],
        "flags": result["flags"],
        "found": result["found"],
        "recall": round(result["recall"], 4),
        "precision": round(result["precision"], 4),
        "f1": round(f1, 4),
        "flag_days": [str(day.date()) for day in flag_days],
        "repair_table": repair_table(fixed, sizes, set(result["found_repairs"]), drop),
        "threshold_curve": curve,
    }


def main(folder):
    night = night_series(folder, [DEVELOPMENT_YEAR])
    fixed = repairs_in_year(folder, DEVELOPMENT_YEAR)
    sizes = leak_size_at_repair(folder, DEVELOPMENT_YEAR, fixed)
    weekday_means = night.groupby(night.index.dayofweek).mean()
    output = {
        "year": DEVELOPMENT_YEAR,
        "night_flow_mean_m3h": round(float(night.mean()), 2),
        "night_flow_mean_by_weekday_m3h": {str(day): round(float(value), 1) for day, value in weekday_means.items()},
        "rules": {},
    }
    for name, window in RULES.items():
        output["rules"][name] = one_rule(night, fixed, sizes, window)
        rule = output["rules"][name]
        print("Rule:", name, "Threshold (m3/h):", rule["threshold_m3h"])
        print("Repairs:", rule["repairs"], "Flags:", rule["flags"], "Found:", rule["found"])
    save_json("results/threshold_2018.json", output)


if __name__ == "__main__":
    main(sys.argv[1])
