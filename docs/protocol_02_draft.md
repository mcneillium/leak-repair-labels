# Protocol 2 (draft): does a model trained on the rule's labels repeat the rule's misses?

Status: draft written by the assistant on 24 November 2026 for Paul to edit. Nothing here is fixed until Paul chooses the question, fills in the open choices and records his predictions with a date. No experiment has been run. The only code run so far is the feasibility check in `sim/`, which times the simulator and computes no result.

## Why a second stage

Protocol 1 measured the rule against the truth. In 2019 the 3-night rule found 3 of the 7 repairs and the 7-night rule found 6, and neither raised a false flag in either year. So the rule's errors in L-Town are misses, not false alarms.

That is the question Dr Feng's project asks in general: when labels come from an imperfect process, what does a model trained on them learn? Protocol 1 cannot answer it, because 7 test repairs give at most 4 misses to study. Simulating more years of the same town gives enough repairs, and enough rule misses, to ask whether a model learns the rule's blind spots.

This follows the flood study, where the measure was how much of the label errors the trained model copied.

## Question (Paul to choose or rewrite one)

- A. When a model is trained on repair labels made by the flow-drop rule, what share of the repairs the rule missed does the model also miss?
- B. Does a model trained on the rule's labels find any repairs the rule missed, and how many false flags does it raise doing so?
- C. How does the share of rule misses that the model repeats change as the gap between two repairs gets shorter?

Chosen question, in Paul's words, with the date:

> TODO (Paul)

## Data

Simulated years of L-Town, made from `L-TOWN.inp` (Zenodo record 4017659, CC BY 4.0) with leaks added at known times. Each simulated year gives 5-minute flows for `p227` and `p235` and the level of `T1`, so the night flow and both rules from protocol 1 run on it unchanged.

The real 2018 and 2019 data are not training or test data here. 2019 has already been scored, so using it again would not be a fresh test. It can be shown beside the simulated results as a check that the simulation behaves like the published data, and it will be labelled as already seen.

## Open choices (Paul to decide)

| Choice | Options | Notes |
| --- | --- | --- |
| B1 Simulator | (a) WNTR's own simulator with pressure-driven demand and leaks as orifices, timed below. (b) EPANET emitters, run in segments with the tank level carried across, which is about 30 times faster but needs more code. (c) The BattLeDIM loaders in the `epyt-flow` or `water-benchmark-hub` packages, if they can regenerate scenarios with new leaks. | (c) needs checking before it is chosen. |
| B2 Leaks per year and their sizes, start times and repair times | Drawn at random from ranges taken from the 2018 leaks only. | Using 2018 keeps 2019 out of the design. |
| B3 Spacing of repairs | Left random, or set on purpose so some repairs fall close together. | The 7-night rule's one 2019 miss came six days after another repair. Question C needs this set on purpose. |
| B4 Rule thresholds | Fixed at 34.5 and 10.0 m3/h from protocol 1, or chosen again on simulated development years. | Fixed is simpler and keeps the rule identical. |
| B5 Model | A logistic regression on the 14 night flows around each day, or a small 1D convolutional network on the same window. | Both run on a CPU. |
| B6 Years | How many simulated years for training, for choosing settings, and for the final test. | The test years are scored once, at the end. |
| B7 Primary measure | Named before any result is seen. For question A: of the true repairs the rule missed in the test years, the share the model also misses. | Scoring uses protocol 1's matching: one to one, within 2 days. |
| B8 Seeds | The seed for the leak draws and for the model. | Recorded in `RUN.md`. |

## Checks before any study run

1. Reproduce one 2018 leak from `dataset_configuration.yaml` in the simulator and compare the simulated night flow with the published 2018 night flow for the same weeks. This uses 2018 only.
2. Run both protocol 1 rules on one simulated year and confirm the code path is the one in `leak_rule.py`.
3. Fix the generator and check that the same seed gives byte-identical files.

## Paul's predictions (recorded before the run)

> TODO (Paul): one prediction for the primary measure, and one for the secondary measure, each with a range. Date and time.

## Limits known in advance

- The simulated years come from the same model as the benchmark, so the rule may do better or worse on them than on a real network.
- The leaks are drawn from ranges set by the designer. The rule's miss rate depends on those ranges.
- A model trained on simulated night flow has not been shown to work on real data.

## Feasibility (assistant work, 24 November 2026)

Run in a Python 3 environment with `wntr` 1.5.0 on the assistant's machine. The scripts are `sim/feasibility.py` and `sim/timing7.py`.

- `L-TOWN.inp` loads: 782 junctions, 905 pipes, 1 tank, 2 reservoirs, 1 pump, a 300 s hydraulic step and 3 demand patterns.
- EPANET without leaks: 0.2 s for 1 day and 1.0 s for 7 days.
- WNTR's simulator with one leak: 8.8 s for 2 days. The leak added 37.9 m3/h after it started, from an orifice area of 0.0005 m2 picked only to test the code.
- WNTR's simulator with two leaks: 31.2 s for 7 days.
- EPANET with one fixed emitter: 1.0 s for 7 days.

At 31 s a week, one simulated year with option B1(a) would take about 27 minutes on that machine. This is arithmetic from one run, not a measurement. Twenty years in four parallel processes would be roughly 2 to 3 hours.
