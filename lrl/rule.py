"""The step-drop rule and its scoring."""

import numpy as np
import pandas as pd

WINDOW_DAYS = 3
MATCH_DAYS = 2


def drops(night, window=WINDOW_DAYS):
    """Mean of the window of days ending on d, minus the mean of the window starting on d+1."""
    before = night.rolling(window).mean()
    after = before.shift(-window)
    result = before - after
    result.name = "drop"
    return result


def flags(drop, threshold, window=WINDOW_DAYS):
    """Days whose drop reaches the threshold and is the largest within one window either side."""
    width = 2 * window + 1
    local_max = drop.rolling(width, center=True, min_periods=1).max()
    chosen = (drop >= threshold) & (drop == local_max)
    return drop.index[chosen.fillna(False).to_numpy()]


def match(flag_days, repair_days):
    """Pair flags with repairs no more than MATCH_DAYS apart, nearest first, one to one."""
    pairs = []
    for flag_number, flag_day in enumerate(flag_days):
        for repair_number, repair_day in enumerate(repair_days):
            gap = abs((flag_day - repair_day).days)
            if gap <= MATCH_DAYS:
                pairs.append((gap, flag_number, repair_number))
    pairs.sort()
    used_flags = set()
    used_repairs = set()
    for gap, flag_number, repair_number in pairs:
        if flag_number in used_flags or repair_number in used_repairs:
            continue
        used_flags.add(flag_number)
        used_repairs.add(repair_number)
    return used_flags, used_repairs


def score(flag_days, repair_days):
    """Counts and rates for one set of flags against one set of repairs."""
    used_flags, used_repairs = match(list(flag_days), list(repair_days))
    found = len(used_repairs)
    n_flags = len(flag_days)
    n_repairs = len(repair_days)
    recall = found / n_repairs if n_repairs else float("nan")
    precision = found / n_flags if n_flags else float("nan")
    if found == 0:
        f1 = 0.0
    else:
        f1 = 2 * precision * recall / (precision + recall)
    return {
        "repairs": n_repairs,
        "flags": n_flags,
        "found": found,
        "recall": recall,
        "precision": precision,
        "f1": f1,
        "found_repairs": sorted(used_repairs),
        "true_flags": sorted(used_flags),
    }


def in_year(days, year):
    days = pd.DatetimeIndex(days)
    return days[days.year == year]


def choose_threshold(drop, repair_days, year, grid, window=WINDOW_DAYS):
    """Threshold with the highest F1 in one year. A tie goes to the larger threshold."""
    best_threshold = None
    best_f1 = -1.0
    for threshold in grid:
        flag_days = in_year(flags(drop, threshold, window), year)
        f1 = score(flag_days, repair_days)["f1"]
        if f1 >= best_f1:
            best_f1 = f1
            best_threshold = float(threshold)
    return best_threshold, best_f1


THRESHOLD_GRID = np.arange(1.0, 40.5, 0.5)
