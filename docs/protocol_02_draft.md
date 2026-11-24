# Protocol 2 (draft): does a model trained on the rule's labels repeat the rule's misses?

Status: draft, third version, 24 November 2026. The first version was written by the assistant. This version records the choices Paul proposed on 24 November (sent at 02:49) and the details the assistant added to make them runnable, which are marked "to confirm". B9 was decided by Paul at 03:33. Nothing here is in force until Paul dates and commits the final version; his predictions and the remaining choices are still open for his review. No experiment has been run. The only code run so far is the feasibility check in `sim/`, which times the simulator and computes no result.

## Why a second stage

Protocol 1 measured the rule against the truth. In 2019 the three-night rule found 3 of the 7 repairs and the seven-night rule found 6, and neither raised a false flag in either year. So the rule's errors in L-Town are misses, not false alarms.

That is the general question in learning from imperfect labels: when labels come from an imperfect process, what does a model trained on them learn? Protocol 1 cannot answer it, because 7 test repairs give at most 4 misses to study. Simulating more years of the same town gives enough repairs, and enough rule misses, to ask whether a model learns the rule's blind spots. This follows the flood study, where the measure was how much of the label errors the trained model copied.

## Question (Paul's wording, 24 November)

If I train a model on repair labels made from drops in night flow, how often does it miss the same repairs as the rule that supplied its labels?

The three-night rule is primary. It missed four of seven repairs in the original test year, so there is a clear reason to study its misses. The seven-night rule is kept as a separate comparison.

## Data

Simulated years of L-Town, made from `L-TOWN_Real.inp` (Zenodo record 4017659, CC BY 4.0; B9) with leaks added at known times. Each simulated year gives 5-minute flows for `p227` and `p235` and the level of `T1`, so the night flow and both rules from protocol 1 run on it unchanged.

The real 2018 and 2019 data are not training or test data here. 2018 sets the leak ranges (B2) and is used in the first check. 2019 has already been scored, so it can only be shown beside the simulated results as already seen.

## Choices (Paul's proposals, 24 November; B9 decided at 03:33)

| Choice | Proposed decision |
| --- | --- |
| B1 Simulator | WNTR's pressure-driven simulator with timed orifice leaks. Start with the 2018 comparison in "Checks before any study run". |
| B2 Leak generation | 2018 only sets the number, sizes and timing of leaks. The actual sampling ranges, and how locations, durations and unrepaired leaks are handled, are written down before the study years are generated (draft ranges below). |
| B3 Repair spacing | Spacing arises naturally in this experiment. The gap from each repair to the one before is recorded. A deliberately crowded repair schedule can be a separate experiment. |
| B4 Rule thresholds | 34.5 m3/h for three nights and 10.0 m3/h for seven nights, as fixed on 2018. |
| B5 Model | Logistic regression on the 14 surrounding night flows. A separate model for each rule's labels. The model uses nights after the candidate date, so it is described as identifying past repairs. |
| B6 Years | 10 training, 4 development and 6 final test years, whole years assigned to each split in advance. The development years fix the model's decision threshold and how consecutive positive days become one flag. The simulated repair truth is kept out of model fitting and threshold selection. |
| B7 Primary measure | Of all true repairs the three-night rule missed in the six test years, the fraction its model also missed. Counts pooled over the six years, shown as numerator and denominator. Each detector's flags are matched to the full repair list independently with protocol 1's rule (one to one, closest first, within 2 days), then compared by repair ID. If the rule misses none, the measure is reported as undefined. |
| B8 Seeds | Simulation seeds 1001 to 1010 for training, 1011 to 1014 for development, 1015 to 1020 for test. Model seed 42 wherever the fitting uses randomness. Recorded in `RUN.md`. |
| B9 Demand (Paul, 03:33) | Use `L-TOWN_Real.inp`. Give each simulated year a distinct, seed-selected whole-week offset into its year of demand. Before running any study year, measure the absolute change in leak-free night flow across the join; if it exceeds 5 m3/h, smooth the join and recheck it. |

Secondary measure: the number of unmatched model flags per test year, averaged over the six years. This is the cost of recovering a repair the rule missed. Shown alongside it: how many of the rule's missed repairs the model recovered, and how many repairs the rule found that the model then lost.

## Details added by the assistant (to confirm)

These fill gaps the choices above leave open. Each is a suggestion for Paul to accept, change or drop before the final version.

1. **Demand (B9), decided by Paul at 03:33; see the table.** Background recorded on 24 November: the public `L-TOWN.inp` has one-week demand patterns, so every simulated week would have had the same demand. `L-TOWN_Real.inp` (same Zenodo record, MD5 equal to the record's) has the same layout but slightly different length, diameter and roughness for every pipe, and 104 demand patterns of 105,120 five-minute steps (365 days). By `dataset_configuration.yaml` it is the network that made the published data. The options not taken were daily scaling from 2018, random noise on each node's demand, and epyt-flow's realistic-demand loader. Details still to confirm: how the offset is drawn from the seed so that no two years share one, and how a join above 5 m3/h is smoothed.
2. **Draft B2 ranges, from the 2018 leaks only.** Counted from the 14 leaks in `dataset_configuration.yaml` that start in 2018. That file also lists the 2019 leaks; they were read for protocol 1 and are not used here.
   - 14 leaks a year, at different pipes drawn at random, excluding the reservoir feeds `p227` and `p235`.
   - Type: 6 of 14 abrupt (full size at once), 8 incipient (growing to full size).
   - Diameter: abrupt 15.9 to 22.9 mm, incipient 8.8 to 22.3 mm, uniform within each range.
   - Incipient growth time, start to full size: 3.6 to 97.8 days.
   - Start times uniform over the year.
   - Repair: in 2018 all 6 abrupt leaks were repaired and 4 of 8 incipient ones were; the 4 left open were the four smallest (8.8 to 11.8 mm). Draft: repair every leak of 15 mm or more, leave the rest open, and draw the time from start to repair from 10.3 to 69.3 days. A repair that would fall after 31 December leaves the leak open at the end of the year.
   - Repair time of day uniform (2018 repairs ranged from 03:00 to 21:00).
   - Each year starts with no leak, as 2018 did.
3. **Growing leaks in WNTR.** WNTR keeps a leak's area fixed, so an incipient leak would be stepped up once a day from zero to full size.
4. **The 14 nights for B5.** Nights d-6 to d+7, the same nights the seven-night rule compares. A day is a positive example when the rule flagged that day. Each rule flagged 3 to 8 days a year in 2018 and 2019, so the classes are very unequal; the decision threshold set on the development years handles that.
5. **How the development years set the model's threshold without the truth.** The threshold and the merging of consecutive positive days are chosen against the rule's own flags on the development years, by best F1 against those flags, with a tie going to the higher threshold as in protocol 1. Merging: consecutive positive days become one flag on the day with the highest probability.
6. **The seven-night comparison.** The same measures, computed for the seven-night rule and its model, reported beside the primary result and not combined with it.
7. **Calendar.** Each simulated year runs on the 2018 calendar (365 days), so the weekly rhythm in night flow falls on the same weekdays.

## Checks before any study run

0. The join (Paul, B9). On a leak-free simulation of `L-TOWN_Real.inp`, measure the absolute change in night flow across the point where a shifted year wraps to the start of the demand year. If it exceeds 5 m3/h, smooth the join and measure it again.
1. Reproduce one 2018 leak from `dataset_configuration.yaml` in the simulator with `L-TOWN_Real.inp` and compare the simulated night flow with the published 2018 night flow for the same weeks. This uses 2018 only. The difference is reported without a pass or fail cutoff (Paul, 03:33).
2. Run both protocol 1 rules on one simulated year and confirm the code path is the one in `leak_rule.py`.
3. Fix the generator and check that the same seed gives byte-identical files.

## Paul's predictions (drafts, not yet confirmed)

These are Paul's draft ranges of 24 November. They stay drafts until he confirms them, with the date and time, in the final version.

1. The model trained on the three-night labels will repeat 60 to 85% of that rule's missed repairs. It sees the same night flows and learns from the rule's flags, so it should pick up many of the same blind spots.
2. That model will raise 0 to 3 unmatched flags per simulated test year on average. The original rule raised few flags, but the model may also flag drops that fall short of the rule's cutoff.

## Limits known in advance

- The simulated years come from the same model as the benchmark, so the rule may do better or worse on them than on a real network.
- The leaks are drawn from ranges set from one year. The rule's miss rate depends on those ranges.
- The demand comes from one year of the benchmark, shifted by whole weeks, so the simulated years share the same seasons and differ mainly in their leaks and in where the year starts.
- A model trained on simulated night flow has not been shown to work on real data.

## Feasibility (assistant work, 24 November 2026)

Run in a Python 3 environment with `wntr` 1.5.0 on the assistant's machine. The scripts are `sim/feasibility.py` and `sim/timing7.py`.

- `L-TOWN.inp` loads: 782 junctions, 905 pipes, 1 tank, 2 reservoirs, 1 pump, a 300 s hydraulic step and 3 demand patterns.
- EPANET without leaks: 0.2 s for 1 day and 1.0 s for 7 days.
- WNTR's simulator with one leak: 8.8 s for 2 days. The leak added 37.9 m3/h after it started, from an orifice area of 0.0005 m2 picked only to test the code.
- WNTR's simulator with two leaks: 31.2 s for 7 days.
- EPANET with one fixed emitter: 1.0 s for 7 days.

At 31 s a week, one simulated year would take about 27 minutes on that machine. This is arithmetic from one run, not a measurement. Twenty years in four parallel processes would be roughly 2 to 3 hours.

With `L-TOWN_Real.inp` (B9), timed at Paul's request on 24 November with `sim/timing_real.py`; the same machine, one week each, demand starting at the first week, nothing scored and no night flow computed:

- Loading the 177 MB file: 5.5 s.
- WNTR's pressure-driven simulator, 7 days, no leak: 41.6 s (2,017 time steps).
- The same with one test leak (orifice area 0.0005 m2 at one junction from day 3, chosen only to test the code): 42.1 s.

At about 42 s a week, one simulated year would take about 37 minutes on that machine, and the 20 study years about 12 hours in one process or about 3 hours in four. This is arithmetic from one run of each, not a measurement of a full year.
