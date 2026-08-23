import argparse
import pandas as pd
from pathlib import Path

def parse_args():
    parser = argparse.ArgumentParser(
        description="Run spike sorting and electrophysiology analysis."
    )

    parser.add_argument(
        "--experiment",
        type=str,
        required=True,
        help="Experiment identifier",
    )
    parser.add_argument(
        "--probe-name",
        type=str,
        required=True,
        help="Name of the probe",
    )
    parser.add_argument(
        "--start-time",
        type=pd.to_datetime,
        required=True,
        help="Start datetime in ISO format or parseable string",
    )
    parser.add_argument(
        "--end-time",
        type=pd.to_datetime,
        required=True,
        help="End datetime in ISO format or parseable string",
    )
    parser.add_argument(
        "--sorter-protocol",
        type=str,
        required=True,
        help="Name of the sorter to run",
    )
    parser.add_argument(
        "--output-folder",
        type=Path,
        required=True,
        help="Directory path for saving outputs",
    )
    parser.add_argument(
        "--shank-id",
        type=int,
        default=None,
        help="Shank ID integer (optional, default: %(default)s)",
    )

    return parser.parse_args()