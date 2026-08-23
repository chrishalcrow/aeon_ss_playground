from pathlib import Path

from broo_helper import make_and_run_python_script
from aeon_ss_playground.broo_parser import parse_args


experiment = "abcEphys01"
probe_name = "ProbeB"
shank_id = 2
sorter_protocol = "dartsort_A"

si_sorter_name = sorter_protocol.split('_')[0]

if si_sorter_name == "dartsort":
    output_folder =  Path("dartsort_native_output")
    gpu=True
    gpu_queue=True
    cores=4

elif si_sorter_name == "kilosort":
    gpu=True
    gpu_queue=True
    cores=4
    output_folder =  Path("kilosort_si_output")

elif si_sorter_name == "lupin":
    gpu=False
    gpu_queue=False
    cores=8

    output_folder =  Path("lupin_si_output")

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
    mem=64, 
    cores=cores, 
    gpu=gpu, 
    gpu_queue=gpu_queue
)