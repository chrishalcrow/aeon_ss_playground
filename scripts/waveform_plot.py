from datetime import datetime, timedelta
import spikeinterface.full as si
from pathlib import Path

import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation, PillowWriter


experiment = "abcEphys01"
probe_name = "ProbeB"
shank_id = 2
sorter_protocol = "lupin_TM"

start = datetime.strptime("2026-06-26 13:30:00", "%Y-%m-%d %H:%M:%S")
end = datetime.strptime("2026-06-27 12:00:00", "%Y-%m-%d %H:%M:%S")
# 2026 07 06 12:00
step = timedelta(minutes=30)

start_end_times = []
current = start
while current < end:
    next_time = min(current + step, end)
    start_end_times.append([current.strftime("%Y-%m-%d %H:%M:%S"), next_time.strftime("%Y-%m-%d %H:%M:%S")])
    current += step



# Shape: (time index, sample , channel ) -> 6 functions, each having 100 frames of 500 points
templates = []
for start, end in start_end_times:
    analyzer_path = Path(f'/run/user/1001/gvfs/smb-share:server=ceph-gw02.hpc.swc.ucl.ac.uk,share=scratch/chalcrow/fromgit/aeon_ss_playground/lupin_TM_si_output/{start.replace(" ", "T").replace(":", "-")}_{end.replace(" ", "T").replace(":", "-")}/shank_2/analyzer')
    analyzer = si.load_sorting_analyzer(analyzer_path, lazy=True)
    unit_index = analyzer.sorting.ids_to_indices([216])[0]
    channel_indicies = analyzer.channel_ids_to_indices([256,257,254,255,252,253])
    extremal_template = analyzer.get_extension('templates').get_data()[unit_index,:,channel_indicies]
    templates.append(extremal_template)



# 1. Setup sample data: 100 frames for each of the 6 functions
num_functions = 6
num_frames = 100

# 2. Setup 3x2 subplot grid
fig, axes = plt.subplots(3, 2, figsize=(12, 10), sharex=True, sharey=True)
axes_flat = axes.flatten()  # Flatten to 1D array for easy iteration

lines = []
subplot_titles = []

for k, ax in enumerate(axes_flat):
    ax.set_ylim(-50, 20)
    ax.grid(True, linestyle="--", alpha=0.5)

    # Line artist for each subplot
    (line,) = ax.plot(templates[0][0,:], lw=2)
    lines.append(line)

    # Per-subplot title
    title = ax.text(
        0.5, 1.03, "",
        transform=ax.transAxes,
        ha="center",
        va="bottom",
        fontsize=10,
        fontweight="bold"
    )
    subplot_titles.append(title)

fig.tight_layout()

# 3. Update function returning all lines and titles
def update(frame_idx):
    updated_artists = []
    for k in range(num_functions):
        lines[k].set_ydata(templates[frame_idx][k,:])
        subplot_titles[k].set_text(f"{times[frame_idx]}")
        updated_artists.extend([lines[k], subplot_titles[k]])
    return updated_artists

# 4. Save animation
anim = FuncAnimation(fig, update, frames=num_frames, blit=True)
writer = PillowWriter(fps=20)
anim.save("grid_functions_animation.gif", writer=writer)
plt.close(fig)