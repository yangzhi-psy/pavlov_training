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

## Participants and corrections

Experiment 1 randomized 107 (ADT 54, LDT 53); ADT 51 completed/analyzed,
LDT 48 completed but only 47 have cognitive records (one roster-only
completer). Experiment 2 screened 57, excluded seven, control analyzed 50;
Experiment 2 reuses the 51 ADT participants. P001–P148 are assigned by sorting
the **original ID** strings alphabetically; P149 follows for the roster-only
completer. This rule is documented without releasing the crosswalk. All public
files use P-codes exclusively. The two duplicate pretests (P036 and P039)
were corrected by masking 31 outcomes in each pretest row;
no uncorrected duplicates are published. Exact age at test is provided
because rounding age to two decimals changes nearest-neighbor tie-breaking and
model precision. DOB, birth spacing and names are omitted.

Primary models use all nonmissing outcome observations (not just paired
completers). Age×time fits center exact age at the entire experiment's
participant mean before filtering per outcome. Matching uses exact sex and
education stage, ages at each person's test date, a 0.25-year caliper, greedy
ADT-first ascending pseudonym order (equivalent to ascending original IDs),
nearest available control and ascending pseudonym tie-breaks. The sensitivity
match uses a 0.10-year age caliper. The Table S5 sensitivity row that matches
on birth-date distance (0.25-year caliper, 32 pairs) needs birth-date
information that is not released; this row is available from the authors on
request.

## Number map

Numbers below are values rounded for reporting; raw precision is in the CSV.
Do not substitute nominal p-values for the within-five BH-FDR corrections.

| Reported statistic | Output CSV | Columns / row selector |
| --- | --- | --- |
| Exp 1 N-back χ² 5.71; p .017; pFDR .084 | `outputs/Table_3/Table_3.csv` | `outcome=N-back 2-vs-0 RT`: `chi2`, `p`, `pFDR` |
| Exp 2 MRT 6.84/.009/.045 | `outputs/Table_4/Table_4.csv` | `MRT rotation RT`, `without_age`: `chi2`, `p`, `pFDR` |
| Exp 2 MRT age-only 6.86/.009/.044 | `outputs/Table_4/Table_4.csv` | `MRT rotation RT`, `age`: `chi2`, `p`, `pFDR` |
| Exp 2 MRT age+age×time 5.14/.023/.117 | `outputs/Table_4/Table_4.csv` | `MRT rotation RT`, `age_time`: `chi2`, `p`, `pFDR` |
| Exp 1 N-back BF BIC 1.26; BF JZS 2.10 | `outputs/Text_Bayes_factors/Text_Bayes_factors.csv` | `BF_BIC`, `BF_JZS` |
| No-outlier aligned processed N-back p .097 | `outputs/Text_no_outlier_sensitivity/Text_no_outlier_sensitivity.csv` | `N-back 2-vs-0 RT`: `p` |
| Matched 19 pairs MRT χ² 4.00/p .046/pFDR .228 | `outputs/Table_S5/Table_S5.csv` | `matching_rule=primary_025`, `MRT rotation RT`: `pairs`, `chi2`, `p`, `pFDR` |
| Matched 13 pairs MRT χ² 6.95/p .008/pFDR .042 | `outputs/Table_S5/Table_S5.csv` | `matching_rule=age_010`, `MRT rotation RT`: same columns |
| Matched 32 pairs (birth-date distance) MRT χ² 1.05/p .307/pFDR .383 | not in this release | available from the authors on request |
| S6 MRT Exp 2 age×time χ² ~.005/p .946 and VIFs | `outputs/Table_S6/Table_S6.csv` | `groups=AC`, `MRT rotation RT`: `age_time_chi2`, `age_time_lr_p`, `vif_group_time`, `vif_age_time` |
| S6 N-back Exp 1 age×time χ² .659/p .417 | `outputs/Table_S6/Table_S6.csv` | `groups=AB`, `N-back 2-vs-0 RT`: `age_time_chi2`, `age_time_lr_p` |
| Exp 1 N-back improvement difference 0.0565, 95% CI [0.0108,0.1023] | `outputs/Table_3_CI/Table_3_CI.csv` | `N-back 2-vs-0 RT`: `adt_minus_ldt_improvement`, `ci_lower`, `ci_upper` |
| Table 3 "Difference in change, LDT − ADT (95% CI)", all five outcomes | `outputs/Table_3_CI/Table_3_CI.csv` | `beta`, `ci_lower`, `ci_upper` (group × time coefficient = LDT change − ADT change, raw units; `adt_minus_ldt_improvement` flips the sign for the accuracy and d′ rows and is not the printed column) |
| Sec 3.1 Exp 1 age-adjusted: N-back Δχ² < 0.1, others < 0.07 | `outputs/Text_exp1_age_adjusted/Text_exp1_age_adjusted.csv` | `delta_chi2` (also `chi2_without_age`, `chi2_with_age`, `p_*`, `pFDR_*`) |
| Sec 3.1 accuracy N-back χ²(1) 2.92, p .087; dz .97/.63 | `outputs/Text_accuracy_nback/Text_accuracy_nback.csv` | `chi2`, `p`, `dz_adt`, `dz_ldt` |
| Sec 3.1 ANT alerting 0.27/p .60; orienting 0.17/p .68 | `outputs/Text_ANT_networks/Text_ANT_networks.csv` | `chi2`, `p` |
| Sec 2.8.5 outliers removed ADT/LDT/control: N-back 2/1/2 (5), MRT 2/4/5 (11), ANT 4/9/7 (20), Raven 4/9/1 (14), Go/No-Go 0/2/1 (3) | `outputs/Text_outlier_counts/Text_outlier_counts.csv` | `removed_adt`, `removed_ldt`, `removed_control`, `removed_total` |
| Sec 2.1 / 4 post hoc power: d ≥ 0.57 (80%), 0.66 (90%); 165–202 per group for d = .31/.28 | `outputs/Text_power/Text_power.csv` | `d`, `n_per_group_rounded_up` |
| Sec 3.2 Exp 2 age–group r .53; VIF 4.0 | `outputs/Table_S6/Table_S6.csv` | `groups=AC`: `point_biserial_r`, `vif_group_time` |


All other outcomes for Tables 3, 4, S3, S5 and S6 are in their respective CSVs.
Output folders are named after the table numbers of the revised manuscript:

| Output folder | Manuscript item |
| --- | --- |
| `Figure_1` | Figure 1 (participant flow) |
| `Table_2` | Table 2 (Experiment 1 demographics, analysed sample: ADT 51, LDT 47) |
| `Table_3` | Table 3 (Experiment 1, signed effect sizes and group × time tests) |
| `Table_3_CI` | Table 3, difference-in-change column (95% CI) |
| `Table_4` | Table 4 (Experiment 2, three model specifications) |
| `Table_S3` | Table S3 (descriptives and signed within-group effect sizes) |
| `Table_S5`, `Table_S5_demographics` | Table S5 (corrected-age matched analyses and the matched-sample demographics in its note) |
| `Table_S6` | Table S6 (age × time terms) |
| `Text_Bayes_factors` | Bayes factors reported in Section 3.3 |
| `Text_no_outlier_sensitivity` | Non-outlier-screened p values reported in Section 2.8.5 |
| `Text_exp1_age_adjusted`, `Text_accuracy_nback`, `Text_ANT_networks` | Section 3.1 robustness checks (`code/section31_checks.py`) |
| `Text_outlier_counts`, `Text_power` | Section 2.8.5 outlier counts and the post hoc power values of Sections 2.1 and 4 (`code/methods_numbers.py`) |

Table 2 presents recalculated demographics for the analysed sample (ADT 51, LDT 47; the
roster-only completer P149 has no cognitive data and is excluded). The Figure 1 allocation and
screening counts come from the study records; analyzed counts come from the
public data. Figure 1 shows the 51/47/50 analyzed cohorts.

Verification: all text outputs are written with LF line endings on every
platform. With the pinned environment, a clean run reproduces the outputs; the
release root `SHA256SUMS.txt` lists every file. CSV values can differ in the
last digits (≤ 1e-8) with other package versions. `Figure_1.png` is a
rendering of `source_data.csv`: its pixels depend on the matplotlib version
(the manuscript image was rendered in an earlier environment and differs from
the pinned-environment rendering in about 1% of pixels; the plotted counts are
identical). PDFs carry a fixed creation date.

## Scope

Covered: Figure 1, Tables 2–4, Tables S3, S5 and S6, the in-text Bayes
factors, the non-outlier-screened sensitivity values and the Section 3.1
robustness checks. Figure 2 and Table S7 (training exposure, compliance) are in
`../02_gamelog`; Figure 3 and Tables S4 and S8 (in-game test tasks) are in
`../03_validity`. Tables 1, S1 and S2 describe the game tasks and the training
rotation and contain no data.

## Change log

- Final revision: Table 2 restricted to the analysed sample (ADT 51, LDT 47).
  Changed: `code/demographics.py` (selection line) and `outputs/Table_2/`; every other output is unchanged.
- Public release: added `code/section31_checks.py` and
  `code/methods_numbers.py` and their five output folders; all CSV/Markdown/build files are written with LF line endings
  (`shared.py`, `figure1.py`, `matching.py`); the package `SHA256SUMS.txt` is
  replaced by the release root `SHA256SUMS.txt`; requirements moved to the
  release root (matplotlib 3.11.1, openpyxl removed as unused). No data file
  and no numeric result changed.
- Public release, disclosure review: `birth_distance_years` removed from
  `data/participants.csv`, and the birth-date-distance matching rule removed
  from `code/matching.py`. Table S5 outputs keep the two age-matching rules
  (19 and 13 pairs), whose values are unchanged; the birth-date row (32 pairs)
  is available from the authors on request.
