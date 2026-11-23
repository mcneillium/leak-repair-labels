import numpy as np
import pandas as pd

from lrl.nightflow import night_flow
from lrl.rule import choose_threshold, drops, flags, in_year, match, score


def step_series():
    days = pd.date_range("2018-01-01", periods=20, freq="D")
    values = [50.0] * 10 + [40.0] * 10
    return pd.Series(values, index=days)


def test_drop_is_ten_at_the_step_and_zero_away_from_it():
    drop = drops(step_series())
    assert drop.loc["2018-01-10"] == 10.0
    assert drop.loc["2018-01-05"] == 0.0
    assert abs(drop.loc["2018-01-09"] - 20.0 / 3) < 1e-9
    assert abs(drop.loc["2018-01-08"] - 10.0 / 3) < 1e-9


def test_one_flag_for_one_step():
    drop = drops(step_series())
    found = flags(drop, 5.0)
    assert list(found) == [pd.Timestamp("2018-01-10")]
    assert len(flags(drop, 10.5)) == 0


def test_match_is_one_to_one_and_within_two_days():
    flag_days = [pd.Timestamp("2018-03-01"), pd.Timestamp("2018-03-02"), pd.Timestamp("2018-06-01")]
    repair_days = [pd.Timestamp("2018-03-03"), pd.Timestamp("2018-06-04")]
    used_flags, used_repairs = match(flag_days, repair_days)
    assert used_repairs == {0}
    assert used_flags == {1}


def test_score_counts():
    flag_days = [pd.Timestamp("2018-03-01"), pd.Timestamp("2018-06-01")]
    repair_days = [pd.Timestamp("2018-03-02"), pd.Timestamp("2018-09-01"), pd.Timestamp("2018-10-01")]
    result = score(flag_days, repair_days)
    assert result["found"] == 1
    assert result["precision"] == 0.5
    assert abs(result["recall"] - 1 / 3) < 1e-12
    assert abs(result["f1"] - 0.4) < 1e-12


def test_threshold_tie_goes_to_the_larger_value():
    drop = drops(step_series())
    repair_days = [pd.Timestamp("2018-01-11")]
    threshold, f1 = choose_threshold(drop, repair_days, 2018, [2.0, 5.0, 9.0, 12.0])
    assert threshold == 9.0
    assert f1 == 1.0


def test_night_flow_takes_tank_filling_off():
    times = pd.date_range("2018-01-01 00:00", "2018-01-01 23:55", freq="5min")
    flows = pd.DataFrame({"a": 60.0, "b": 40.0}, index=times)
    hours_since_two = (times - pd.Timestamp("2018-01-01 02:00")).total_seconds() / 3600
    level = 1.0 + 0.1 * np.clip(hours_since_two, 0, 2)
    levels = pd.DataFrame({"T": level}, index=times)
    result = night_flow(flows, levels, ["a", "b"], "T", area=100.0)
    assert len(result) == 1
    assert abs(result.iloc[0] - 90.0) < 1e-9


def test_in_year_keeps_only_that_year():
    days = [pd.Timestamp("2018-12-31"), pd.Timestamp("2019-01-01")]
    assert list(in_year(days, 2019)) == [pd.Timestamp("2019-01-01")]


def test_seven_day_window_ignores_a_weekly_rhythm_and_sees_a_step():
    days = pd.date_range("2018-01-01", periods=56, freq="D")
    weekly = np.where(days.dayofweek >= 5, 30.0, 0.0)
    step = np.where(np.arange(56) < 28, 20.0, 0.0)
    night = pd.Series(100.0 + weekly + step, index=days)
    drop = drops(night, window=7)
    assert abs(drop.loc["2018-01-28"] - 20.0) < 1e-9
    assert abs(drop.loc["2018-01-14"]) < 1e-9
    assert list(flags(drop, 10.0, window=7)) == [pd.Timestamp("2018-01-28")]
    three_day = flags(drops(night), 10.0)
    assert len(three_day) > 1
