from pathlib import Path

import numpy as np
from spikeinterface.sortingcomponents.peak_detection import detect_peaks
from spikeinterface.sortingcomponents.peak_localization import localize_peaks
from spikeinterface.core import get_noise_levels

from aeon_ss_playground.broo_parser import parse_args
from aeon_ss_playground.io import load_recording
import spikeinterface.full as si

args = parse_args()

experiment = args.experiment
probe_name = args.probe_name
start_time = args.start_time
end_time = args.end_time
shank_id = args.shank_id
output_folder =  args.output_folder
cores = args.cores

if experiment == "abcEphys01":
    root = Path("/ceph/aeon/aeon/data/raw/AEONX1/abcEphys01")

peak_output_folder = output_folder / Path(f"{start_time:%Y-%m-%dT%H-%M-%S}_{end_time:%Y-%m-%dT%H-%M-%S}/shank_{shank_id}/peaks")
peak_output_folder.mkdir(parents=True, exist_ok=True)

recording_raw = load_recording(root, start_time, end_time, probe_name="ProbeB", shank_id=shank_id)
si.set_global_job_kwargs(n_jobs=cores)

num_chans = recording_raw.get_num_channels()
sampling_frequency = recording_raw.get_sampling_frequency()

pp_rec = si.astype(si.common_reference(si.bandpass_filter(recording_raw)), dtype='float32')

noise_levels = get_noise_levels(pp_rec, return_in_uV=False)

detection_params = {
    "peak_sign": "neg",
    "detect_threshold": 8,
    "exclude_sweep_ms": 0.8,
    "radius_um": 80.0,
    "noise_levels": noise_levels,
}

peaks = detect_peaks(
    pp_rec, method="locally_exclusive", method_kwargs=detection_params,
)
peak_locations = localize_peaks(pp_rec, peaks, method='grid_convolution')

np.save(peak_output_folder / 'peaks.npy', peaks)
np.save(peak_output_folder / 'peak_locations.npy', peak_locations)
