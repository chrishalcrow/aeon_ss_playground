from pathlib import Path
from datetime import datetime, timedelta
from broo_helper import make_and_run_python_script
import time as tiiiime
from datetime import datetime, time, timedelta

experiment = "abcEphys01"
probe_name = "ProbeB"
shank_id = 2

experiment_start = datetime.strptime("2026-06-25 09:05:47", "%Y-%m-%d %H:%M:%S")
experiment_end = datetime.strptime("2026-07-11 11:53:54", "%Y-%m-%d %H:%M:%S")

gpu=False
gpu_queue=False
cores=8
output_folder =  Path("detect_output")

# Total number of calendar days spanned
num_days = (experiment_end.date() - experiment_start.date()).days + 1

for i in range(num_days):
    current_date = experiment_start.date() + timedelta(days=i)

    # Standard midnight-to-midnight boundaries for the current calendar date
    day_midnight_start = datetime.combine(current_date, time.min)
    day_midnight_end = datetime.combine(current_date + timedelta(days=1), time.min)

    # Clip to experiment bounds
    start_time = max(day_midnight_start, experiment_start).strftime("%Y-%m-%d %H:%M:%S")
    end_time = min(day_midnight_end, experiment_end).strftime("%Y-%m-%d %H:%M:%S")

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

    tiiiime.sleep(1.001)
