from pathlib import Path

base_dir = Path("/ceph/scratch/chalcrow/fromgit/aeon_ss_playground/abcEphys01/lupin_si_output/")
target_subpath = Path("shank_0/analyzer/extensions/quality_metrics")

# Collect directories that contain the target path
matching_folders = [
    folder for folder in base_dir.iterdir()
    if folder.is_dir() and (folder / target_subpath).exists()
]

make_commands = True
#print(matching_folders)


for matching_folder_path in matching_folders:

    #print(matching_folder_path)

    if make_commands:

        print(f"mv {Path(*matching_folder_path.parts[-3:])} mock_dj_store/ephys-processed/abcEphys01-aeon3/AAA-1140901/insertion_2/ephys_blocks/")
        print(f"mv mock_dj_store/ephys-processed/abcEphys01-aeon3/AAA-1140901/insertion_2/ephys_blocks/{Path(*matching_folder_path.parts[-1:])}/shank_0 mock_dj_store/ephys-processed/abcEphys01-aeon3/AAA-1140901/insertion_2/ephys_blocks/{Path(*matching_folder_path.parts[-1:])}/shank0")
        print(f"mkdir mock_dj_store/ephys-processed/abcEphys01-aeon3/AAA-1140901/insertion_2/ephys_blocks/{Path(*matching_folder_path.parts[-1:])}/shank0/lupin_000/")
        print(f"mv mock_dj_store/ephys-processed/abcEphys01-aeon3/AAA-1140901/insertion_2/ephys_blocks/{Path(*matching_folder_path.parts[-1:])}/shank0/analyzer mock_dj_store/ephys-processed/abcEphys01-aeon3/AAA-1140901/insertion_2/ephys_blocks/{Path(*matching_folder_path.parts[-1:])}/shank0/lupin_000/sorting_analyzer")

print(f"Found {len(matching_folders)} matching folders.")
