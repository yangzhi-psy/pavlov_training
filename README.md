# Adaptive-difficulty cognitive training: data and code for the revised manuscript

This folder regenerates every result, table and figure of the revised manuscript from the files in this folder alone: Figures 1–3, Tables 2–4 and S3–S8, Sections 2.7 and 3.1, the Bayes factors and the sensitivity analyses. The one exception is the Table S5 sensitivity row that matches on birth-date distance: it needs birth-date information that is not released, and it is available from the authors on request. Participants are identified by pseudonymous P-codes (P001–P149). 

## How to run
1. Install Python 3.12 (tested with 3.12.13, 64-bit, Windows 11).
2. Create an environment and install the pinned packages:
   ```
   python -m venv .venv
   .venv\Scripts\python -m pip install -r requirements.txt      (Windows)
   .venv/bin/python -m pip install -r requirements.txt          (macOS/Linux)
   ```
3. From this folder: `python run_all.py` (about 70 s). It runs, with paths relative to this folder:
   - `01_cognitive/run_all.py`;
   - `02_gamelog/code/table_s7_section27.py` and `02_gamelog/code/figure2.py`;
   - `03_validity/run_figure3_tableS4_tableS8.py`.

   Each step overwrites its `outputs/` folder. The parts can also be run separately from their folders.
4. Check the result: `sha256sum -c SHA256SUMS.txt` (or any SHA-256 tool). All text files are written with LF line endings on every platform.

**Pinned environment** (`requirements.txt`): numpy 2.3.5, pandas 2.3.3, scipy 1.16.2, statsmodels 0.14.5, matplotlib 3.11.1, tabulate 0.10.0, and their dependencies.

## Folder map
| Folder | Content |
|---|---|
| `01_cognitive/` | Cognitive outcome data (pre/post, three groups), participant attributes and analysis code. It has its own `README.md` (number map) and `data/DATA_DICTIONARY.md`. |
| `02_gamelog/` | Game-log data of Experiment 1: `data/` (sessions, participants, passive-session benchmark), `code/`, `outputs/` and `DATA_DICTIONARY.md` |
| `03_validity/` | In-game test-task trial data and the convergent-validity analysis (Figure 3, Tables S4 and S8). It has its own `README.md`. |
| `LICENSE`, `LICENSE-DATA` | MIT (code), CC BY 4.0 (data, documentation, figures) |
| `MANIFEST.md` | One line per file |
| `SHA256SUMS.txt` | SHA-256 of every file (except itself) |

## Samples
- **Experiment 1 (ADT vs LDT):** ADT 51 and LDT 47 have cognitive data.
- **Game-log sample:** ADT 51 and LDT 46. One LDT participant's game-log archive contained no sessions.
- **P149:** an LDT training completer with game logs but no cognitive data, so not part of any manuscript analysis. They appear in `01_cognitive/data/participants.csv` (Figure 1 count of 48 LDT completers) but not in `02_gamelog/data/participants.csv` or `02_gamelog/data/sessions.csv`. Their sessions entered only the passive-session benchmark, which is released as an aggregate (`02_gamelog/data/passive_benchmark.csv`).
- **Experiment 2:** reuses the 51 ADT participants, plus a recreational-gaming control group of 50.

## Manuscript item map
| Manuscript item | Script | Output (relative to the part folder) |
|---|---|---|
| Figure 1 (participant flow) | `01_cognitive/code/figure1.py` | `outputs/Figure_1/Figure_1.png`, `.pdf`, `source_data.csv` (allocation and screening counts come from the study records and are written into the script; analysed counts are checked against the data) |
| Table 2 (Exp 1 demographics, ADT 51 / LDT 47) | `01_cognitive/code/demographics.py` | `outputs/Table_2/Table_2.csv` |
| Table 3 (Exp 1: pre→post, signed dz, n, χ², p, pFDR) | `01_cognitive/code/exp1.py` | `outputs/Table_3/Table_3.csv` |
| Table 3, "Difference in change, LDT − ADT (95% CI)" | `01_cognitive/code/exp1.py` | `outputs/Table_3_CI/Table_3_CI.csv`: `beta`, `ci_lower`, `ci_upper` |
| Table 4 (Exp 2, three models) | `01_cognitive/code/exp2.py` | `outputs/Table_4/Table_4.csv` |
| Table S3 (descriptives, paired change) | `01_cognitive/code/exp1.py` | `outputs/Table_S3/Table_S3.csv` |
| Table S4 (25 RT × standard-measure correlations) | `03_validity/run_figure3_tableS4_tableS8.py` | `outputs/TableS4.csv`, `outputs/figure3_tableS4_results.csv` |
| Table S5 (matched analyses) and its note (matched demographics: mean ages 20.02 / 20.07, sex, years of study) | `01_cognitive/code/matching.py` | `outputs/Table_S5/Table_S5.csv`, `outputs/Table_S5_demographics/Table_S5_demographics.csv`, `outputs/Table_S5/matched_pairs.csv` (years of study). Released rows: primary match (0.25-year age caliper, 19 pairs) and the 0.10-year age caliper (13 pairs). The birth-date-distance row (32 pairs) is **available from the authors on request**. |
| Table S6 (age × time) | `01_cognitive/code/age_time.py` | `outputs/Table_S6/Table_S6.csv` |
| Table S7 (training exposure) | `02_gamelog/code/table_s7_section27.py` | `outputs/Table_S7.csv`, `outputs/group_results.csv` |
| Table S8 (domain-matched pairs by level) | `03_validity/run_figure3_tableS4_tableS8.py` | `outputs/TableS8.csv` |
| Figure 2 (difficulty progression, 51 ADT) | `02_gamelog/code/figure2.py` | `outputs/Figure2.png`, `.pdf`, `figure2_source.csv`, `Figure2_plotted_values.csv` |
| Figure 3 (test-task RT vs standard measures) and caption | `03_validity/run_figure3_tableS4_tableS8.py` | `outputs/Figure3.png`, `outputs/Figure3_caption.txt` |
| Tables 1, S1, S2 (task descriptions, schedule) and Figure S1 (schematic) | — | no data |

## Notes
- **Table 3 sign convention:** "Difference in change, LDT − ADT" is the group × time coefficient (LDT change − ADT change, raw units). For RT outcomes, a positive value means ADT improved more; for Raven accuracy and Go/No-Go d′, a positive value means LDT improved more.
- **Passive sessions:** zero correct responses, or fewer than 0.5 × the mean correct count of all sessions of the same game at the same level. Passive sessions are excluded from active training time and from the test-task RTs.
- **Disclosure:** `01_cognitive/data/participants.csv` contains exact age at test (needed for the age-adjusted models and the age matching), sex, education stage and year of study. No birth dates or birth spacing are released.
- **Session timing:** `02_gamelog/data/sessions.csv` gives no calendar dates and no time of day. Days are indexed (`day_index`, `training_day_number`). Within a day, each session's start is given as `start_offset_min`: minutes since that participant's first session start of the day. The sitting and 90-min rules of Section 2.7 depend only on these within-day differences, so all outputs are identical to those computed from the logged clock times.
- **Provenance:** the public files were derived from the internal, identifiable study data by internal scripts that need the private ID map. Those scripts are not distributed. The derivation was checked value by value against the internal data.

## Licence
- **Code** (`*.py` and `02_gamelog/code/style/*.json`): MIT License, see `LICENSE`.
- **Data, documentation and figures** (`*.csv`, `*.md`, `*.txt`, `*.png`, `*.pdf`): Creative Commons Attribution 4.0 International (CC BY 4.0), see `LICENSE-DATA`.

## Citation
Please cite the article and this dataset:
- Dataset: [authors] (2026). *Adaptive-difficulty cognitive training: data and code for the revised manuscript.* Open Science Framework. **[OSF DOI]**: placeholder, to be replaced with the DOI minted after upload.

## Data availability
The de-identified data and analysis code that reproduce all results, tables and figures are openly available on the Open Science Framework at [OSF DOI] (data under CC BY 4.0, code under MIT). The Table S5 sensitivity analysis that matches participants on birth-date distance requires birth-date information that is not shared publicly; this result is available from the authors on request. Raw game-log archives and participant identifiers are not shared to protect participant privacy; they are available from the corresponding author on reasonable request, subject to ethics approval.
