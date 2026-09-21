from pathlib import Path

import numpy as np
from spikeinterface.preprocessing.motion import save_motion_info
from aeon_ss_playground.broo_parser import peak_parse_args
from aeon_ss_playground.io import load_recording
import spikeinterface.full as si
from spikeinterface.core.time_series_tools import get_random_sample_slices

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

recording_raw = load_recording(root, start_time, end_time, probe_name="ProbeB", shank_id=shank_id, experiment_name = "abcEphys01")

si.set_global_job_kwargs(n_jobs=cores)

pp_rec = si.astype(
    si.common_reference(
        si.bandpass_filter(recording_raw),
    operator='average'),
dtype='float32')

slices = get_random_sample_slices(pp_rec, chunk_duration='300s', num_chunks_per_segment=144, seed=1205)

output_folder = Path(output_folder)
output_folder.mkdir(exist_ok=True)
np.save(output_folder / 'random_slices.npy', np.array(slices))

recs = []
for slice in slices:
    _, start_frame, end_frame = slice
    rec = pp_rec.frame_slice(start_frame=start_frame, end_frame=end_frame)
    recs.append(rec)

sliced_rec = si.concatenate_recordings(recs)

motion, motion_info = si.compute_motion(sliced_rec, output_motion_info=True, estimate_motion_kwargs={'rigid': True})

save_motion_info(motion_info, output_folder / 'sliced_motion_info', overwrite=True)


