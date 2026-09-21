from broo_helper import make_and_run_python_script

make_and_run_python_script("do_merges", "scripts/do_merges.py", hours=6, cores=8, mem=64, gpu=False, gpu_queue=False)
