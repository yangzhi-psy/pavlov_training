# Game-log data: data dictionary

Public, de-identified game-log data of Experiment 1 (ADT n = 51, LDT n = 46). Participants are identified by the P-codes of `01_cognitive`. The files contain no names, original IDs, calendar dates or times of day: time is expressed as a logged-day index and, within a day, as minutes since the participant's first session of that day.

**Source and processing (internal, not distributed).** The data were derived from the participants' raw game-log archives after the cleaning described in the manuscript (Section 2.7):
- removal of 4,437 sessions that were stored in a second participant's archive (shared devices);
- the passive-session flag;
- the start of training. Training day 1 is the first logged day after the installation (familiarisation) day. For ADT it was taken from the training schedule; for LDT it was identified from the game content of the first logged days, with two manual corrections.

**Exclusions.**
- One LDT completer (P149) has an archive but no cognitive-outcome data (not in the analysis roster). Their 2,049 sessions are not included. The manuscript reports no value that depends on them, except through the passive-session benchmark. That benchmark is the level mean over all cleaned sessions, and it is provided as an aggregate in `passive_benchmark.csv`.
- One LDT completer has an empty archive. They are listed in `participants.csv` with no sessions.

## data/sessions.csv
123,154 rows, one per session of the 97 participants in the game-log sample, ordered by participant and session order.

| Column | Type | Meaning | Units |
|---|---|---|---|
| participant | text | P-code | |
| group | text | ADT (adaptive difficulty) or LDT (low difficulty) | |
| session_order | integer | Order of the session within the participant, by logged end time (ties keep the log order) | 1..n |
| day_index | integer | Logged-day index: 1 = the participant's first logged day, 2 = next day with any logged session, and so on; days without logs are skipped. Day 1 is the installation/familiarisation day for 88 of the 97 participants (up to two familiarisation days); for the other 9 the first logged day is training day 1. | day |
| training_day | Y/N | The day is a training day (on or after training day 1). N = familiarisation (pre-training) day | |
| training_day_number | integer | Index among training days (1 = training day 1); empty on familiarisation days. Days after training day 19 (allowed before post-testing) are kept | day |
| start_offset_min | decimal (4 places) | Session start, in minutes since the start of the participant's first session of that logged day (0 for the first session). Start = logged end time − duration; a logged day is the calendar date of the session end time. The values are whole seconds / 60: multiply by 60 and round to recover whole seconds exactly | min |
| duration_s | integer | Logged session duration. Session end = start + duration | s |
| game_key | text | Game file name: `<game>_0` = training game (13 games), `<game>_1` = in-game test task (5 tasks) | |
| game | text | Game name (`ColorJudgment` is shown as "ColorJudgement" in Figure 2) | |
| game_type | text | training / test | |
| level | integer | Difficulty level of the session (raw `HardMod`) | level |
| correct_count | integer | Number of correct responses in the session | items |
| n_items | integer | Number of scored items in the session | items |
| passive | Y/N | Passive session: zero correct responses, or correct_count < 0.5 × mean correct count of all sessions of the same game_key at the same level (`passive_benchmark.csv`) | |

## data/participants.csv
98 rows: the Experiment 1 training completers with cognitive data (ADT 51, LDT 47), i.e. all completers except P149.

| Column | Type | Meaning |
|---|---|---|
| participant | text | P-code |
| group | text | ADT / LDT |
| included_in_log_sample | Y/N | In the game-log sample (ADT 51, LDT 46) |
| figure2_line_order | integer | Drawing order (1–51) of the ADT lines in Figure 2, as in the original figure (colour = order modulo 7); empty for LDT |
| note | text | Reason for exclusion, if any |

## data/passive_benchmark.csv
604 rows, one per game_key × level. These are aggregates over all 125,203 cleaned sessions of the 98 archives, including the excluded LDT completer's archive.

| Column | Type | Meaning | Units |
|---|---|---|---|
| game_key | text | As in sessions.csv | |
| hardmod | integer | Level (= `level` in sessions.csv) | level |
| n_sessions | integer | Cleaned sessions at that game and level | count |
| mean_correct | float | Mean correct_count | items |
| threshold_0_5_mean | float | 0.5 × mean_correct; a session with correct_count below it (or zero) is passive | items |

## outputs/ (written by code/)
| File | Content |
|---|---|
| `daily_metrics.csv` | One row per participant × logged day: total / qualifying / passive sessions, active_training_time_min (summed duration of qualifying sessions, min), n_sittings, session_span_min (sum of sitting spans, min), met_90min (Y/N), training_day, training_day_number |
| `participant_metrics.csv` | One row per participant: total_active_time_s / _h, total / qualifying / passive sessions (all logged days), sessions_training_days, qualifying_training_days, days_logged, logged_days_played_incl_familiarisation, pretraining_days, training_days_counted, training_days_played (≥ 1 qualifying session), days_met_90min, compliance_90min_pct_days (% of training days), passive_rate_pct, peak_training_difficulty, peak_test_difficulty_pooled |
| `group_results.csv` | 13 measures: ADT and LDT n, median, Q1, Q3 (numpy, linear interpolation), Mann–Whitney U for ADT (two-sided, scipy default), p, pooled values (compliance: met days / training days; passive: passive / all sessions) |
| `Table_S7.csv` | Table S7 as printed |
| `Section_2_7.csv` | Every Section 2.7 and Table S7-note value, formatted as in the text |
| `figure2_source.csv` | 51 ADT × game × day cells with ≥ 1 session (day 0 = familiarisation days pooled): level_last_session (plotted), level of the last non-passive session, n_sessions, n_nonpassive |
| `Figure2_plotted_values.csv` | The plotted series: 51 participants × 18 games × training days 1–19, with status (observed / carried forward / before the first session) |
| `Figure2.png`, `Figure2.pdf` | Figure 2 |

**Sitting rule (Section 2.7).** Computed from start_offset_min and duration_s, which give the same within-day differences as the logged clock times. Within each logged day, all sessions (qualifying and passive) are sorted by (start, end). A session opens a new sitting when its start is more than 15 min after the latest end time of the sessions already in the current sitting. Sitting span = latest end − first start. A day meets the requirement when its sitting spans sum to at least 90 min.
