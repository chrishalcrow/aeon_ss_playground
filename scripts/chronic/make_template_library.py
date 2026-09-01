from pathlib import Path
from aeon_ss_playground.lupin import make_template_library
import spikeinterface.full as si

output_folder = Path('')
global_info_folder = output_folder / 'global_info'

recording_paths = [
    '',
]

recordings = []
for recording_path in recording_paths:
    recording = si.read_spikeglx(recording_path)
    recordings.append(recording)

all_recordings = si.concatenate_recordings(recordings)

templates_folder = global_info_folder / "templates.zarr"
make_template_library(all_recordings, templates_folder)

