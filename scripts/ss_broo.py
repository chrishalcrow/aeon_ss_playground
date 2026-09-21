from pathlib import Path
from datetime import datetime, timedelta
from broo_helper import make_and_run_python_script
from aeon_ss_playground.broo_parser import parse_args
import time

probe_name = "ProbeB"
shank_id = 2
sorter_protocol = "lupin_TM"
#sorter_protocol = "kilosort"

experiment = "abcEphys01"
start = datetime.strptime("2026-06-25 09:05:47", "%Y-%m-%d %H:%M:%S")
end = datetime.strptime("2026-06-26 10:00:00", "%Y-%m-%d %H:%M:%S")

#day_indices = [0,1,2,6,7]
#day_indices = [3,4,5,8]
day_indices = [9,10,11,12,13]

start = datetime.strptime("2026-06-26 04:00:00", "%Y-%m-%d %H:%M:%S")
end = datetime.strptime("2026-06-27 10:00:00", "%Y-%m-%d %H:%M:%S")

# 2026 07 06 12:00
experiment = "ProjectAeonOVC"
if experiment == "ProjectAeonOVC":
    start = datetime.strptime("2026-08-31 16:36:55", "%Y-%m-%d %H:%M:%S")
    #end = datetime.strptime("2026-08-31 16:36:55", "%Y-%m-%d %H:%M:%S")
    end = datetime.strptime("2026-09-02 19:17:41", "%Y-%m-%d %H:%M:%S")
    probe_name = "ProbeA"
    day_indices = [0]

if sorter_protocol in ['lupin', 'lupin_TM']:
    start_end_times = []
    for day_index in day_indices:
        day_start = start + timedelta(days=day_index)
        day_end = end + timedelta(days=day_index)
        start_end_times.append([day_start, day_end])
else:
    step = timedelta(minutes=30)
    start_end_times = []
    current = start
    while current < end:
        next_time = min(current + step, end)
        start_end_times.append([current.strftime("%Y-%m-%d %H:%M:%S"), next_time.strftime("%Y-%m-%d %H:%M:%S")])
        current += step

    start_end_times.append([start.strftime("%Y-%m-%d %H:%M:%S"), end.strftime("%Y-%m-%d %H:%M:%S")])

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
    cores=16
    output_folder =  Path(f"{experiment}/lupin_TM_si_output")

elif si_sorter_name == "lupin":
    gpu=False
    gpu_queue=True,
    cores=8
    output_folder =  Path(f"{experiment}/{probe_name}/ephys_block/")
else:
    raise ValueError('Unknown sorting protocol')

output_folder.mkdir(parents=True, exist_ok=True)

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
        hours=24*3,
        mem=64,
        cores=cores, 
        gpu=gpu, 
        gpu_queue=gpu_queue,
        aeon=True,
    )

    time.sleep(1.001)
