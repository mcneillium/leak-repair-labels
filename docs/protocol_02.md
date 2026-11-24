# Protocol 2. Does a model trained on the rule's labels repeat the rule's misses?

Finalised 24 November 2026 at 03:40 UK time, before study scoring. Paul proposed the question, main design and prediction ranges and chose B9. At his request, Codex reviewed the remaining choices, specified the procedures below and committed this version. The feasibility timings at the end are the only simulation results in the draft history.

## Why a second stage

Protocol 1 measured the rule against the truth. In 2019 the three-night rule found 3 of the 7 repairs and the seven-night rule found 6, and neither raised a false flag in either year. So the rule's errors in L-Town are misses, not false alarms.

That is the general question in learning from imperfect labels: when labels come from an imperfect process, what does a model trained on them learn? Protocol 1 cannot answer it, because 7 test repairs give at most 4 misses to study. Simulating more years of the same town gives enough repairs, and enough rule misses, to ask whether a model learns the rule's blind spots. This follows the flood study, where the measure was how much of the label errors the trained model copied.

## Question (Paul's wording, 24 November)

If I train a model on repair labels made from drops in night flow, how often does it miss the same repairs as the rule that supplied its labels?

The three-night rule is primary. It missed four of seven repairs in the original test year, so there is a clear reason to study its misses. The seven-night rule is kept as a separate comparison.

## Data

Simulated years of L-Town, made from `L-TOWN_Real.inp` (Zenodo record 4017659, CC BY 4.0; B9) with leaks added at known times. Each simulated year gives 5-minute flows for `p227` and `p235` and the level of `T1`, so the night flow and both rules from protocol 1 run on it unchanged.

The real 2018 and 2019 data are not training or test data here. 2018 sets the leak ranges (B2) and is used in the first check. 2019 has already been scored, so it can only be shown beside the simulated results as already seen.

## Fixed choices

| Choice | Decision |
| --- | --- |
| B1 Simulator | WNTR's pressure-driven simulator with timed orifice leaks. Start with the 2018 comparison in "Checks before any study run". |
| B2 Leak generation | 2018 only sets the number, sizes and timing of leaks. Use the sampling rules below. |
| B3 Repair spacing | Spacing arises naturally in this experiment. The gap from each repair to the one before is recorded. A deliberately crowded repair schedule can be a separate experiment. |
| B4 Rule thresholds | 34.5 m3/h for three nights and 10.0 m3/h for seven nights, as fixed on 2018. |
| B5 Model | Logistic regression on the 14 surrounding night flows. A separate model for each rule's labels. The model uses nights after the candidate date, so it is described as identifying past repairs. |
| B6 Years | 10 training, 4 development and 6 final test years, whole years assigned to each split in advance. The development years fix the model's decision threshold and whether to merge consecutive positive days. The simulated repair truth is kept out of model fitting and threshold selection. |
| B7 Primary measure | Of all true repairs the three-night rule missed in the six test years, the fraction its model also missed. Counts pooled over the six years, shown as numerator and denominator. Each detector's flags are matched to the full repair list independently with protocol 1's rule (one to one, closest first, within 2 days), then compared by repair ID. If the rule misses none, the measure is reported as undefined. |
| B8 Seeds | Simulation seeds 1001 to 1010 for training, 1011 to 1014 for development, 1015 to 1020 for test. Model seed 42 wherever the fitting uses randomness. Recorded in `RUN.md`. |
| B9 Demand (Paul, 03:33) | Use `L-TOWN_Real.inp`. Give each simulated year a distinct, seed-selected whole-week offset into its year of demand. Before running any study year, measure the absolute change in leak-free night flow across the join; if it exceeds 5 m3/h, smooth the join and recheck it. |

Secondary measure: the number of unmatched model flags per test year, averaged over the six years. This is the cost of recovering a repair the rule missed. Shown alongside it: how many of the rule's missed repairs the model recovered, and how many repairs the rule found that the model then lost.

## Generating the years

Use the 365-day 2018 calendar and a five-minute grid. Reset the hydraulic initial conditions and leak schedule at each year boundary.

**B9 demand assignment.** Shuffle the ascending integers 0 through 51 once with Python's `random.Random(20261124).shuffle(weeks)`. Assign the first 20 entries in order to simulation seeds 1001 through 1020. The master seed controls demand assignment only. Each year's own seed controls its leaks. The fixed assignments are in `RUN.md`. Apply the same offset to all 104 demand patterns. For simulation slot t starting at zero and assigned week w, read source slot (t + 2016w) modulo 105120. Apply the shift to demands only. Each year retains the original order of demand samples except for the single wrap. Since 365 days is 52 weeks plus one day, the weekday alignment changes by one day after the wrap.

**B2 leak generation.** The 14 leaks that start in 2018 in `dataset_configuration.yaml` set the following ranges. Draws within each range are uniform. Use the year's random generator, keeping pipe selection, size, growth, start time and duration independent except for the explicit repair eligibility rule.

- Sample 14 different pipes without replacement from the sorted pipe IDs, excluding reservoir feeds `p227` and `p235`. Assign the first six abrupt leaks and the remaining eight incipient leaks. Place each leak at the midpoint of its pipe.
- Sample the final orifice diameter in millimetres. Use 15.9–22.9 for abrupt leaks and 8.8–22.3 for incipient leaks. An abrupt leak opens at full area. For an incipient leak draw a growth time of 3.6–97.8 days. Grow **orifice area** linearly from zero to the area implied by the final diameter. Update at 24-hour intervals from onset and set the exact full area at the growth endpoint, rounded to the nearest five-minute slot. Stop growth at repair or year end if either occurs first.
- Start with no leaks. Draw each onset uniformly from the five-minute slots after the first slot of the year. A leak with sampled final diameter at least 15 mm is eligible for repair. Draw its elapsed time to repair uniformly from the five-minute multiples within 10.3–69.3 days. Onset plus duration gives the repair timestamp, including the time of day. This permits overnight repairs. The observed 2018 clock-time range was 03:00–21:00.
- Leave smaller leaks open. If a planned repair falls outside the year, leave that leak open at year end and exclude that repair from the year's truth list. Keep naturally close repairs, preserve distinct pipe IDs and record the gap between successive repairs. The realised number of repairs can vary even though every year has 14 leak onsets.

## Fitting and evaluation details

1. For candidate date d, use the 14 night flows from d−6 through d+7 inclusive, in date order. Require all 14 nights in the same year. The target is one exactly when that rule flags d. Fit one logistic regression per rule to its training labels. Standardise each feature using training years only. Use an intercept, L2 penalty, C = 1, lbfgs, at most 1,000 iterations and equal weight per training day. Use model seed 42 wherever a random seed applies. Investigate nonconvergence before opening test scores.
2. On development years, consider all distinct predicted probabilities as inclusive thresholds plus a threshold above the maximum for zero flags. Compare two choices at each threshold: keep all positive days, or merge consecutive positive days within a year into one flag on the highest-probability day (earliest date on ties). Maximise pooled exact-date F1 against the rule's day labels on eligible development dates. Break ties by higher threshold, then by choosing merging. Freeze both settings before test. Development selection uses rule flags only.
3. Apply protocol 1's rules on each complete year's night-flow series. Model flags require the 14-night window. Score both detectors against the full in-year repair list, as specified in B7. Show separately how many true repairs fall outside the model's candidate-date span, since the rules and model may have different coverage at the ends of a year.
4. Report the seven-night model using the same measures in a separate comparison. Within each year match each detector independently to truth before pooling across years. Report counts of recovered and lost repairs, unmatched flags by year and the six-year mean.

## Checks before any study scoring

0. **Demand join.** Before generating any study year with leaks, run the 20 fixed demand offsets leak-free, using the same hydraulic settings and initial conditions as the study years. For an internal wrap, use `leak_rule.night_flow` on the last source-day night and the first source-day night, in chronological simulation order. Record the signed and absolute difference in m³/h. An offset of zero would have no internal wrap.

   If the absolute difference exceeds 5 m³/h, replace the first 24 hours after the wrap in each demand pattern with a crossfade at matching times of day. For slots j = 0,…,287 of that day, use (1 − j/287) × last-source-day[j] + (j/287) × first-source-day[j]. All other slots stay as supplied. This changes the demand input before hydraulics. Rerun that offset leak-free and recompute the same statistic. Log seed, week, join date, signed differences before and after, and whether smoothing was used. Exactly 5 passes. Use the checked demand inputs for the corresponding study year. If the recheck exceeds 5, pause before generating study years and date an amendment. Keep all join nights in scoring.
1. **2018 comparison.** Reproduce one 2018 leak in the real network. Use p232, a short incipient event starting on 31 January, with its recorded onset, growth endpoint, diameter and repair time. Use unshifted demand, compare corresponding nights for the period from onset through repair and report each simulated-minus-published difference and the median signed and median absolute differences. The published record includes other operating conditions and leaks. This comparison is descriptive and has no pass/fail cutoff.
2. **Rule path.** On a separate engineering year (seed 1000, offset zero), exercise the unchanged night-flow, drop and flag functions in `leak_rule.py` for both windows. Keep this year outside the three study splits.
3. **Reproduction.** Generate the engineering year twice with identical inputs and seed. Verify byte-identical flow, tank-level and repair-schedule files before running the study splits.

## Predictions fixed before scoring

1. Among the true repairs the three-night rule misses, its model will also miss **60–85%**, pooled over the six test years. Variable demand may obscure repair drops, increasing the number the rule misses. The model sees that same flow history, but a change in the number of rule misses alone gives no direction for the *fraction* the model repeats. Retain the original range. Show the numerator and denominator. With zero rule misses, the prediction cannot be assessed.
2. The three-night model will raise **0–3 unmatched flags per simulated test year on average**. The sparse rule labels favour few flags, while variable demand can still produce drops the model flags. Compare the total unmatched flags divided by six with this range. Individual years may exceed three.

Both intervals include their endpoints. Neither forecast is a condition for accepting the results.

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
