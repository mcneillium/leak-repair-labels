"""Fetch the L-Town files the study uses from Zenodo record 4017659."""

import sys
import urllib.request
from pathlib import Path

RECORD = "https://zenodo.org/api/records/4017659/files"
FILES = [
    "2018_SCADA_Flows.csv",
    "2018_SCADA_Levels.csv",
    "2018_Leakages.csv",
    "2019_SCADA_Flows.csv",
    "2019_SCADA_Levels.csv",
    "2019_Leakages.csv",
    "2018_Fixed_Leakages_Report.txt",
    "dataset_configuration.yaml",
    "L-TOWN.inp",
]


def main(folder):
    folder = Path(folder)
    folder.mkdir(parents=True, exist_ok=True)
    for name in FILES:
        target = folder / name
        if target.exists():
            print("Already present:", name)
            continue
        urllib.request.urlretrieve(f"{RECORD}/{name}/content", target)
        print("Downloaded:", name, target.stat().st_size, "bytes")


if __name__ == "__main__":
    main(sys.argv[1])
