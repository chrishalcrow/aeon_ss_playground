import numpy as np
from pathlib import Path
import pandas as pd
from datetime import datetime, timezone, timedelta

data_folder = Path('/ceph/aeon/aeon/data/raw/AEONX1/ProjectAeonOVC/2026-08-31T160655Z/NeuropixelsV2/')

AP_data_list = list(data_folder.glob('NeuropixelsV2_ProbeA_AmplifierData_*'))

AP_data_list.sort(key=lambda p: int(p.stem.split("_")[-1]))

date_str = '2026-08-31T160655Z'

dt_naive = datetime.strptime(date_str, '%Y-%m-%dT%H%M%SZ')

starts = []
ends = []
paths = []
for filepath in AP_data_list:
    formatted_str = dt_naive.strftime('%Y-%m-%d %H:%M:%S')
    starts.append(formatted_str)
    dt_naive += timedelta(minutes=10)
    formatted_str = dt_naive.strftime('%Y-%m-%d %H:%M:%S')
    ends.append(formatted_str)
    paths.append(Path(*filepath.parts[-3:]))

all_path_df = pd.DataFrame(columns=['start','end','path'], data=np.array([starts,ends,paths]).T)
all_path_df.to_csv('rokas_paths.csv')
