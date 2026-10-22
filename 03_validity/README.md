# Figure 3, Table S4 and Table S8: in-game test-task RT and standardized cognitive measures

These are the code and data for Figure 3, Table S4 and Table S8 of the revised manuscript. Participants are identified by P-codes only (the same codes as `01_cognitive`); this folder contains no original IDs, names or dates.

## How to run
From this folder:
```
python run_figure3_tableS4_tableS8.py
```
or run `python run_all.py` in the release root. It reads `inputs/test_task_trials_pcode.csv` and `../01_cognitive/data/cognitive_long.csv` and writes `outputs/` (about 5 s). The figure uses the Arial font. Package versions: see the release `README.md` and `requirements.txt`; with matplotlib 3.11.1 the PNG is byte-identical to the manuscript figure, other matplotlib versions or fonts change the rendering only. The CSV values do not depend on the environment.

## Inputs
| File | Content |
|---|---|
| `inputs/test_task_trials_pcode.csv` | One row per trial of every session of the five in-game test tasks (ColorJudgment_1, Singler_1, MatchCard_1, Pack_1, Toilet_1) for the 97 included participants (ADT 51, LDT 46): 316,320 rows. Columns: participant_id, group, game_key, session_index, hardmod (difficulty level), passive (Y/N), trial_index, rt_s (per-trial response time, `SubGameDuration`, s). |
| `../01_cognitive/data/cognitive_long.csv` | The public cognitive data; posttest = `time == 1`. |

**Passive sessions** follow the manuscript definition: zero correct responses, or fewer than 0.5 × the mean correct count of all sessions of the same game at the same difficulty level (benchmark: `02_gamelog/data/passive_benchmark.csv`).

**Provenance.** The P-coded trial file was derived from the final game logs by an internal script that requires the private ID map; it is not distributed. The row order of the trial file is kept, because it fixes the floating-point summation order of the RT means.

## Definitions
- **RT:** for a participant, task and level, the mean of all per-trial response times over the participant's **non-passive** sessions of that task at that level.
- **Shared levels:** ColorJudgement 13, Singler 8, MatchCard 12, Pack 8, Toilet 18.
- **Standard measures (posttest):** Go/No-Go d′ (`GoNogo_d`), N-back 2-vs-0 RT (`Nback_2VS0_RT`), MRT rotation RT (`MRT_rotate_RT`), ANT executive control (`ANT_execution`), Raven ≥2-element accuracy (`Raven_2more_ACC`).
- **Figure 3 and Table S4:**
  - Inclusion, rule (i): participants with at least one non-passive session at the shared level of **all five** tasks. n = 94; the list is in `outputs/included_participants_rule_i_Pcodes.csv`.
  - 25 Spearman correlations (5 tasks × 5 measures). The 95% CI uses the Fisher z method, and pFDR is Benjamini–Hochberg across all 25. The per-pair n is 86–93 (some standardized scores are missing).
  - Asterisks in Figure 3 mark **uncorrected** p (* < .05, ** < .01, *** < .001).
  - Figure 3 and Table S4 both read the single computation file `outputs/figure3_tableS4_results.csv`.
  - A consistency check (asterisked cells = rows with p < .05) is asserted.
  - `outputs/Figure3_caption.txt` is the manuscript caption, with n and the smallest pFDR filled in from the results.
- **Table S8:** domain-matched pairs at the listed levels:
  - ColorJudgement 8/11/13;
  - Singler 4/6/8;
  - MatchCard 4/6/8/10/12;
  - Pack 4/6/8;
  - Toilet 8–18 in steps of 2.

  Each row includes every included participant with RT at that level and a posttest score (n 87–96). The table is descriptive and uncorrected.
- **Why Table S8 differs from Table S4 at the shared level:** only the inclusion rule differs. Table S8 uses everyone with data at that level, while Table S4 uses rule (i), which removes 1–3 participants per pair. Restricted to rule (i), the Table S8 shared-level rows equal the Table S4 domain-matched rows exactly (for example MatchCard L12: ρ .279, n 95 in Table S8 vs .308, n 92 under rule (i)).

## Key values
- n = 94.
- Domain-matched pairs: ColorJudgement–Go/No-Go d′ −.105 (n 93); Singler–Raven −.146 (n 87); MatchCard–N-back RT .308 [.111, .483] (n 92, p = .003, pFDR = .070); Pack–MRT RT .189 (n 92); Toilet–ANT executive control −.020 (n 86).
- Smallest pFDR = .070; no correlation survives FDR correction.

Checksums of all files are in the release root `SHA256SUMS.txt`.
