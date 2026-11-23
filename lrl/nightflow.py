"""Daily night flow with tank filling taken off."""

import pandas as pd

NIGHT_START_HOUR = 2
NIGHT_END_HOUR = 4


def night_flow(flows, levels, inflow_meters, tank, area):
    """Night flow in cubic metres an hour for every day that has a full night window."""
    inflow = flows[inflow_meters].sum(axis=1)
    hours = inflow.index.hour
    in_window = (hours >= NIGHT_START_HOUR) & (hours < NIGHT_END_HOUR)
    mean_inflow = inflow[in_window].groupby(inflow.index[in_window].normalize()).mean()
    counts = inflow[in_window].groupby(inflow.index[in_window].normalize()).count()
    steps_expected = (NIGHT_END_HOUR - NIGHT_START_HOUR) * 12
    full_days = counts[counts == steps_expected].index

    level = levels[tank]
    days = pd.DatetimeIndex(full_days)
    level_start = level.reindex(days + pd.Timedelta(hours=NIGHT_START_HOUR))
    level_end = level.reindex(days + pd.Timedelta(hours=NIGHT_END_HOUR))
    rise = level_end.to_numpy() - level_start.to_numpy()
    filling = area * rise / (NIGHT_END_HOUR - NIGHT_START_HOUR)

    result = mean_inflow.loc[days] - filling
    if result.isna().any():
        raise ValueError("Night flow could not be computed for every day")
    result.name = "night_flow"
    return result
