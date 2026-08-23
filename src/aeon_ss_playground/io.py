import datetime
import pandas as pd
from pathlib import Path
import numpy as np

import probeinterface as pi
import spikeinterface as si

def load_recording(
        root: Path, 
        start: datetime.datetime, 
        end: datetime.datetime, 
        shank_id: None | int = None, 
        probe_name: str = "ProbeB",
    ) -> si.BaseRecording:

    sampling_frequency = 30_000
    gain_to_uV = 3.05176
    offset_to_uV = -2048 * gain_to_uV

    if probe_name == "ProbeB":
        path_to_ephys_paths = Path("abcEphys01_B_ephys_paths.csv")
        path_to_probe = Path("/ceph/aeon/aeon/data/raw/AEONX1/abcEphys01/2026-06-25T090547Z/M01_ProbeB_4Shanks_2000_to_2700um_LFP.json")

    paths = pd.read_csv(path_to_ephys_paths, parse_dates=["start", "end"])

    start_index = int(paths["start"].searchsorted(start) - 1)
    end_index = int(paths["end"].searchsorted(end) + 1)

    ephys_paths: np.ndarray[str] = paths.iloc[start_index:end_index]["path"].values
    paths_start_time: datetime.datetime = paths.iloc[start_index]["start"]

    time_difference = start - paths_start_time
    start_frame = round(time_difference.total_seconds() * sampling_frequency)

    end_time = end - paths_start_time
    end_frame = round(end_time.total_seconds() * sampling_frequency)

    probe = pi.read_probeinterface(path_to_probe)

    recs: list[si.BaseRecording] = []
    for ephys_path in ephys_paths:
        resolved_path = root / Path(ephys_path)
        recs.append(
            si.read_binary(
                resolved_path,
                sampling_frequency=30_000,
                dtype=np.uint16,
                num_channels=384,
                gain_to_uV=gain_to_uV,
                offset_to_uV=offset_to_uV,
            )
        )

    rec: si.BaseRecording = si.concatenate_recordings(recs)

    rec: si.BaseRecording = rec.frame_slice(start_frame=start_frame, end_frame=end_frame)
    rec.set_probegroup(probegroup=probe, in_place=True)

    y_locations = rec.get_channel_locations()[:,1]
    good_channel_mask = (y_locations < 3000) | (y_locations > 1800)
    good_channel_ids = rec.channel_ids[good_channel_mask]
    middle_rec = rec.select_channels(channel_ids=good_channel_ids)

    if shank_id is None:
        return middle_rec
    else:
        one_shank_recording = middle_rec.split_by('group')[shank_id]
        return one_shank_recording
