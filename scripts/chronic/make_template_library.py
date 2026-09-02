from pathlib import Path
from aeon_ss_playground.lupin import make_template_library
import spikeinterface.full as si

shank_id = 2

# modify for where you want to put the output
output_folder = Path('')
global_info_folder = output_folder / f'shank_{shank_id}/global_info'
global_info_folder.mkdir(parents=True, exist_ok=True)

recording_paths = [
    'rec_1',
    'rec_2',
]

recordings = []
for recording_path in recording_paths:
    recording = si.read_spikeglx(recording_path).split_by('group')[shank_id]
    recordings.append(recording)

all_recordings = si.concatenate_recordings(recordings)

templates_folder = global_info_folder / f"templates_shank_{shank_id}.zarr"
make_template_library(all_recordings, templates_folder)
