from pathlib import Path
from datetime import datetime, timedelta
from broo_helper import make_and_run_python_script
from aeon_ss_playground.broo_parser import parse_args
import time

experiment = "abcEphys01"
probe_name = "ProbeB"
shank_id = 2
sorter_protocol = "lupin_TM"

start = datetime.strptime("2026-07-01 12:00:00", "%Y-%m-%d %H:%M:%S")
end = datetime.strptime("2026-07-06 12:00:00", "%Y-%m-%d %H:%M:%S")
# 2026 07 06 12:00
step = timedelta(minutes=30)

start_end_times = []
current = start
while current < end:
    next_time = min(current + step, end)
    start_end_times.append([current.strftime("%Y-%m-%d %H:%M:%S"), next_time.strftime("%Y-%m-%d %H:%M:%S")])
    current += step

si_sorter_name = sorter_protocol.split('_')[0]

if si_sorter_name == "dartsort":
    gpu=True
    gpu_queue=True
    cores=4
    output_folder =  Path("dartsort_native_output")

elif si_sorter_name == "kilosort":
    gpu=True
    gpu_queue=True
    cores=4
    output_folder =  Path("kilosort_si_output")

elif sorter_protocol == "lupin_TM":
    gpu=False
    gpu_queue=False
    cores=8
    output_folder =  Path("lupin_TM_si_output")

elif si_sorter_name == "lupin":
    gpu=False
    gpu_queue=False
    cores=8
    output_folder =  Path("lupin_si_output")


for start_time, end_time in start_end_times:

    python_arg = f"""scripts/spike_sort.py \
    --experiment {experiment} \
    --probe-name {probe_name} \
    --shank-id {shank_id} \
    --sorter-protocol {sorter_protocol} \
    --output-folder {output_folder} \
    --start-time "{start_time}" \
    --end-time "{end_time}" \
    --cores {cores} \
    """

    make_and_run_python_script(
        sorter_protocol, 
        python_arg, 
        hours=1,
        mem=64,
        cores=cores, 
        gpu=gpu, 
        gpu_queue=gpu_queue
    )


    time.sleep(1.001)
