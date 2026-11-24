# Log

Times are UTC. Everything down to "Observations, not tested claims" was written on 23 November 2026. Later entries carry their own dates. The commit times are the record where they differ.

## Decisions by Paul

1. Use the public L-Town benchmark for a leakage study, with results reported as a first look.
2. The rule: a step drop in night flow (02:00 to 04:00, tank filling removed), 3 days before against 3 days after, threshold chosen on 2018. A flag counts when it is within 2 days of a real repair.
3. Predictions for the 3-day rule on 2019: 2 or 3 of the 7 repairs found; 50 to 80% of flags real.
4. Amendment 1, after seeing 2018 only: keep the 3-day rule as primary and add a 7-day rule beside it.
5. Predictions for the 7-day rule on 2019: 4 or 5 of the 7 repairs found; over 80% of flags real.

Decisions 2 to 5 were made by choosing among options the assistant offered.

## Choices made by the assistant on 23 November

Kept as first recorded. Paul's decision on each, made on 24 November 2026, is in the entry of that date below.

- A1. Town inflow is `p227` plus `p235`, the two pipes leaving the reservoirs in `L-TOWN.inp`.
- A2. Tank filling is taken off as tank area times the rise in level between 02:00 and 04:00, divided by 2 hours. The level is recorded to 0.01 m, which is about 1 m3/h over the window.
- A3. One flag per step: a day is flagged only when its drop is the largest within one window either side.
- A4. Threshold grid 1.0 to 40.0 m3/h in steps of 0.5; highest F1 on 2018; a tie goes to the larger threshold.
- A5. Flags and repairs are matched one to one, nearest first.
- A6. A real repair is a leak whose end time is before the end of the dataset. Leaks that run to 31 December 2019, 23:55 are treated as never repaired.
- A7. Primary measure: repairs found in 2019. Secondary: share of flags that are real.
- A8. For the 2019 run the 2018 and 2019 flows are joined, so that drops in the first days of 2019 can use the last nights of 2018. A flag belongs to the year of its day.
- A9. The wording of the question and of the protocol.

## Work done by the assistant on 23 November

The first implementation (the `lrl` package, `scripts/` and `tests/`), the protocol text, this log and both runs. Runs were made on a cloud Linux machine with Python 3.13.18 and pandas 3.0.5. That implementation was replaced on 24 November (see below); the git history keeps it.

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

## 23 November 2026, later: re-run and a second implementation

- Morning: Paul re-ran the first implementation on his own machine and reported that his numbers matched (3 of 7 and 6 of 7 in 2019).
- Afternoon: the assistant wrote `leak-study-coding-brief.md`, which gives the rules and the check values for every stage and contains no code. Codex wrote a second implementation and six tests from it and ran them. Paul's run log for that run, in his words:

  > I supplied the coding brief with the rules and check values. The first implementation had been written with AI tools earlier on 23 November. For this run, Codex wrote a fresh implementation and six tests from the brief and ran them on 23 November 2026. The original implementation folders were not opened. This run produced a separate implementation for review. No repository replacement or publication update took place.

- Checked by the assistant the same afternoon: all six tests pass, every check value in the brief is reproduced, and one line of 144 (the `__main__` guard) is shared with the first implementation.

## 24 November 2026: the Codex implementation becomes the baseline

- 02:00. The assistant reran the Codex pack with the versions named in `RUN.md` (pandas 2.2.3, PyYAML 6.0.3, pytest 9.2.0; Python 3.13.18): 6 tests passed, and `results/stages.txt` and `results/study.json` came out identical to the saved files, byte for byte. Thresholds, the 79-row threshold curve for each window, flags and both repair tables equal the first implementation's.
- File reads, logged in order: `2018_SCADA_Flows.csv`, `2018_SCADA_Levels.csv`, `2018_Fixed_Leakages_Report.txt`; both thresholds fixed (34.5 and 10.0 m3/h); then `dataset_configuration.yaml`, the first file holding any 2019 record; then `2018_Leakages.csv`, the two 2019 SCADA files and `2019_Leakages.csv`. The first implementation's threshold step had opened `dataset_configuration.yaml` before fixing its thresholds, keeping only the 2018 rows.
- Paul's decision: keep the Codex implementation as the study's baseline, because it fixes both thresholds using the 2018 data before opening any file containing 2019 records. Commit `3e42797` removes the first implementation; commit `bdc2790` adds the Codex one with its saved output.
- Two differences in how the Codex version works, neither changing a result: it takes the 2018 repairs from `2018_Fixed_Leakages_Report.txt` and stops if they differ from the configuration file's; and the 16 m tank diameter is a constant taken from the brief, where the first implementation read it from `L-TOWN.inp`.
- The tests print four NumPy `DeprecationWarning`s about timedelta units (lines 17, 36, 37 and 41 of `leak_rule.py`) under pandas 2.2.3 with a recent NumPy. No result is affected. NumPy is not pinned in `RUN.md`.

### Paul's decisions on choices A1 to A9 (24 November 2026, sent at 01:54)

| Choice | Decision | Paul's reason and wording |
| --- | --- | --- |
| A1 | Confirmed | Inflow is `p227` plus `p235`. Both are reservoir feeds. Adding `PUMP_1` would count water moving inside the network again. |
| A2 | Confirmed | Keep the tank correction. The 1 m3/h is the change in the correction from a 0.01 m change in the level difference. The overall accuracy of the correction has not been measured. |
| A3 | Confirmed | Keep the local peak check, because one repair can produce several consecutive days above threshold. The condition is: the drop must be the largest within one window either side. That wording also covers equal peaks. |
| A4 | Confirmed | Keep the 79 thresholds, choose the best F1 on 2018 and take the higher threshold on a tie. The higher cutoff can give the same number of flags or fewer. Both tied ranges are recorded below. 34.5 and 10.0 m3/h stay as the baseline. The exploratory 2019 sweep across the tied ranges is left for now. |
| A5 | Confirmed | Keep the one-to-one matching within two days, closest pair first, with the existing ordering for ties (earlier flag, then earlier repair). Every repair and every flag is counted at most once. |
| A6 | Confirmed | A repair is counted when the leak ends before the dataset cutoff. The other 16 leaks are described as still open at the end of the observation period. |
| A7 | Confirmed | Lead with how many recorded repairs were found, then give the flag count and how many flags matched. With seven repairs in the test year, the counts stay visible. |
| A8 | Confirmed | Use late December 2018 to give the first January dates their full history, after the thresholds are fixed. The first retained 2019 flag was on 3 February (7-night rule). |
| A9 | Confirmed | The question, predictions, protocol and amendment stay as originally recorded. This dated entry records the confirmation. |

Tied ranges at the best 2018 F1 (from `results/study.json`):

- 3 nights: F1 0.8235 for every threshold from 29.5 to 34.5 m3/h (11 values). Chosen: 34.5.
- 7 nights: F1 0.8889 for every threshold from 4.0 to 10.0 m3/h (13 values). Chosen: 10.0.

How 2019 comes out elsewhere in those ranges has not been run.

## 24 November 2026, evening: draft of the next stage (assistant work)

- The assistant wrote `docs/protocol_02_draft.md` at Paul's request ("set up next stage of research"). It offers three sample questions, lists eight open choices (B1 to B8) and leaves the question, the choices and the predictions for Paul. Nothing in it is fixed. The assistant also added a short "Next stage" section to `README.md` pointing to the draft.
- The assistant ran two feasibility scripts, `sim/feasibility.py` and `sim/timing7.py`, with `wntr` 1.5.0. They load `L-TOWN.inp`, time EPANET and WNTR runs and add test leaks at arbitrary junctions. No night flow was computed, no rule was run and no real 2018 or 2019 record was opened. Timings are in the draft.

## 24 November 2026, night: protocol 2 draft, second version

- Paul proposed the question (option A, in his wording), the three-night rule as primary with the seven-night rule as a comparison, choices B1 to B8, a secondary measure, and two draft predictions (sent at 02:49). He asked that the predictions stay drafts until he confirms them, and said he will date and commit the final protocol himself.
- The assistant put these into `docs/protocol_02_draft.md` and added seven details marked "to confirm". The main one is a new choice B9: the public `L-TOWN.inp` repeats a one-week demand pattern, so simulated years need demand that varies or the rule may miss almost nothing. The draft B2 ranges were counted by the assistant from the 14 leaks that start in 2018 in `dataset_configuration.yaml`, with the 2019 rows skipped in code. No simulation was run.
- Paul's findings paragraph replaced the placeholder in `README.md`.

## 24 November 2026, 03:20: rerun on Paul's PC, and the NumPy version

- The original run's NumPy version was not recorded. Paul listed the packages in all eleven of his conda environments; none had pandas 2.2.3, PyYAML 6.0.3 and pytest 9.2.0 together, so the original environment no longer exists and its NumPy version cannot be recovered.
- The eight data files were copied to Paul's PC from the assistant's copy. All eight MD5 checksums equal those published on the Zenodo record.
- Paul made a new conda environment (`leak`, Python 3.12), installed pandas 2.2.3, PyYAML 6.0.3 and pytest 9.2.0 as in `RUN.md`, and ran the tests and the study. pip chose NumPy 2.5.5.
- Result, checked by the assistant from the files Paul's run wrote: 6 passed, 4 warnings; `stages.txt` and `study.json` identical to `results/` byte for byte once Windows line endings are removed.
- `RUN.md` now pins NumPy 2.5.5 and says it is the rerun's version, not the original's.

## 24 November 2026, 03:25: `L-TOWN_Real.inp` checked for protocol 2 (assistant work)

- Downloaded from Zenodo record 4017659 (177 MB, MD5 `40fb38de25ed692a5ddd30e0f5fae332`, equal to the record's). Not added to the repository.
- Read only, nothing simulated: same layout as `L-TOWN.inp`, all 905 pipes with different length, diameter and roughness, and 104 demand patterns covering 365 days at 5-minute steps. Added as option (d) under B9 in `docs/protocol_02_draft.md`, for Paul to decide.

## 24 November 2026, 03:33 to 03:45: B9 decided, and the real network timed

- Paul decided B9 at 03:33: use `L-TOWN_Real.inp`; give each simulated year a distinct, seed-selected whole-week offset; before any study year, measure the absolute change in leak-free night flow across the join, smooth it if it exceeds 5 m3/h and recheck; report the simulated-against-published 2018 night-flow difference with no pass or fail cutoff. The assistant recorded these in `docs/protocol_02_draft.md` (third version). His predictions and the remaining choices are still open for his review.
- At his request the assistant ran `sim/timing_real.py`: one week of `L-TOWN_Real.inp` in WNTR's pressure-driven simulator with no leak (41.6 s) and with one test leak (42.1 s); loading took 5.5 s. Neither run was scored and no night flow was computed.

## 24 November 2026 at 03:40 UK time. Protocol 2 finalised before scoring

At Paul's request, Codex finalised and committed the protocol from draft 41a32f0. The final document records the 2018-based leak ranges, calendar and growing-leak rules, model features and development selection, frozen week assignments and a 24-hour demand crossfade with a 5 m³/h recheck. Codex retained Paul's original two prediction ranges after reviewing B9. The seed assignment was reproduced without running hydraulics. No study years were generated or scored during finalisation.

## 24 November 2026 at 03:43 UK time: predictions confirmed by Paul

After the protocol commit `5df22c2`, Paul confirmed both predictions himself, unchanged: of the true repairs the three-night rule misses in the six test years, its model will also miss 60 to 85%, pooled across the years; and the three-night model will raise 0 to 3 unmatched flags per test year on average. Keeping the ranges after B9 was his decision. In his words: more variable demand could mean the three-night rule misses more repairs, but that does not tell him whether the model will miss a bigger or smaller share of those same repairs. At 03:45 he also confirmed the detail Codex specified at finalisation (leaks at pipe midpoints, growing leaks stepped up by area each day, the logistic regression settings with standardisation on the training years only, `p232` for the 2018 comparison, seed `1000` kept separate) and Check 0 as written, with all 20 full-year leak-free runs. No amendment to the protocol. This note was written by the assistant from Paul's messages. No study year has been generated.
