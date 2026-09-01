from pathlib import Path
from datetime import datetime, timedelta
from broo_helper import make_and_run_python_script
import time

experiment = "abcEphys01"
probe_name = "ProbeB"
shank_id = 2

start = datetime.strptime("2026-06-25 09:05:47", "%Y-%m-%d %H:%M:%S")
end = datetime.strptime("2026-06-26 00:00:00", "%Y-%m-%d %H:%M:%S")

gpu=False
gpu_queue=False
cores=8
output_folder =  Path("dartsort_native_output")

start_time = start.strftime("%Y-%m-%d %H:%M:%S")
end_time = end.strftime("%Y-%m-%d %H:%M:%S")

python_arg = f"""scripts/detect_peaks.py \
--experiment {experiment} \
--probe-name {probe_name} \
--shank-id {shank_id} \
--output-folder {output_folder} \
--start-time "{start_time}" \
--end-time "{end_time}" \
--cores {cores} \
"""

make_and_run_python_script(
    "detect", 
    python_arg, 
    hours=4,
    mem=32,
    cores=cores, 
    gpu=gpu, 
    gpu_queue=gpu_queue
)

time.sleep(1.001)
