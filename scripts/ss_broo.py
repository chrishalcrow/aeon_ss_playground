from pathlib import Path

from broo_helper import make_and_run_python_script
from aeon_ss_playground.broo_parser import parse_args


experiment = "abcEphys01"
probe_name = "ProbeB"
shank_id = 2
sorter_protocol = "dartsortA"
output_folder =  Path("dartsort_native_output")

start_end_times = [
    ["2026-06-26 00:00:00", "2026-06-26 12:00:00"],
]

start_time, end_time = start_end_times[0]

python_arg = f"""spike_sort.py \
--experiment {experiment} \
--probe-name {probe_name} \
--shank-id {shank_id} \
--sorter-protocol {sorter_protocol} \
--output-folder {output_folder} \
--start-time "{start_time}" \
--end-time "{end_time}" \
"""

make_and_run_python_script(
    "spike_sort", 
    python_arg, 
    hours=24, 
    cores=8, 
    mem=64, 
    gpu=False, 
    gpu_queue=False
)