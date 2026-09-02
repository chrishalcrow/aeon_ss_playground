Toy repo for prototyping and play with new spike sorting methods for Aeon.

To use on the SWC cluster, first get an a small interactive job

```
srun -p cpu -n 1 --mem=8G --pty bash -i
```

Then download (git clone) the repo, change directory into it and make sure the environment can build

```
git clone https://github.com/chrishalcrow/aeon_ss_playground.git
cd aeon_ss_playground
uv sync
```

You can run run scripts from within the repo directory:

```
uv run scripts/chronic/make_template_library.py
```
