from pathlib import Path
import spikeinterface as si

old_existing_max = 1

lupin_TM_path = Path("lupin_TM_si_output")
date_paths = list(lupin_TM_path.glob('2026*'))

for date_path in date_paths:

    analyzer_path = date_path / 'shank_2/analyzer'
    try:
        analyzer = si.load_sorting_analyzer(analyzer_path, load_extensions=False, lazy=True)
    
        existing_max = max(old_existing_max, max(analyzer.unit_ids))
        if existing_max > old_existing_max:
            print(existing_max)
            old_existing_max = existing_max

    except:
        continue

print(existing_max)

