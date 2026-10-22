"""Figure 3, Table S4 and Table S8: in-game test-task RT vs standardized cognitive measures (posttest).

Run:  python run_figure3_tableS4_tableS8.py        (Python 3 with numpy, pandas, scipy, statsmodels, matplotlib)
Inputs:  inputs/test_task_trials_pcode.csv (one row per trial of the five in-game test tasks, 97 included participants,
         P-codes) and ../01_cognitive/data/cognitive_long.csv (public cognitive data; posttest = time 1).
Outputs (outputs/): figure3_tableS4_results.csv (the one computation both Figure 3 and Table S4 read), Figure3.png,
                   Figure3_caption.txt, TableS4.csv, TableS8.csv, included_participants_rule_i_Pcodes.csv.

Definitions
- RT: mean of all per-trial response times (SubGameDuration, s) over the participant's NON-PASSIVE sessions of the task at
  the level. Passive = zero correct responses or < 0.5 x the mean correct count of the same game and level (manuscript).
- Shared levels: ColorJudgement 13, Singler 8, MatchCard 12, Pack 8, Toilet 18.
- Figure 3 / Table S4: rule (i) - participants with >= 1 non-passive session at the shared level of ALL five tasks
  (n = 94); 5 tasks x 5 standard measures = 25 Spearman correlations; 95% CI by Fisher z; BH-FDR across all 25.
- Table S8: domain-matched pairs at each listed level, every included participant with RT at that level and the score
  (descriptive, uncorrected).
Ported without change of logic from the internal scripts that produced the manuscript values; only the P-code inputs,
the output names, LF line endings and the caption wording (synchronised with the manuscript) differ."""
import os
import numpy as np, pandas as pd
from scipy import stats as sps
from statsmodels.stats.multitest import multipletests
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

HERE = os.path.dirname(os.path.abspath(__file__))
IN, OUT = os.path.join(HERE, "inputs"), os.path.join(HERE, "outputs")
os.makedirs(OUT, exist_ok=True)
LEVEL = {"ColorJudgment_1": 13, "Singler_1": 8, "MatchCard_1": 12, "Pack_1": 8, "Toilet_1": 18}
LEVELS_B = {"ColorJudgment_1": [8, 11, 13], "Singler_1": [4, 6, 8], "MatchCard_1": [4, 6, 8, 10, 12], "Pack_1": [4, 6, 8], "Toilet_1": [8, 10, 12, 14, 16, 18]}
DISP = {"ColorJudgment_1": "ColorJudgement", "Singler_1": "Singler", "MatchCard_1": "MatchCard", "Pack_1": "Pack", "Toilet_1": "Toilet"}
STD = ["GoNogo_d", "Nback_2VS0_RT", "MRT_rotate_RT", "ANT_execution", "Raven_2more_ACC"]
STD_LABEL = {"GoNogo_d": "Go/No-Go d′", "Nback_2VS0_RT": "N-back 2-vs-0 RT", "MRT_rotate_RT": "MRT rotation RT",
             "ANT_execution": "ANT executive control", "Raven_2more_ACC": "Raven ≥2-element ACC"}
MATCH = {"ColorJudgment_1": "GoNogo_d", "Singler_1": "Raven_2more_ACC", "MatchCard_1": "Nback_2VS0_RT", "Pack_1": "MRT_rotate_RT", "Toilet_1": "ANT_execution"}

T = pd.read_csv(os.path.join(IN, "test_task_trials_pcode.csv"))
cog = pd.read_csv(os.path.join(HERE, os.pardir, "01_cognitive", "data", "cognitive_long.csv"))
post = cog[cog.time == 1].set_index("participant_id")
inc = sorted(T.participant_id.unique())
print(f"included participants with test-task data: {len(inc)}; trial rows {len(T)}")

# ---------------- Figure 3 / Table S4 computation (compute_figure3_tableS4.py)
t = T[(T.passive == "N") & (T.hardmod == T.game_key.map(LEVEL))]
rt = t.groupby(["participant_id", "game_key"]).rt_s.agg(["mean", "size"]).rename(columns={"mean": "rt", "size": "n_trials"})
has = {gk: set(rt.xs(gk, level="game_key").index) for gk in LEVEL}
sub = sorted(set.intersection(*has.values()))
print(f"rule (i) subsample: n = {len(sub)}")
rows = []
for gk in LEVEL:
    r = rt.xs(gk, level="game_key").rt
    for std in STD:
        d = pd.DataFrame({"rt": r.reindex(sub), "s": post[std].reindex(sub)}).dropna()
        n = len(d); rho, p = sps.spearmanr(d.rt, d.s)
        z, se = np.arctanh(rho), 1 / np.sqrt(n - 3)
        rows.append(dict(task=DISP[gk], game_key=gk, shared_level=LEVEL[gk], standard_measure=std, standard_label=STD_LABEL[std],
                         domain_matched=MATCH[gk] == std, n=n, rho=rho, p=p, ci_low=np.tanh(z - 1.96 * se), ci_high=np.tanh(z + 1.96 * se)))
R = pd.DataFrame(rows)
R["p_fdr"] = multipletests(R.p, method="fdr_bh")[1]
R["stars_uncorrected"] = np.select([R.p < .001, R.p < .01, R.p < .05], ["***", "**", "*"], "")
R.to_csv(os.path.join(OUT, "figure3_tableS4_results.csv"), index=False, lineterminator="\n")
pd.DataFrame({"participant_id": sub}).to_csv(os.path.join(OUT, "included_participants_rule_i_Pcodes.csv"), index=False, lineterminator="\n")

# ---------------- Figure 3, Table S4, caption (render_figure3_tableS4.py; reads the results file only)
R = pd.read_csv(os.path.join(OUT, "figure3_tableS4_results.csv"))
TASKS = ["ColorJudgement", "Singler", "MatchCard", "Pack", "Toilet"]
fmt3 = lambda v: f"{v:.3f}".replace("0.", ".", 1) if v >= 0 else f"−{abs(v):.3f}".replace("0.", ".", 1)
pfmt = lambda p: "< .001" if p < .001 else f"{p:.3f}".lstrip("0")
plt.rcParams.update({"font.family": "Arial", "font.weight": "bold", "pdf.fonttype": 42})
M = R.pivot(index="standard_measure", columns="task", values="rho").loc[STD, TASKS]
ST = R.pivot(index="standard_measure", columns="task", values="stars_uncorrected").loc[STD, TASKS].fillna("")
LV = R.drop_duplicates("task").set_index("task").shared_level
vmax = float(np.ceil(np.abs(M.values).max() * 10) / 10)
fig = plt.figure(figsize=(8.0, 6.0), dpi=100, facecolor="white")
L0, B0, CW, RH, GAP = 0.26, 0.16, 0.118, 0.145, 0.012
cmap = plt.get_cmap("viridis")
for j, task in enumerate(TASKS):
    ax = fig.add_axes([L0 + j * (CW + GAP), B0, CW, RH * 5])
    im = ax.imshow(M[[task]].values, cmap=cmap, vmin=-vmax, vmax=vmax, aspect="auto")
    for i, std in enumerate(STD):
        v = M.loc[std, task]; c = "white"
        ax.text(0, i - 0.08, f"{v:.3f}", ha="center", va="center", color=c, fontsize=10.5, fontweight="normal")
        if ST.loc[std, task]: ax.text(0, i + 0.22, ST.loc[std, task], ha="center", va="center", color=c, fontsize=15, fontweight="bold")
    ax.set_xticks([0]); ax.set_xticklabels([f"RT_{int(LV[task])}"], rotation=45, ha="right", fontsize=9.5)
    ax.set_yticks(range(5)); ax.set_yticklabels([f"{s}_after" for s in STD] if j == 0 else [], fontsize=9.5)
    ax.set_title(task, fontsize=11, fontweight="bold", pad=6)
    for e in np.arange(-0.5, 5, 1): ax.axhline(e, color="#808080", lw=1)
    for s in ax.spines.values(): s.set_color("#808080")
    ax.tick_params(length=4, width=1)
    if j > 0: ax.tick_params(axis="y", left=False)
cax = fig.add_axes([L0 + 5 * (CW + GAP) + 0.005, B0, 0.025, RH * 5])
cb = fig.colorbar(im, cax=cax); cb.ax.tick_params(labelsize=9)
fig.savefig(os.path.join(OUT, "Figure3.png"), dpi=300, facecolor="white"); plt.close(fig)
n_star_fig = int((ST != "").values.sum())
TS4 = pd.DataFrame({"In-game task": R.task + " (level " + R.shared_level.astype(str) + ")", "Standard measure": R.standard_label,
                    "ρ": R.rho.map(fmt3), "95% CI": "[" + R.ci_low.map(fmt3) + ", " + R.ci_high.map(fmt3) + "]",
                    "p": R.p.map(pfmt), "pFDR": R.p_fdr.map(pfmt), "n": R.n})
TS4.to_csv(os.path.join(OUT, "TableS4.csv"), index=False, encoding="utf-8-sig", lineterminator="\n")
n_sig_table = int((R.p < .05).sum())
print(f"consistency: asterisked cells in Figure 3 = {n_star_fig}; Table S4 rows with p < .05 = {n_sig_table}")
assert n_star_fig == n_sig_table
nmin, nmax = R.n.min(), R.n.max()
best = R.loc[R.p_fdr.idxmin()]; surv = R[R.p_fdr < .05]
cap = ("Figure 3. Spearman correlations between response time (RT) on the five in-game test tasks and the standardized cognitive "
       "measures at posttest. Each column is one in-game task at its shared difficulty level (ColorJudgement 13, Singler 8, "
       "MatchCard 12, Pack 8, Toilet 18); RT is the mean per-trial response time of the participant’s non-passive sessions at that "
       f"level. The analysis includes the 94 participants with at least one non-passive session at the shared level of all five tasks "
       f"(n = {nmin}–{nmax} per pair, depending on missing standardized scores). Cell values are Spearman ρ; colour encodes ρ. "
       "Asterisks mark uncorrected p values (* p < .05, ** p < .01, *** p < .001). After Benjamini–Hochberg correction across all 25 "
       f"pairs, the smallest pFDR is {pfmt(best.p_fdr)} ({best.task}–{best.standard_label}); " +
       ("no correlation survives FDR correction." if surv.empty else f"pairs surviving FDR correction: {', '.join(surv.task + '–' + surv.standard_label)}."))
assert len(sub) == 94, "caption states 94; subsample differs"
open(os.path.join(OUT, "Figure3_caption.txt"), "w", encoding="utf-8", newline="\n").write(cap + "\n")

# ---------------- Table S8 (compute_tableS8.py, panel B)
s8 = T[T.game_key.isin(LEVEL) & (T.passive == "N")]
RT = s8.groupby(["game_key", "hardmod", "participant_id"]).rt_s.mean()


def corr(gk, lvl):
    if (gk, lvl) not in RT.index.droplevel(2): return 0, np.nan, np.nan
    r = RT.loc[(gk, lvl)]
    d = pd.DataFrame({"rt": r, "s": post[MATCH[gk]].reindex(r.index)}).dropna()
    if len(d) < 5: return len(d), np.nan, np.nan
    rho, p = sps.spearmanr(d.rt, d.s); return len(d), rho, p


B = pd.DataFrame([dict(task=DISP[gk], standard_measure=MATCH[gk], level=lv, **dict(zip(("n", "rho", "p"), corr(gk, lv))))
                  for gk, lvs in LEVELS_B.items() for lv in lvs])
B.to_csv(os.path.join(OUT, "TableS8.csv"), index=False, lineterminator="\n")
print("done:", sorted(os.listdir(OUT)))
