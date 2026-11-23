# Leak repair labels from a flow-drop rule

First look, 23 November 2026. One town, two rules, seven test repairs. Not peer reviewed.

## Question

When leak repairs are inferred from a drop in night flow, how many of the real repairs does the rule find, and how many of the repairs it flags are real?

## Why

A model that learns from repair records learns from whatever made those records. Where a repair is inferred from a drop in flow, the label comes from a rule, and the rule has its own errors. This study measures those errors on a public dataset where the true repair times are known.

## Data

L-Town, the benchmark of the Battle of the Leakage Detection and Isolation Methods (BattLeDIM 2020). It is a simulated town with flows and tank level every 5 minutes for 2018 and 2019, and the start and end time of every leak. Licence CC BY 4.0. See `CITATION.md`.

2018 is the development year (10 repairs). 2019 is the test year (7 repairs) and was opened once, after the protocol and predictions were committed.

## Result

| Rule | Threshold set on 2018 | 2018: found of 10, flags | 2019: found of 7, flags | Predicted for 2019 |
| --- | ---: | --- | --- | --- |
| 3-day step drop (primary) | 34.5 m3/h | 7 found, 7 flags | 3 found, 3 flags | 2 or 3 found; 50 to 80% of flags real |
| 7-day step drop (added by amendment 1) | 10.0 m3/h | 8 found, 8 flags | 6 found, 6 flags | 4 or 5 found; over 80% of flags real |

Every flag in both years was a real repair, so the rules' errors here are all misses. Tables for each repair are in `results/`.

<!-- TODO (Paul): put the findings in your own words. -->

## How to run

```
pip install pandas pytest
python -m lrl.download data
python -m pytest tests
python scripts/set_threshold_2018.py data
python scripts/test_2019.py data
```

Run the scripts from the repository root with `PYTHONPATH=.` set. `set_threshold_2018.py` reads no 2019 file.

## Limits

- The town is simulated. No flag in either year was false, which is unlikely to hold in a real network where demand changes, valve operations and meter faults also produce drops.
- Seven test repairs. One repair more or less moves a rule's result by 14 points.
- One town, two rules, one way of choosing the threshold.
- The rules stand in for the idea of inferring a repair from a flow drop. They are not any water company's rule, and no water company's data is used.

## How this was produced

The question was chosen by Paul McNeill from wording offered by an AI assistant. He chose the rule, recorded the predictions before each run and decided amendment 1. The assistant wrote the code and the protocol text and made both runs on its own machine. `LOG.md` records which choices were the assistant's. Paul has not yet re-run the study on his own machine.
