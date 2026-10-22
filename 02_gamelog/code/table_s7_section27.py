"""Training exposure (Table S7, Section 2.7) from the public session data.

Reads data/sessions.csv and data/participants.csv and writes to outputs/:
  daily_metrics.csv        one row per participant x logged day (sessions, active time, sittings, 90-min requirement)
  participant_metrics.csv  one row per participant (exposure measures)
  group_results.csv        ADT vs LDT: median [IQR], Mann-Whitney U (for ADT, two-sided), p, pooled values
  Table_S7.csv             Table S7 as printed
  Section_2_7.csv          every Section 2.7 / Table S7-note number, with the sentence it appears in

Definitions (Section 2.7):
  - session start = logged end time - duration (released as a within-day offset, start_offset_min);
  - passive session: flag in the data (zero correct responses, or fewer than 0.5 x the mean correct count of all
    sessions of the same game at the same level; benchmark in data/passive_benchmark.csv); qualifying = not passive;
  - total active training time = summed duration of qualifying sessions on all logged days;
  - sitting: within each logged day, sessions (qualifying and passive) are sorted by (start, end); a session opens a
    new sitting when it starts more than 15 min after the latest end time of the sessions already in the sitting;
    sitting span = latest end - first start; a day meets the requirement when its sitting spans sum to >= 90 min;
  - training days exclude the familiarisation (installation) day(s); days after training day 19 are included.
"""
from pathlib import Path

import numpy as np
import pandas as pd
from scipy.stats import mannwhitneyu

ROOT = Path(__file__).resolve().parents[1]
DATA, OUT = ROOT / 'data', ROOT / 'outputs'
GAP_S, REQUIRED_S = 15 * 60, 90 * 60


def write_csv(frame, name):
    frame.to_csv(OUT / name, index=False, lineterminator='\n', float_format='%.17g')


def sittings(day):
    """Number of sittings and summed sitting span (s) of one logged day.

    Session start = within-day offset (minutes since the first session start of the day, 4 decimals; x 60 and rounded
    gives whole seconds); session end = start + duration (= the logged end time, shifted by the same day constant)."""
    start = (day.start_offset_min * 60).round().to_numpy(float)
    end = start + day.duration_s.to_numpy(float)
    order = np.lexsort((end, start))
    n, span, first, latest = 0, 0., None, None
    for i in order:
        if first is None or start[i] - latest > GAP_S:
            if first is not None:
                span += latest - first
            n, first, latest = n + 1, start[i], end[i]
        else:
            latest = max(latest, end[i])
    return n, span + (latest - first)


def daily_metrics(S):
    rows = []
    for (pid, group, day), d in S.groupby(['participant', 'group', 'day_index'], sort=True):
        q = d[d.passive == 'N']
        n_sit, span = sittings(d)
        rows.append(dict(participant=pid, group=group, day_index=day, training_day=d.training_day.iloc[0],
                         training_day_number=d.training_day_number.iloc[0], total_sessions=len(d), qualifying_sessions=len(q),
                         passive_sessions=len(d) - len(q), active_training_time_min=q.duration_s.sum() / 60,
                         n_sittings=n_sit, session_span_min=span / 60, met_90min='Y' if span >= REQUIRED_S else 'N'))
    D = pd.DataFrame(rows)
    D['training_day_number'] = D.training_day_number.astype('Int64')
    return D


def participant_metrics(S, D, P):
    rows = []
    for pid, d in S.groupby('participant', sort=True):
        q = d[d.passive == 'N']
        dd = D[D.participant == pid]
        td = dd[dd.training_day == 'Y']
        rows.append(dict(
            participant=pid, group=d.group.iloc[0],
            total_active_time_s=q.duration_s.sum(), total_active_time_h=q.duration_s.sum() / 3600,
            total_sessions=len(d), qualifying_sessions=len(q), passive_sessions=len(d) - len(q),
            passive_rate_pct=100 * (len(d) - len(q)) / len(d),
            sessions_training_days=int(td.total_sessions.sum()), qualifying_training_days=int(td.qualifying_sessions.sum()),
            days_logged=len(dd), logged_days_played_incl_familiarisation=int((dd.qualifying_sessions > 0).sum()),
            pretraining_days=int((dd.training_day == 'N').sum()), training_days_counted=len(td),
            training_days_played=int((td.qualifying_sessions > 0).sum()), days_met_90min=int((td.met_90min == 'Y').sum()),
            compliance_90min_pct_days=100 * (td.met_90min == 'Y').sum() / len(td),
            peak_training_difficulty=q.loc[q.game_type == 'training', 'level'].max(),
            peak_test_difficulty_pooled=q.loc[q.game_type == 'test', 'level'].max()))
    M = pd.DataFrame(rows)
    return M.merge(P[['participant', 'included_in_log_sample']], on='participant', how='left')


MEASURES = [
    ('total_active_time_s', 'Total active training time (s)', 's'),
    ('total_active_time_h', 'Total active training time (h)', 'h'),
    ('qualifying_sessions', 'Qualifying (non-passive) sessions, all logged days', 'count'),
    ('total_sessions', 'All sessions completed, all logged days', 'count'),
    ('sessions_training_days', 'All sessions completed, training days only', 'count'),
    ('qualifying_training_days', 'Qualifying sessions, training days only', 'count'),
    ('logged_days_played_incl_familiarisation', 'Logged days played (incl. familiarisation)', 'days'),
    ('training_days_played', 'Training days played', 'days'),
    ('compliance_90min_pct_days', 'Daily 90-min compliance, participant level', '% of training days'),
    ('passive_sessions', 'Passive sessions (count)', 'count'),
    ('passive_rate_pct', 'Passive-session rate, participant level', '% of sessions'),
    ('peak_training_difficulty', 'Peak difficulty, training games', 'level'),
    ('peak_test_difficulty_pooled', 'Peak difficulty, test tasks (pooled)', 'level'),
]


def num(v, decimals=2):
    """Manuscript number style: thousands separator, at most two decimals, trailing zeros dropped."""
    s = f'{round(float(v), decimals):,.{decimals}f}'
    return s.rstrip('0').rstrip('.') if '.' in s else s


def p_text(p):
    return '< .001' if p < .001 else f'{p:.3f}'.lstrip('0')


def p_eq(p):
    return 'p < .001' if p < .001 else f'p = {p_text(p)}'


def group_results(M, D):
    A, L = M[M.group == 'ADT'], M[M.group == 'LDT']
    rows = []
    for col, label, unit in MEASURES:
        a, b = A[col].astype(float).to_numpy(), L[col].astype(float).to_numpy()
        t = mannwhitneyu(a, b, alternative='two-sided')
        q = lambda v: (np.median(v), np.percentile(v, 25), np.percentile(v, 75))
        rows.append(dict(column=col, measure=label, unit=unit, ADT_n=len(a), **dict(zip(('ADT_median', 'ADT_Q1', 'ADT_Q3'), q(a))),
                         LDT_n=len(b), **dict(zip(('LDT_median', 'LDT_Q1', 'LDT_Q3'), q(b))), U_ADT=t.statistic, p=t.pvalue))
    G = pd.DataFrame(rows)
    pooled = {}
    for g, x in (('ADT', A), ('LDT', L)):
        td = D[D.participant.isin(x.participant) & (D.training_day == 'Y')]
        pooled[g] = dict(days_met=int((td.met_90min == 'Y').sum()), training_days=len(td),
                         passive=int(x.passive_sessions.sum()), sessions=int(x.total_sessions.sum()))
    return G, pooled


def main():
    OUT.mkdir(exist_ok=True)
    S = pd.read_csv(DATA / 'sessions.csv').sort_values(['participant', 'session_order'])
    P = pd.read_csv(DATA / 'participants.csv')
    inc = set(P.loc[P.included_in_log_sample == 'Y', 'participant'])
    S = S[S.participant.isin(inc)]
    D = daily_metrics(S)
    M = participant_metrics(S, D, P)
    assert M.groupby('group').size().to_dict() == {'ADT': 51, 'LDT': 46}
    G, pooled = group_results(M, D)
    write_csv(D, 'daily_metrics.csv')
    write_csv(M, 'participant_metrics.csv')
    gp = G.copy()
    gp['pooled'] = ''
    gp.loc[gp.column == 'compliance_90min_pct_days', 'pooled'] = '; '.join(
        f"{g} {v['days_met']}/{v['training_days']} days = {100 * v['days_met'] / v['training_days']:.2f}%" for g, v in pooled.items())
    gp.loc[gp.column.isin(['passive_sessions', 'passive_rate_pct']), 'pooled'] = '; '.join(
        f"{g} {v['passive']}/{v['sessions']} sessions = {100 * v['passive'] / v['sessions']:.2f}%" for g, v in pooled.items())
    write_csv(gp, 'group_results.csv')

    g = G.set_index('column')
    def cell(col, grp, fixed=False):
        f = (lambda v: f'{v:.2f}') if fixed else num
        r = g.loc[col]
        return f'{f(r[grp + "_median"])} [{f(r[grp + "_Q1"])}, {f(r[grp + "_Q3"])}]'
    s7 = [('Total active training time (h)', 'total_active_time_h', True), ('Sessions completed', 'total_sessions', False),
          ('Training days played', 'training_days_played', False),
          ('Training days meeting the 1.5-h requirement (%)', 'compliance_90min_pct_days', False), ('Passive sessions', 'passive_sessions', False)]
    T = pd.DataFrame([{'Measure': label, 'ADT (n = 51) Mdn [IQR]': cell(col, 'ADT', fx), 'LDT (n = 46) Mdn [IQR]': cell(col, 'LDT', fx),
                       'U': num(g.loc[col, 'U_ADT']), 'p': p_text(g.loc[col, 'p'])} for label, col, fx in s7])
    write_csv(T, 'Table_S7.csv')

    r = lambda col: g.loc[col]
    a, l = pooled['ADT'], pooled['LDT']
    sec = [
        ('Sec 2.7 active time', f"median {r('total_active_time_h').ADT_median:.1f} h vs. {r('total_active_time_h').LDT_median:.1f} h, "
                                f"U = {num(r('total_active_time_h').U_ADT)}, {p_eq(r('total_active_time_h').p)}"),
        ('Sec 2.7 training days played', f"median {num(r('training_days_played').ADT_median)} vs. {num(r('training_days_played').LDT_median)}, "
                                         f"U = {num(r('training_days_played').U_ADT)}, {p_eq(r('training_days_played').p)}"),
        ('Sec 2.7 sessions completed (LDT vs ADT)', f"median {num(r('total_sessions').LDT_median)} vs. {num(r('total_sessions').ADT_median)} across all logged days, "
                                                    f"including the familiarisation day; U = {num(r('total_sessions').U_ADT)}, {p_eq(r('total_sessions').p)}"),
        ('Sec 2.7 / Table S7 note pooled compliance', f"{100 * a['days_met'] / a['training_days']:.1f}% of training days in ADT ({a['training_days']} days) and "
                                                      f"{100 * l['days_met'] / l['training_days']:.1f}% in LDT ({l['training_days']} days); "
                                                      f"ADT {a['days_met']}/{a['training_days']}, LDT {l['days_met']}/{l['training_days']}"),
        ('Sec 2.7 compliance, participant level', f"participant-level median {r('compliance_90min_pct_days').ADT_median:.1f}% vs. "
                                                  f"{r('compliance_90min_pct_days').LDT_median:.1f}%, U = {num(r('compliance_90min_pct_days').U_ADT)}, "
                                                  f"{p_eq(r('compliance_90min_pct_days').p)}"),
        ('Sec 2.7 passive sessions', f"median {num(r('passive_sessions').ADT_median)} vs. {num(r('passive_sessions').LDT_median)} per participant, "
                                     f"U = {num(r('passive_sessions').U_ADT)}, {p_eq(r('passive_sessions').p)}; "
                                     f"{100 * a['passive'] / a['sessions']:.1f}% vs. {100 * l['passive'] / l['sessions']:.1f}% of all sessions"),
        ('Table S7 note pooled passive sessions', f"ADT {a['passive']:,} of {a['sessions']:,} sessions, {100 * a['passive'] / a['sessions']:.1f}%; "
                                                  f"LDT {l['passive']:,} of {l['sessions']:,}, {100 * l['passive'] / l['sessions']:.1f}%"),
        ('Sec 2.7 sample', f"ADT, n = {int(r('total_sessions').ADT_n)}; LDT, n = {int(r('total_sessions').LDT_n)}"),
    ]
    write_csv(pd.DataFrame(sec, columns=['item', 'value']), 'Section_2_7.csv')
    print(T.to_string(index=False))
    for item, value in sec:
        print(f'{item}: {value}')


if __name__ == '__main__':
    main()
