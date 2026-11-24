# Reproduce the run

Clone the repository or extract the ZIP. From that folder, install the versions used for this run and run the commands below. Replace the quoted path with the folder containing the original CSV, YAML and text files from [Zenodo record 4017659](https://doi.org/10.5281/zenodo.4017659). Python 3.12 was used.

    python -m pip install numpy==2.5.5 pandas==2.2.3 PyYAML==6.0.3 pytest==9.2.0
    python -m pytest -q test_leak_rule.py
    python leak_rule.py "path/to/data" --output results

The supplied results/stages.txt contains the console output. The program writes results/study.json, including all 79 threshold scores for each window and the flag paired with each repair. A null flag means the repair was missed. Flows, thresholds and drops are in m³/h.

## Versions

The original run did not record its NumPy version, and the environment it used no longer exists. NumPy 2.5.5 is the version from my rerun on 24 November 2026, in a new conda environment with Python 3.12 on Windows and the other three versions above. That rerun passed all 6 tests and wrote `stages.txt` and `study.json` identical to the saved files, apart from Windows line endings. With this NumPy the tests print four `DeprecationWarning`s about timedelta units (lines 17, 36, 37 and 41 of `leak_rule.py`); they do not change any result.

## Protocol 2 seed assignments

The master demand seed is 20261124. Year seeds control the leaks. Offsets below correspond to consecutive seeds in ascending order within each row. The model seed is 42.

| Split | Year seeds | Demand offsets in whole weeks |
| --- | --- | --- |
| Training | 1001–1010 | 19, 7, 47, 20, 1, 23, 6, 39, 30, 13 |
| Development | 1011–1014 | 37, 33, 46, 12 |
| Final test | 1015–1020 | 34, 41, 14, 5, 26, 16 |
