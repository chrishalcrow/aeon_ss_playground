from pathlib import Path
from broo_helper import make_and_run_python_script
import time

experiment = "abcEphys01"
probe_name = "ProbeB"
shank_id = 2
sorter_protocol = "lupin"

si_sorter_name = sorter_protocol.split('_')[0]

start_end_indices =[
    [0,1]
]

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

for start_index, end_index in start_end_indices:

    python_arg = f"""scripts/spike_sort.py \
    --experiment {experiment} \
    --probe-name {probe_name} \
    --shank-id {shank_id} \
    --sorter-protocol {sorter_protocol} \
    --output-folder {output_folder} \
    --start-index "{start_index}" \
    --end-index "{end_index}" \
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
