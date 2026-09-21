from broo_helper import make_and_run_python_script

make_and_run_python_script("merges", "scripts/get_all_merges.py", hours=6, cores=4, mem=16, gpu=False, gpu_queue=False)
