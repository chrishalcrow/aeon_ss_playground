from pathlib import Path
import spikeinterface as si
import numpy as np
import datetime

global_merge_unit_groups = [
    [243, 245],
    [174, 178, 317],
    [190, 192],
    [151, 155],
    [181, 322],
    [165, 171],
    [199, 327],
    [238, 240],
    [125, 299],
    [276, 281],
    [173, 316],
    [113, 293],
    [123, 348, 349],
    [262, 269],
    [104, 109],
    [141, 146, 148],
    [108, 294, 295],
]

max_unit = 355

global_new_unit_ids = (max_unit + 1) + np.arange(len(global_merge_unit_groups)).astype('int')

lupin_TM_path = Path("lupin_TM_si_output")
date_paths = list(lupin_TM_path.glob('2026*'))

for date_path in date_paths:
    now = datetime.datetime.now()
    print(f"doing {date_path} at {str(now)}", flush=True)

    try:
        analyzer_path = date_path / 'shank_2/analyzer'
        analyzer = si.load_sorting_analyzer(analyzer_path)

        analyzer_merge_unit_groups = []
        analyzer_new_unit_ids = []
        for new_unit_id, global_merge_unit_group in zip(global_new_unit_ids, global_merge_unit_groups, strict=True):
            include_merge = True

            one_merge_unit_group = []
            for unit_id in global_merge_unit_group:
                if unit_id in analyzer.unit_ids:
                    one_merge_unit_group.append(unit_id)

            if len(one_merge_unit_group) < 2:
                include_merge = False
                
            if include_merge:
                analyzer_merge_unit_groups.append(one_merge_unit_group)
                analyzer_new_unit_ids.append(new_unit_id)

        analyzer_merged = analyzer.merge_units(
            merge_unit_groups=analyzer_merge_unit_groups, 
            raise_error_if_overlap_fails = False, 
            new_unit_ids=analyzer_new_unit_ids, 
            sparsity_overlap=0.5, 
            censor_ms=1
        )

        merged_analyzer_path = analyzer_path.with_name("analyzer_merged")

        analyzer_merged.save_as(format='binary_folder', folder=merged_analyzer_path)

    except Exception as e:
        print(f"error, {e}")


