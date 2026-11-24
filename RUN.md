# Reproduce the run

Extract the ZIP. From that folder, install the versions used for this run and run the commands below. Replace the quoted path with the folder containing the original CSV, YAML and text files from [Zenodo record 4017659](https://doi.org/10.5281/zenodo.4017659). Python 3.12 was used.

    python -m pip install pandas==2.2.3 PyYAML==6.0.3 pytest==9.2.0
    python -m pytest -q test_leak_rule.py
    python leak_rule.py "path/to/data" --output results

The supplied results/stages.txt contains the console output. The program writes results/study.json, including all 79 threshold scores for each window and the flag paired with each repair. A null flag means the repair was missed. Flows, thresholds and drops are in m³/h.
