import pandas as pd
import pytest

from leak_rule import choose_threshold, drops, flags, match, night_flow


@pytest.fixture
def step():
    return pd.Series([50] * 10 + [40] * 10, index=pd.date_range("2018-01-01", periods=20))


def test_step_drop(step):
    drop = drops(step, 3)
    days = pd.to_datetime(["2018-01-10", "2018-01-09", "2018-01-08", "2018-01-05"])
    assert drop.loc[days].tolist() == pytest.approx([10, 20 / 3, 10 / 3, 0])


def test_one_flag_for_one_step(step):
    drop = drops(step, 3)
    assert flags(drop, 3, 5).index.tolist() == [step.index[9]]
    assert flags(drop, 3, 10.5).empty


def test_filling_tank():
    times = pd.date_range("2018-01-01 02:00", periods=25, freq="5min")
    inflow = pd.Series(100, index=times)
    level = pd.Series([1.0, 1.2], index=times[[0, -1]])
    assert night_flow(inflow, level, area=100).iloc[0] == pytest.approx(90)


def test_closest_flag_and_two_day_limit():
    marked = pd.to_datetime(["2018-03-01", "2018-03-02", "2018-06-01"])
    repairs = {"a": pd.Timestamp("2018-03-03"), "b": pd.Timestamp("2018-06-04")}
    assert match(marked, repairs) == {"a": marked[1]}


def test_larger_threshold_wins_tie(step):
    best, rows = choose_threshold(drops(step, 3), 3, {"pipe": step.index[9]}, [9, 5])
    assert [row["f1"] for row in rows] == [1, 1]
    assert best == 9


def test_weekly_rhythm():
    days = pd.date_range("2018-01-01", periods=56)
    nights = pd.Series([50 + 30 * (day.weekday() in (4, 5)) for day in days], index=days)
    nights.iloc[28:] -= 20
    assert flags(drops(nights, 7), 7, 10).index.tolist() == [days[27]]
    assert len(flags(drops(nights, 3), 3, 10)) > 1
