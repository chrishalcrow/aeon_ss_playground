from pathlib import Path
from broo_helper import make_and_run_python_script
import time

experiment = "abcEphysPilot02"
probe_name = "ProbeB"
shank_ids = [3]
sorter_protocol = "lupin"

experiment_names = ['ProjectAeonOVC', 'abcEphys01', 'abcEphysPilot02', 'abcEphysPilot03', 'abcEphysPilot04', 'abcGolden01']
assert experiment in experiment_names, f"No experiment called {experiment}!!!"

si_sorter_name = sorter_protocol.split('_')[0]

start_end_indices =[
    [144*n,144*n + 180] for n in range(2,6)
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

print(gpu)
print(gpu_queue)


output_folder.mkdir(parents=True, exist_ok=True)

for shank_id in shank_ids:
    for count, (start_index, end_index) in enumerate(start_end_indices):

#        if count != 0:
        time.sleep(1.001)

        python_arg = f"""scripts/spike_sort.py \
        --experiment {experiment} \
        --probe-name {probe_name} \
        --shank-id {shank_id} \
        --sorter-protocol {sorter_protocol} \
        --output-folder {output_folder} \
        --start-index {start_index} \
        --end-index {end_index} \
        --cores {cores} \
        """

        make_and_run_python_script(
            sorter_protocol, 
            python_arg, 
            hours=48,
            mem=48,
            cores=cores, 
            gpu=gpu, 
            gpu_queue=gpu_queue,
            aeon=True,
        )
