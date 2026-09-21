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

DATE_FORMAT = "%Y-%m-%dT%H-%M-%S"


def parse_interval(folder_name: str) -> tuple[datetime, datetime]:
    """Parse folder name 'START_END' into datetime objects."""
    start_str, end_str = folder_name.split("_")
    return datetime.strptime(start_str, DATE_FORMAT), datetime.strptime(
        end_str, DATE_FORMAT
    )


def list_directories_up_to(folder_path: str | Path, end_input: str) -> list[Path]:
    target_end = datetime.strptime(end_input, DATE_FORMAT)
    base_dir = Path(folder_path)

    matched = []
    # Iterate through subdirectories only
    for path in sorted(base_dir.iterdir()):
        if not path.is_dir():
            continue

        try:
            start_dt, end_dt = parse_interval(path.name)
        except ValueError:
            continue  # Skip any folders that don't match the format

        # Include directories where the folder starts before the target end time
        if start_dt < target_end:
            matched.append(path)

    return matched

user_end_date = "2026-07-11T11-53-54"
results = list_directories_up_to('detect_output', user_end_date)

print(results, flush=True)

all_peaks = []
all_peak_locations = []

for one_dir in results:

    peak_output_folder = Path(one_dir) / f"shank_{shank_id}/peaks"
    all_peaks.append(np.load(peak_output_folder / 'peaks.npy'))
    all_peak_locations.append(np.load(peak_output_folder / 'peak_locations.npy'))

peaks = np.concat(all_peaks)
peak_locations = np.concat(all_peak_locations)

print("Got all peaks!", flush=True)

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

save_motion_info(motion_info, 'all_motion_info', overwrite=True)

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

