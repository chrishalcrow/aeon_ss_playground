from pathlib import Path
import matplotlib.pyplot as plt

import numpy as np
from spikeinterface.sortingcomponents.peak_detection import detect_peaks
from spikeinterface.sortingcomponents.peak_localization import localize_peaks
from spikeinterface.core import get_noise_levels
from spikeinterface.sortingcomponents.motion import estimate_motion
from spikeinterface.preprocessing.motion import save_motion_info
from aeon_ss_playground.broo_parser import peak_parse_args
from aeon_ss_playground.io import load_recording
import spikeinterface.full as si

args = peak_parse_args()

experiment = args.experiment
probe_name = args.probe_name
start_time = args.start_time
end_time = args.end_time
shank_id = args.shank_id
output_folder =  args.output_folder
cores = args.cores

if experiment == "abcEphys01":
    root = Path("/ceph/aeon/aeon/data/raw/AEONX1/abcEphys01")
else:
    raise FileNotFoundError('No root given!!!!')


from datetime import datetime
from pathlib import Path

peak_output_folder = output_folder / Path(f"{start_time:%Y-%m-%dT%H-%M-%S}_{end_time:%Y-%m-%dT%H-%M-%S}/shank_{shank_id}/peaks")

peaks = np.load(peak_output_folder / 'peaks.npy')
peak_locations = np.load(peak_output_folder / 'peak_locations.npy')

recording_raw = load_recording(root, start_time, end_time, probe_name="ProbeB", shank_id=shank_id)

si.set_global_job_kwargs(n_jobs=cores)

pp_rec = si.astype(
    si.common_reference(
        si.bandpass_filter(recording_raw),
    operator='average'),
dtype='float32')

print("about to estimate motion", flush=True)

motion = estimate_motion(pp_rec, peaks, peak_locations, resolution_mode='online', rigid=True, time_horizon_s=1_000)
#motion = estimate_motion(pp_rec, peaks, peak_locations, rigid=True)

print('about to make the motion info dict...', flush=True)

motion_info = dict(
    parameters={'sampling_frequency': 30_000},
    run_times={},
    peaks=peaks,
    peak_locations=peak_locations,
    motion=motion,
)

print('about to save motion info...', flush=True)

save_motion_info(motion_info, peak_output_folder / 'motion_info', overwrite=True)

print('and plot the result...', flush=True)

# and plot
fig = plt.figure(figsize=(14, 8))
si.plot_motion_info(
    motion_info,
    pp_rec,
    figure=fig,
    color_amplitude=True,
    amplitude_cmap="inferno",
    scatter_decimate=10000,
)
fig.savefig(peak_output_folder / f"motion_plot.png")

