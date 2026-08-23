from pathlib import Path

from aeon_ss_playground.broo_parser import parse_args
from aeon_ss_playground.io import load_recording

args = parse_args()

experiment = args.experiment
probe_name = args.probe_name
start_time = args.start_time
end_time = args.end_time
shank_id = args.shank_id
sorter_protocol = args.sorter_protocol
output_folder =  args.output_folder

if experiment == "abcEphys01":
    root = Path("/ceph/aeon/aeon/data/raw/AEONX1/abcEphys01")

si_sorter_name = sorter_protocol.split('_')[0]

sorter_output_folder = output_folder / Path(f"{start_time:%Y-%m-%dT%H-%M-%S}_{end_time:%Y-%m-%dT%H-%M-%S}/shank_{shank_id}")
sorter_output_folder.mkdir(parents=True)

rec = load_recording(root, start_time, end_time, probe_name="ProbeB", shank_id=shank_id)

import dartsort

if si_sorter_name == "dartsort":

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

