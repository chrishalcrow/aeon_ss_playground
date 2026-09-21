#!/bin/bash 

#SBATCH -J sliced
#SBATCH -p cpu
#SBATCH -N 1
#SBATCH --mem 128G
#SBATCH --mail-user c.halcrow@ucl.ac.uk
#SBATCH --mail-type END,FAIL
#SBATCH -n 8
#SBATCH -t 0-03:00
#SBATCH -o logs/sliced_%j.out
#SBATCH -e logs/sliced_%j.err 

module load uv

ulimit -n 4096

cd /ceph/scratch/chalcrow/fromgit/aeon_ss_playground/scripts
uv run scripts/sliced_motion.py --experiment abcEphys01 --probe-name ProbeB --shank-id 2 --output-folder sliced_output --start-time "2026-06-25 09:05:47" --end-time "2026-07-11 11:53:54" --cores 8 