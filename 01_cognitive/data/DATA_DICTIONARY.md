# Cognitive data dictionary

## `cognitive_long.csv` and `cognitive_long_no_outlier_removal.csv`

Each record is one participant at pretest (`time=0`) or posttest (`time=1`).
`participant_id` is a pseudonym; `experiment_membership` and `group` identify
Experiment 1 ADT (A), LDT (B), and Experiment 2 recreational control (C).
The same ADT cohort is in both experiments. All remaining columns are the
original cognitive outcome names, not scores derived by the release scripts.
`ACC` means accuracy/proportion correct; `RT` is response time (seconds for
the five focal RT contrasts, although Go/No-Go raw RT is in milliseconds);
`d` is Go/No-Go sensitivity d-prime. `Nback_2VS0_RT` is the 2-versus-0
working-memory RT contrast, `MRT_rotate_RT` rotation RT,
`Raven_2more_ACC` ≥2-element Raven accuracy, and `ANT_execution` executive
attention RT contrast. All 36 original outcome fields, including secondary
task variants, are retained. Missing outcome values are empty cells.

The main file applies outcome-level 1.5×IQR outlier removal and masks the
identical, erroneously duplicated 31 pretest outcome values for two participants
(62 cells total). The no-outlier-removal file uses the **aligned processed dump**
(not the raw, misaligned dump); it has the same two masked pretests, retains
pre-outlier values, and excludes one additional noncohort row. `GoNogo_d`
contains a nonfinite value in the unscreened data, so that sensitivity fit is
undefined. Per-outcome complete-pair counts differ from available-case MixedLM
observation counts.
The `Table_S3` paired t-test p-values are descriptive paired tests, **not**
the original manuscript's model-based `emmeans` significance marks.

## `participants.csv`

One row per participant: 148 with cognitive results and P149, an LDT training
completer with no cognitive record. `group` A/B/C; `sex` demographic category 1/2;
`education_stage` original stage code (1/2/3); `year_of_study` original
grade label (g1/g2/g3/g6). Empty demographics for the roster-only participant
are genuinely unavailable. `age_years` is age at testing floored to whole
years; `age_at_test_2dp` is the displayed age rounded to 0.01 year;
`age_at_test` is the **unrounded age at test** needed to reproduce age-adjusted
models and deterministic caliper matching. `age_centered_AB_3dp` and
`age_centered_AC_3dp` are display-only, rounded to 0.001 year after subtracting
the corresponding experiment's mean over 98 or 101 cognitive-data participants
before outcome-specific missingness. Model code recomputes centered age from
the unrounded age, to preserve published precision.

No birth-date information is released: no DOB and no relative birth spacing.
The birth-date-distance sensitivity match of Table S5 (32 pairs) therefore
cannot be rerun from this release; that row is available from the authors on
request. No original IDs, names, or DOBs are present in the release.

Public P-codes for the 148 analyzed subjects were assigned in alphabetical
original-ID order; roster-only subjects follow after those 148 in their own
alphabetical order. The private crosswalk is **not** part of this release.
