Toy repo for prototyping and play with new spike sorting methods for Aeon.

To use on the SWC cluster, first get an a small interactive job

```
srun -p cpu -n 1 --mem=8G --pty bash -i
```

Then download (git clone) the repo, change directory into it:

```
git clone https://github.com/chrishalcrow/aeon_ss_playground.git
cd aeon_ss_playground
```

We can then check that the environment build looks good by using `uv`. If you're on the SWC HPC you need to load `uv` into your session to run it:

```
module load uv
uv sync
```

You can run run scripts from within the repo directory:

```
uv run scripts/chronic/make_template_library.py
```
