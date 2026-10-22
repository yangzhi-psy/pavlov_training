# Cognitive-data open release

Reproducible, pseudonymized cognitive outcomes for adaptive-difficulty training
(ADT) versus low-difficulty training (LDT; Experiment 1), and ADT versus
recreational gaming (Experiment 2). Python 3.12 (tested with 3.12.13); install
the pinned packages with `python -m pip install -r requirements.txt` (it refers
to the release root `requirements.txt`), then run `python run_all.py` from
this directory (or call it by absolute path), or `python run_all.py` in the
release root to run all three parts. All analysis scripts read only this
folder's `data/` files; no private roster or original repository is needed.

## Folder map

- `data/`: public long-form scores (corrected and no-outlier-removal), public
  participant attributes, data dictionary.
- `code/shared.py`: common ML/Powell random-intercept MixedLM group×time LR
  tests, chi-square(1), BH-FDR, BIC/JZS integrations, export helpers.
- `code/exp1.py`, `exp2.py`, `matching.py`, `age_time.py`, `bayes.py`,
  `sensitivity.py`, `demographics.py`, `figure1.py`, `section31_checks.py`,
  `methods_numbers.py`: one module per analysis.
- `outputs/<name>/`: source-data CSV, standalone `build.py` (delegates to
  public script), produced table in CSV+Markdown or PNG+PDF figure. Figure 1
  also includes self-contained plotting code in `plot.py` (imports shared model
  loaders from `code/`).
- `run_all.py`: regenerate every output. `requirements.txt`: pinned runtime.
