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

do_blackbox_sorting = True

if experiment == "ProjectAeonOVC":
    root = Path("/ceph/aeon/aeon/data/raw/AEONX1/ProjectAeonOVC")
    use_blocks=False
if experiment == "abcEphys01":
    root = Path("/ceph/aeon/aeon/data/raw/AEONX1/abcEphys01")
    use_blocks=True

si_sorter_name = sorter_protocol.split('_')[0]

sorter_output_folder = output_folder / Path(f"{start_time:%Y-%m-%dT%H-%M-%S}_{end_time:%Y-%m-%dT%H-%M-%S}/shank{shank_id}")
sorter_output_folder.mkdir(parents=True, exist_ok=True)

print(f"{start_time=}")
print(f"{end_time=}")

rec = load_recording(root, start_time, end_time, probe_name=probe_name, shank_id=shank_id, experiment_name=experiment, use_blocks=use_blocks)
print(rec)

si.set_global_job_kwargs(n_jobs=cores)

if sorter_protocol == "lupin_T":
    from aeon_ss_playground.lupin import make_template_library

    templates_folder = sorter_output_folder / "templates.zarr"

    make_template_library(rec, templates_folder)

    quit()

elif sorter_protocol == "lupin_TM":
    from aeon_ss_playground.lupin import do_template_matching

    #templates_folder = Path("/ceph/scratch/chalcrow/fromgit/aeon_ss_playground/lupin_si_output/2026-06-26T12-00-00_2026-06-27T12-00-00/shank_2/templates.zarr")
    #templates_folder = Path("/ceph/scratch/chalcrow/fromgit/aeon_ss_playground/lupin_si_output/2026-06-26T12-00-00_2026-07-06T12-00-00/shank_2/templates.zarr")
    templates_folder = Path("/ceph/scratch/chalcrow/fromgit/aeon_ss_playground/ProjectAeonOVC/lupin_si_output/2026-08-31T16-06-55_2026-09-02T19-17-41/shank_2/templates.zarr")

    old_analyzer: si.SortingAnalyzer = do_template_matching(rec, templates_folder, sorter_output_folder)
    preprocessed_recording_for_analyzer = old_analyzer._recording
    sorting = old_analyzer.sorting

    do_blackbox_sorting = False

if do_blackbox_sorting:

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

    elif si_sorter_name == "kilosort4":

        sorter_output = sorter_output_folder / 'kilosort4_si_output'
        sorting = si.run_sorter(sorter_name=si_sorter_name, recording=rec, do_correction=False, use_binary_file=False, verbose=True, remove_existing_folder=True, folder=sorter_output, Th_learned=8)
        
    elif si_sorter_name == "lupin":

        sorter_output = sorter_output_folder / f'lupin_000/lupin_si_output'

        print(f"{sorter_output=}")
        if sorter_output.is_dir():
            sorting = si.load(sorter_output)
        else:
            sorting = si.run_sorter(sorter_name=si_sorter_name, recording=rec, apply_motion_correction=False, verbose=True, remove_existing_folder=True, folder=sorter_output)

    preprocessed_recording_for_analyzer = si.common_reference(si.bandpass_filter(rec))

lupin_folder = sorter_output_folder / f"{si_sorter_name}_000/"
lupin_folder.mkdir(parents=True, exist_ok=True)

analyzer = si.create_sorting_analyzer(
    sorting = sorting,
    recording = preprocessed_recording_for_analyzer,
    folder = lupin_folder / "sorting_analyzer",
    format = "binary_folder",
    peak_sign = "both",
    radius_um = 70,
)

analyzer.compute(generic_postprocessing)
