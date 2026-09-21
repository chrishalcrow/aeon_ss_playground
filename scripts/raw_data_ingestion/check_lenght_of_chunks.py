from pathlib import Path
import datetime

import pandas as pd
import numpy as np
import probeinterface as pi 
import spikeinterface as si

experiment_name = 'ProjectAeonOVC'

root = Path(f"/ceph/aeon/aeon/data/raw/AEONX1/{experiment_name}")

probe_name = 'ProbeA'

sampling_frequency = 30_000
gain_to_uV = 3.05176
offset_to_uV = -2048 * gain_to_uV

if experiment_name == 'ProjectAeonOVC':
    path_to_ephys_paths = Path("rokas_paths.csv")
    if probe_name == 'ProbeA':
        path_to_probe = Path("probe_output_test.json")
else:
    if probe_name == "ProbeB":
        path_to_ephys_paths = Path("abcEphys01_B_ephys_paths.csv")
        path_to_probe = Path("/ceph/aeon/aeon/data/raw/AEONX1/abcEphys01/2026-06-25T090547Z/M01_ProbeB_4Shanks_2000_to_2700um_LFP.json")
    elif probe_name == "ProbeA":
        path_to_ephys_paths = Path("abcEphys01_ephys_paths.csv")
        path_to_probe = Path("/ceph/aeon/aeon/data/raw/AEONX1/abcEphys01/2026-06-25T090547Z/M01_ProbeA_4Shanks_1500_to_2200um.json")


paths = pd.read_csv(path_to_ephys_paths, parse_dates=["start", "end"])

probe = pi.read_probeinterface(path_to_probe)

for ephys_path in paths["path"]:

    rec = si.read_binary(
        root / ephys_path,
        sampling_frequency=30_000,
        dtype=np.uint16,
        num_channels=384,
        gain_to_uV=gain_to_uV,
        offset_to_uV=offset_to_uV,
    )

    if rec.get_num_samples() != 18000000:
        print(f"{ephys_path} has {rec.get_num_samples()} samples.")
        
