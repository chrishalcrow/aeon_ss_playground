from pathlib import Path

import numpy as np
import pandas as pd
import spikeinterface.full as si

def get_match_from_sortings(sorting1, sorting2, final_frame=30_000*60*60*30):

    print("doing get match from sortings")

    six_hours = 30_000*60*60*6

    start_of_comparison = 0
    end_of_comparison = six_hours

    sort1_sliced = sorting1.frame_slice(start_frame = final_frame - six_hours + start_of_comparison , end_frame=final_frame - six_hours + end_of_comparison)
    sort2_sliced = sorting2.frame_slice(start_frame = start_of_comparison, end_frame=end_of_comparison)

    comparison = si.compare_two_sorters(sort1_sliced, sort2_sliced)

    return comparison.get_matching()[0].values


def build_match_s3_column(matches_s1s2, matches_s2s3, sorting_2, sorting_3):

    match_s3_column = []

    for unit_in_s2 in matches_s1s2:
        if unit_in_s2 != -1:
            match_in_s3 = matches_s2s3[sorting_2.ids_to_indices([unit_in_s2])[0]]
        else:
            match_in_s3 = -1

        match_s3_column.append(match_in_s3)

    s3_unit_ids = sorting_3.unit_ids

    unmatched_units = set(s3_unit_ids).difference(set(list(matches_s2s3)))
    match_s3_column += list(unmatched_units)

    return match_s3_column


dj_store_path = Path('mock_dj_store')
ephys_blocks_path = dj_store_path / 'ephys-processed/abcEphys01-aeon3/AAA-1140901/insertion_2/ephys_blocks/'

block_paths = list(ephys_blocks_path.glob('2026*'))

sorted_paths = sorted(block_paths, key=lambda p: p.parts[-1])

print(sorted_paths)

sorter_output_paths = [block_path / 'shank0/lupin_000/sorting_analyzer' for block_path in sorted_paths]
sortings = [si.load_sorting_analyzer(sorter_output_path, load_extensions=False, lazy=True).sorting for sorter_output_path in sorter_output_paths]

matches={}
s0_unit_ids = sortings[0].unit_ids
s0_column = s0_unit_ids

print("about to match")

columns = [s0_column]
for sorting_index, _ in enumerate(sortings[:-1]):

    matches = get_match_from_sortings(sortings[sorting_index], sortings[sorting_index+1])
    columns.append(build_match_s3_column(columns[-1], matches, sortings[sorting_index], sortings[sorting_index+1]))

global_data = -1*np.ones((len(columns), len(columns[-1])))

for col_index, column in enumerate(columns):
    global_data[col_index,:len(column)] = column

all_matches = pd.DataFrame(data=global_data.T, columns=[f's{col_index}' for col_index, _ in enumerate(columns)]).astype('int')

print("about to save")


all_matches.to_csv('global_ids.csv')

