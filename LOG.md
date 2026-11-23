# Log

Times are UTC on 23 November 2026. The commit times are the record where they differ.

## Decisions by Paul

1. Use the public L-Town benchmark for a leakage study, with results reported as a first look.
2. The rule: a step drop in night flow (02:00 to 04:00, tank filling removed), 3 days before against 3 days after, threshold chosen on 2018. A flag counts when it is within 2 days of a real repair.
3. Predictions for the 3-day rule on 2019: 2 or 3 of the 7 repairs found; 50 to 80% of flags real.
4. Amendment 1, after seeing 2018 only: keep the 3-day rule as primary and add a 7-day rule beside it.
5. Predictions for the 7-day rule on 2019: 4 or 5 of the 7 repairs found; over 80% of flags real.

Decisions 2 to 5 were made by choosing among options the assistant offered.

## Choices made by the assistant (for Paul to confirm or change)

- A1. Town inflow is `p227` plus `p235`, the two pipes leaving the reservoirs in `L-TOWN.inp`.
- A2. Tank filling is taken off as tank area times the rise in level between 02:00 and 04:00, divided by 2 hours. The level is recorded to 0.01 m, which is about 1 m3/h over the window.
- A3. One flag per step: a day is flagged only when its drop is the largest within one window either side.
- A4. Threshold grid 1.0 to 40.0 m3/h in steps of 0.5; highest F1 on 2018; a tie goes to the larger threshold.
- A5. Flags and repairs are matched one to one, nearest first.
- A6. A real repair is a leak whose end time is before the end of the dataset. Leaks that run to 31 December 2019, 23:55 are treated as never repaired.
- A7. Primary measure: repairs found in 2019. Secondary: share of flags that are real.
- A8. For the 2019 run the 2018 and 2019 flows are joined, so that drops in the first days of 2019 can use the last nights of 2018. A flag belongs to the year of its day.
- A9. The wording of the question and of the protocol.

## Work done by the assistant

All code, tests, the protocol text, this log and both runs. Runs were made on a cloud Linux machine with Python 3.13.18 and pandas 3.0.5. Paul has not yet re-run them.

## Record

- 01:29. Protocol 1 written with Paul's rule and predictions. Before this, the 2018 files had been opened to check their layout and list the 2018 leaks. From the configuration file two counts for 2019 had been taken (19 leaks starting, 7 ending before the year end) and nothing else.
- One test had a wrong expected value: for a 10-unit step I wrote that the drop one day before the step is 10/3. It is 20/3, because two of the three days after it are already lower. The code was right and the test was corrected before the first commit.
- Commit `1bcdf90`: protocol, code and tests. No 2019 file read.
- Run 1 (2018). 3-day rule: threshold 34.5 m3/h, 7 flags, 7 of 10 repairs found. Mean night flow 98.3 m3/h. Night flow is higher on two nights of each week: weekday means 88.9 to 94.5 on five days, 111.1 and 120.8 on the other two. At thresholds up to 3 m3/h the 3-day rule raises 52 flags in the year.
- 01:56. Amendment 1 recorded with Paul's decision and his predictions for the 7-day rule.
- Run 1 repeated for both rules. 3-day rule unchanged. 7-day rule: threshold 10.0 m3/h, 8 flags, 8 of 10 repairs found. Its two misses, p538 (2 June) and p866 (12 June), each fall within 14 days of another repair.
- Commit `894d638`: amendment and both thresholds. No 2019 file read.
- Run 2 (2019), made once. 3-day rule: 3 flags, 3 of 7 repairs found. 7-day rule: 6 flags, 6 of 7 found. No flag in 2019 was false for either rule. Mean night flow in 2019 is 148.6 m3/h.
- Check: the 2019 result was recounted with a separate script that shares no code with the package (plain csv reading and loops). Same flags and same counts for both rules.

## Predictions against results (2019)

| Rule | Measure | Predicted | Found | Met |
| --- | --- | --- | --- | --- |
| 3-day | Repairs found, of 7 | 2 or 3 | 3 | Yes |
| 3-day | Share of flags real | 50 to 80% | 100% (3 of 3) | No |
| 7-day | Repairs found, of 7 | 4 or 5 | 6 | No |
| 7-day | Share of flags real | Over 80% | 100% (6 of 6) | Yes |

## Observations, not tested claims

- The 3-day rule's three finds in 2019 were leaks of 17.9, 20.4 and 21.6 m3/h at repair. It missed leaks of 28.2, 26.2 and 26.5 m3/h. The drop it measured at the three it found (35.3 to 38.3 m3/h) is larger than the leak that was repaired.
- The 7-day rule's one miss in 2019 (p827, repaired 7 February) came six days after another repair (p523, 1 February). One flag was raised for the two.
- Neither rule raised a false flag in either year.
