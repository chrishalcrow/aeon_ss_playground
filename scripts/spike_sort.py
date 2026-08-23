from pathlib import Path

from aeon_ss_playground.broo_parser import parse_args
from aeon_ss_playground.io import load_recording
import spikeinterface.full as si

args = parse_args()

experiment = args.experiment
probe_name = args.probe_name
start_time = args.start_time
end_time = args.end_time
shank_id = args.shank_id
sorter_protocol = args.sorter_protocol
output_folder =  args.output_folder
cores = args.cores

if experiment == "abcEphys01":
    root = Path("/ceph/aeon/aeon/data/raw/AEONX1/abcEphys01")

si_sorter_name = sorter_protocol.split('_')[0]

sorter_output_folder = output_folder / Path(f"{start_time:%Y-%m-%dT%H-%M-%S}_{end_time:%Y-%m-%dT%H-%M-%S}/shank_{shank_id}")
sorter_output_folder.mkdir(parents=True, exist_ok=True)

rec = load_recording(root, start_time, end_time, probe_name="ProbeB", shank_id=shank_id)
si.set_global_job_kwargs(n_jobs=cores)

if si_sorter_name == "dartsort":

    import dartsort

    tmp_dir = Path("dartsort_tempo_4")
    tmp_dir.mkdir(exist_ok=True)

    dartsort_result = dartsort.dartsort(
        rec,
        sorter_output_folder,
        cfg=dartsort.DARTsortUserConfig(
            preprocessing="ibllikecmr",
            do_motion_estimation=False,
            save_intermediates=True,
            tmpdir_parent=str(tmp_dir),
            copy_recording_to_tmpdir="yes",
            work_in_tmpdir=True,
        ),
    )

elif si_sorter_name == "kilosort":

    sorter_output = sorter_output_folder / 'kilosort_si_output'
    sorting = si.run_sorter(sorter_name=si_sorter_name, recording=rec, do_correction=False, use_binary_file=False, verbose=True, remove_existing_folder=True, folder=sorter_output)
    
elif si_sorter_name == "lupin":

    sorter_output = sorter_output_folder / 'lupin_si_output'
    sorting = si.run_sorter(sorter_name=si_sorter_name, recording=rec, apply_motion_correction=False, verbose=True, remove_existing_folder=True, folder=sorter_output)

preprocessed_recording_for_analyzer = si.common_reference(si.bandpass_filter(si.unsigned_to_signed(rec)))

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
