# Leak repair labels from a flow-drop rule

First look, 23 November 2026. One town, two rules, seven test repairs. Not peer reviewed.

Write-up: https://paulmartinmcneill.com/research/#leak-repair-labels

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

Every flag in both years matched a recorded repair, so the rules' errors here are all misses. `results/study.json` holds every threshold score, both repair tables and the flag paired with each repair; `results/stages.txt` is the printed output of the run.

I wanted to know whether a drop in night flow was enough to pick out a repair. I set the thresholds using 2018, then checked them against the seven recorded repairs in 2019. The three-night rule found three and the seven-night rule found six. Every flag matched a recorded repair within two days. What stood out to me was that the three-night rule could raise a genuine flag every time and still miss more than half the repairs.

## How to run

Put the files listed in `CITATION.md` in one folder, then:

```
python -m pip install pandas==2.2.3 PyYAML==6.0.3 pytest==9.2.0
python -m pytest -q test_leak_rule.py
python leak_rule.py "path/to/data" --output results
```

`RUN.md` has the same steps. Both thresholds are fixed from the 2018 files before any file containing 2019 records is opened.

## Limits

- The town is simulated. No flag in either year was false, which is unlikely to hold in a real network where demand changes, valve operations and meter faults also produce drops.
- Seven test repairs. One repair more or less moves a rule's result by 14 points.
- One town, two rules, one way of choosing the threshold.
- The rules stand in for the idea of inferring a repair from a flow drop. They are not any water company's rule, and no water company's data is used.

## Next stage

`docs/protocol_02_draft.md` is a draft of a second protocol: simulate more years of L-Town with leaks at known times, train a model on the rule's labels, and measure how many of the rule's misses the model repeats. The question, the design choices and the predictions have not been chosen yet, and nothing in it has been run.

## How this was produced

I chose the rule, recorded my predictions before the runs and chose amendment 1 from options suggested by an AI assistant. An AI assistant wrote and ran the first implementation on 23 November. Codex wrote a second implementation from a brief containing the rules and check values. Both implementations produced the same thresholds, flag dates and repair results. I kept the Codex version because it fixes both thresholds using the 2018 data before opening any file containing 2019 records. I also re-ran the study on my own machine and the numbers matched. LOG.md records the detailed choices and the date I reviewed each one.
