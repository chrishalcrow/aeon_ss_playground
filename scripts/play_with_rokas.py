from pathlib import Path
from aeon_ss_playground.io import load_recording
from datetime import datetime

root = Path("/ceph/aeon/aeon/data/raw/AEONX1/ProjectAeonOVC")

start = datetime.strptime('2026-08-31 16:06:55', '%Y-%m-%d %H:%M:%S')
end = datetime.strptime("2026-09-02 19:17:42", "%Y-%m-%d %H:%M:%S")

rec = load_recording(
    root=root,
    start=start,
    end=end,
    probe_name='ProbeA',
    experiment_name='ProjectAeonOVC',
    shank_id=2,
)




