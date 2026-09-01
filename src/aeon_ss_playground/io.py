import datetime
import pandas as pd
from pathlib import Path
import numpy as np

import probeinterface as pi
import spikeinterface.full as si

from spikeinterface.core.base import base_period_dtype
from spikeinterface.core.generate import MockRecording

def generate_mock_zero_recording(rec_to_mock: si.BaseRecording, total_frames, probe):

    rec_with_probe = rec_to_mock.select_channels_with_probe(probe.probes[0])
    sampling_frequency = rec_to_mock.sampling_frequency
    recording = MockRecording(
        durations = [total_frames/sampling_frequency],
        sampling_frequency = sampling_frequency,
        num_channels = rec_to_mock.get_num_channels(),
    )
    silence_periods = np.array([(0, 0, recording.get_num_samples())], dtype=base_period_dtype)
    recording.set_probegroup(rec_with_probe.get_probegroup())
    zero_recording = si.silence_periods(si.astype(recording, dtype=rec_to_mock.dtype), periods=silence_periods)
    zero_recording._main_ids = rec_to_mock._main_ids
    return zero_recording

def load_recording(
        root: Path, 
        start: datetime.datetime, 
        end: datetime.datetime, 
        shank_id: None | int = None, 
        probe_name: str = "ProbeB",
        all_channels=True,
    ) -> si.BaseRecording:

    sampling_frequency = 30_000
    gain_to_uV = 3.05176
    offset_to_uV = -2048 * gain_to_uV

    if probe_name == "ProbeB":
        path_to_ephys_paths = Path("abcEphys01_B_ephys_paths.csv")
        path_to_probe = Path("/ceph/aeon/aeon/data/raw/AEONX1/abcEphys01/2026-06-25T090547Z/M01_ProbeB_4Shanks_2000_to_2700um_LFP.json")
    if probe_name == "ProbeA":
        path_to_ephys_paths = Path("abcEphys01_A_ephys_paths.csv")
        path_to_probe = Path("/ceph/aeon/aeon/data/raw/AEONX1/abcEphys01/2026-06-25T090547Z/M01_ProbeA_4Shanks_1500_to_2200um.json")

    paths = pd.read_csv(path_to_ephys_paths, parse_dates=["start", "end"])

    start_index = max(0,int(paths["start"].searchsorted(start) - 1))
    end_index = int(paths["end"].searchsorted(end)+1)

    print(f"{start_index=}")
    print(f"{end_index=}")
   

    ephys_paths: np.ndarray[str] = paths.iloc[start_index:end_index]["path"].values
    print(ephys_paths)

    paths_start_time: datetime.datetime = pd.to_datetime(paths.iloc[start_index]["start"])
    paths_end_time: datetime.datetime = pd.to_datetime(paths.iloc[end_index-1]["end"])

    time_difference = start - paths_start_time
    start_frame = round(time_difference.total_seconds() * sampling_frequency)

    end_time = end - paths_start_time
    end_frame = round(end_time.total_seconds() * sampling_frequency)

    print(f"{start=}, {paths_start_time=}, {end_time=}, {end=}")

    probe = pi.read_probeinterface(path_to_probe)

    recs: list[si.BaseRecording] = []
    for path_index, ephys_path in zip(range(start_index, end_index), ephys_paths, strict=True):

#        print(path_index, ephys_path, flush=True)

        path_start_time: datetime.datetime = pd.to_datetime(paths.loc[path_index]["start"])
        path_end_time: datetime.datetime = pd.to_datetime(paths.loc[path_index]["end"])
        expected_num_frames = int((path_end_time - path_start_time).total_seconds() * sampling_frequency)
        
        if ephys_path == 'blank':
            rec_to_mock = recs[0]
            rec = generate_mock_zero_recording(rec_to_mock, expected_num_frames, probe)
        else:
            resolved_path = root / Path(ephys_path)
            rec = si.unsigned_to_signed(si.read_binary(
                resolved_path,
                sampling_frequency=30_000,
                dtype=np.uint16,
                num_channels=384,
                gain_to_uV=gain_to_uV,
                offset_to_uV=offset_to_uV,
            ))
            if rec.get_num_samples() != 18_000_000:
                print(f"{rec.get_num_samples()=}")
            # rec should be 10 mins but it's missing some samples...
            if expected_num_frames == 18_000_000 and rec.get_num_samples() != expected_num_frames:
                print(f"{expected_num_frames=}")
                print(f"{paths_end_time=}")
                print(f"{paths_start_time=}")
                print(ephys_path, flush=True)
                remaining_rec = generate_mock_zero_recording(rec_to_mock=rec, total_frames=(expected_num_frames - rec.get_num_samples()), probe=probe)
                rec = si.concatenate_recordings([rec, remaining_rec])
                print(rec.get_num_samples())            
        recs.append(rec)
        
    rec: si.BaseRecording = si.concatenate_recordings(recs)

    rec: si.BaseRecording = rec.frame_slice(start_frame=start_frame, end_frame=end_frame)
    rec.set_probegroup(probegroup=probe, in_place=True)
    
    if not all_channels:
        y_locations = rec.get_channel_locations()[:,1]
        good_channel_mask = (y_locations < 3000) | (y_locations > 1800)
        good_channel_ids = rec.channel_ids[good_channel_mask]
        middle_rec = rec.select_channels(channel_ids=good_channel_ids)
    else:
        middle_rec = rec

    if shank_id is None:
        return middle_rec
    else:
        one_shank_recording = middle_rec.split_by('group')[shank_id]
        return one_shank_recording
