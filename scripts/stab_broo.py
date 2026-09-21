from broo_helper import make_and_run_python_script

make_and_run_python_script("stability", "scripts/get_stability_info.py", hours=4, cores=4, mem=32, gpu=False, gpu_queue=False)
