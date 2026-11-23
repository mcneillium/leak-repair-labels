"""Run each rule once on 2019 with the threshold fixed on 2018."""

import json
import sys
from pathlib import Path

from lrl.rule import drops, flags, in_year, score
from lrl.study import RULES, leak_size_at_repair, night_series, repair_table, repairs_in_year, save_json

TEST_YEAR = 2019


def main(folder):
    fixed_thresholds = json.loads(Path("results/threshold_2018.json").read_text())["rules"]
    night = night_series(folder, [2018, 2019])
    fixed = repairs_in_year(folder, TEST_YEAR)
    sizes = leak_size_at_repair(folder, TEST_YEAR, fixed)
    repair_days = list(fixed["repair_day"])
    night_2019 = night[night.index.year == TEST_YEAR]
    output = {
        "year": TEST_YEAR,
        "night_flow_mean_m3h": round(float(night_2019.mean()), 2),
        "rules": {},
    }
    for name, window in RULES.items():
        threshold = fixed_thresholds[name]["threshold_m3h"]
        drop = drops(night, window)
        flag_days = in_year(flags(drop, threshold, window), TEST_YEAR)
        result = score(flag_days, repair_days)
        true_flags = set(result["true_flags"])
        flag_rows = []
        for number, day in enumerate(flag_days):
            flag_row = {"day": str(day.date()), "drop_m3h": round(float(drop.loc[day]), 2), "real_repair": number in true_flags}
            flag_rows.append(flag_row)
        output["rules"][name] = {
            "window_days": window,
            "threshold_m3h": threshold,
            "repairs": result["repairs"],
            "flags": result["flags"],
            "found": result["found"],
            "recall": round(result["recall"], 4),
            "precision": None if result["flags"] == 0 else round(result["precision"], 4),
            "flag_table": flag_rows,
            "repair_table": repair_table(fixed, sizes, set(result["found_repairs"]), drop),
        }
        print("Rule:", name, "Threshold (m3/h):", threshold)
        print("Repairs:", result["repairs"], "Flags:", result["flags"], "Found:", result["found"])
    night_out = [{"day": str(day.date()), "night_flow_m3h": round(float(value), 2)} for day, value in night.items()]
    save_json("results/test_2019.json", output)
    save_json("results/night_flow_2018_2019.json", night_out)


if __name__ == "__main__":
    main(sys.argv[1])
