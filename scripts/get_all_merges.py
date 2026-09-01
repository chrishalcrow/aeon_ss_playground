from pathlib import Path
import json
import spikeinterface.full as si

curation_decisions = {}

lupin_TM_path = Path("lupin_TM_si_output")
date_paths = list(lupin_TM_path.glob('2026*'))

for date_path in date_paths:

    print(f"doing {date_path}")

    try:
        analyzer_path = date_path / 'shank_2/analyzer'
        analyzer = si.load_sorting_analyzer(analyzer_path)

        merge_unit_groups = si.compute_merge_unit_groups(analyzer, preset='slay')
        curation_decisions[date_path.name] = merge_unit_groups

    except:
        continue

with open("all_merge_decisions.json", "w") as file:
    json.dump(curation_decisions, file, default=int, indent=4)