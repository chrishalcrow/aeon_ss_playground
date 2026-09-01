from pathlib import Path
from aeon_ss_playground.lupin import do_template_matching
import spikeinterface.full as si

output_folder = Path('')
global_info_folder = output_folder / 'global_info'

recording_paths = [
    '',
]

recording_path = recording_paths[0]
recording = si.read_spikeglx(recording_path)

templates_folder = global_info_folder / "templates.zarr"

sorter_output_folder = output_folder / 'rec_1'

old_analyzer: si.SortingAnalyzer = do_template_matching(recording, templates_folder, sorter_output_folder)
preprocessed_recording_for_analyzer = old_analyzer._recording
sorting = old_analyzer.sorting

analyzer = si.create_sorting_analyzer(
    sorting=sorting,
    recording=preprocessed_recording_for_analyzer,
    folder=sorter_output_folder / "analyzer",
    format="binary_folder",
    peak_sign="both",
    radius_um=70,
)

generic_postprocessing = {
    "unit_locations": {},
    "random_spikes": {},
    "noise_levels": {},
    "waveforms": {},
    "templates": {},
    "spike_amplitudes": {},
    "amplitude_scalings": {},
    "isi_histograms": {},
    "spike_locations": {},
    "correlograms": {},
    "template_similarity": {},
    "quality_metrics": {},
    "template_metrics": {},
}

analyzer.compute(generic_postprocessing)

