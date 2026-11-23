# Protocol 1: how wrong is a flow-drop rule at finding leak repairs?

Recorded at 01:29 UTC on 23 November 2026, before any 2019 flow, level or leak record was read. The 2018 files had been opened to check their layout and to list the 2018 leaks. For 2019, only two counts had been taken from the dataset's configuration file: 19 leaks start in 2019, and 7 of them end before 31 December 2019.

## Question

When leak repairs are inferred from a drop in night flow, how many of the real repairs does the rule find, and how many of the repairs it flags are real?

## Data

L-Town, the public benchmark of the Battle of the Leakage Detection and Isolation Methods (BattLeDIM 2020), Zenodo record 4017659, licence CC BY 4.0. It is a simulated town: flows, levels and leaks were generated with a hydraulic model, so the leak and repair times are known exactly. Measurements are every 5 minutes for 2018 and 2019.

Files used: `2018_SCADA_Flows.csv`, `2019_SCADA_Flows.csv`, `2018_SCADA_Levels.csv`, `2019_SCADA_Levels.csv`, `dataset_configuration.yaml`, and `L-TOWN.inp` for the tank diameter.

A real repair is a leak whose end time in `dataset_configuration.yaml` falls before the end of the dataset (31 December 2019, 23:55). 2018 has 10 and they match `2018_Fixed_Leakages_Report.txt`. 2019 has 7.

## Roles of the two years

2018 is the development year: the rule's threshold is chosen on it and it may be looked at freely. 2019 is the test year: the rule is run on it once, with the threshold fixed, after this protocol is committed.

## Night flow

Town inflow is the sum of the two reservoir meters, `p227` and `p235`, in cubic metres an hour. Part of the inflow fills the tank `T1` at night, so the tank's change in storage is taken off. For each day:

night flow = mean inflow from 02:00 up to 04:00, minus tank area times (level at 04:00 minus level at 02:00), divided by 2 hours.

Tank area comes from the 16 m diameter in `L-TOWN.inp`.

## The rule (chosen by Paul, 23 November)

Night-flow step drop. For each day d, the drop is the mean night flow of days d-2, d-1 and d, minus the mean night flow of days d+1, d+2 and d+3. Day d is flagged as a repair when its drop is at least the threshold and is the largest drop among days d-3 to d+3. That gives one flag for one step.

## Threshold

Chosen on 2018 only: every value from 1.0 to 40.0 cubic metres an hour in steps of 0.5 is tried, and the one with the highest F1 against the 2018 repairs is kept. A tie goes to the larger threshold.

## Scoring

A flag on day d finds a repair when the repair's date is within 2 days of d. Each repair is matched to at most one flag and each flag to at most one repair, nearest first.

Primary measure: how many of the 7 real repairs in 2019 the rule finds. Secondary measure: the share of the rule's 2019 flags that are real repairs. The size of each repaired leak at the time of repair is reported beside whether it was found.

## Paul's predictions for 2019 (recorded before the run)

- The rule finds 2 or 3 of the 7 real repairs.
- Between 50% and 80% of the rule's flags are real repairs.

## Limits known in advance

- The town is simulated. Its demand follows fixed patterns with noise, so drops that are not repairs may be rarer than in a real network.
- 7 test repairs is a small number. One repair more or less moves the result by 14 points.
- One town, one rule, one way of choosing the threshold.
- The rule stands in for the idea of inferring a repair from a flow drop. It is not any water company's rule.
