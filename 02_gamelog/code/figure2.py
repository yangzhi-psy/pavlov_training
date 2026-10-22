"""Figure 2: difficulty progression of the 51 ADT participants in the 18 games over training days 1-19.

Reads data/sessions.csv and data/participants.csv and writes to outputs/:
  figure2_source.csv          one row per participant x game x day with >= 1 session (day 0 = familiarisation day(s) pooled):
                              level of the last session (level_last_session; plotted), level of the last non-passive session,
                              session counts
  Figure2_plotted_values.csv  the plotted series (51 participants x 18 games x days 1-19) with status
  Figure2.png (300 dpi), Figure2.pdf

Daily value = level of the last session of that game that day (Section 2.7, Figure 2 caption). A day without a session
of that game carries the most recent value forward; before the first session on days 1-19 the day-0 value is held, or 0
if there is none. Lines are drawn in the original figure's order (participants.csv, figure2_line_order) and colours.
Panel layout and font sizes come from style/*.json (calibrated to the original figure). Font: Times New Roman.
"""
import json
from pathlib import Path

import numpy as np
import pandas as pd
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.ticker

ROOT = Path(__file__).resolve().parents[1]
DATA, OUT, STYLE = ROOT / 'data', ROOT / 'outputs', Path(__file__).resolve().parent / 'style'
GAMES = ['AlienLanguage', 'BBQ', 'ColorJudgement', 'CubesProjection', 'Delivery', 'InnerSpaceMap', 'Lines', 'MatchCard', 'Mines',
         'OneOrTwoSteps', 'Pack', 'Roadblocks', 'ServeFood', 'Shopping', 'Singler', 'SpaceStation', 'Toilet', 'Train']
TITLES = {g: g for g in GAMES}
TITLES['BBQ'] = 'Barbecue'
NDAYS = 19


def source():
    S = pd.read_csv(DATA / 'sessions.csv')
    P = pd.read_csv(DATA / 'participants.csv')
    order = list(P[P.figure2_line_order.notna()].sort_values('figure2_line_order').participant)
    assert len(order) == 51 and set(order) == set(P[(P.group == 'ADT') & (P.included_in_log_sample == 'Y')].participant)
    s = S[S.participant.isin(order)].sort_values(['participant', 'session_order']).copy()
    s['game'] = s.game.replace({'ColorJudgment': 'ColorJudgement'})
    s['day'] = np.where(s.training_day == 'Y', s.training_day_number, 0).astype(float).astype(int)
    g = s.groupby(['participant', 'game', 'day'])
    F = g.agg(n_sessions=('level', 'size'), n_nonpassive=('passive', lambda v: int((v == 'N').sum())),
              level_last_session=('level', 'last')).reset_index()
    F = F.join(s[s.passive == 'N'].groupby(['participant', 'game', 'day'])['level'].last().rename('level'), on=['participant', 'game', 'day'])
    F['level'] = F.level.astype('Int64')
    return F[['participant', 'game', 'day', 'level', 'n_sessions', 'n_nonpassive', 'level_last_session']], order


def series(obs, pid, g):
    cur = obs.get((pid, g, 0), 0.0)
    st0 = 'day0' if (pid, g, 0) in obs else 'zero'
    out, sts, seen = [], [], False
    for k in range(1, NDAYS + 1):
        if (pid, g, k) in obs:
            cur, seen = obs[(pid, g, k)], True
            sts.append('observed')
        else:
            sts.append('carried' if seen else f'pre_first_{st0}')
        out.append(cur)
    return np.array(out, float), sts


def draw(V, order, png, pdf):
    colors = ['#0072bd', '#d95319', '#edb120', '#7e2f8e', '#77ac30', '#4dbeee', '#a2142f']
    W, H, DPI = 1920, 987, 100
    PX = 72.0 / DPI
    axes = {d['game']: d for d in json.loads((STYLE / 'figure2_axes.json').read_text())}
    title_cal = json.loads((STYLE / 'title_calibration.json').read_text())
    base_title_pt = 16.5 * PX * 2.16
    plt.rcParams.update({'font.family': 'Times New Roman', 'svg.fonttype': 'none', 'pdf.fonttype': 42})
    ser = {g: [V[(V.participant == pid) & (V.game == g)].sort_values('day').level.values for pid in order] for g in GAMES}
    fig = plt.figure(figsize=(W / DPI, H / DPI), dpi=DPI, facecolor='white')
    for i, g in enumerate(GAMES):
        lo, hi = axes[g]['ylim_used']
        yt = list(axes[g]['yticks'])
        mx = float(np.nanmax(np.vstack(ser[g])))
        if mx > hi:                                        # never truncate: extend to the next multiple of 5
            step = yt[1] - yt[0]
            hi = float(np.ceil(mx / 5) * 5)
            yt = [float(t) for t in np.arange(0, hi + 1e-6, step)]
        xl, ytp, xr, yb = axes[g]['axes_px']
        ax = fig.add_axes([xl / W, 1 - yb / H, (xr - xl) / W, (yb - ytp) / H])
        for j, y in enumerate(ser[g]):
            ax.plot(np.arange(1, 20), y, color=colors[j % 7], lw=0.8333 * PX, solid_joinstyle='round', solid_capstyle='butt')
        ax.set_xlim(*axes[g]['xlim_used'])
        ax.set_ylim(lo, hi)
        ax.set_xticks([5, 10, 15, 20])
        ax.set_yticks(yt)
        cal = title_cal.get(g, {'scale': 1.0, 'dy_px': 0.0})
        ax.set_title(TITLES[g], fontsize=base_title_pt * cal['scale'], pad=9 + cal['dy_px'] * PX)
        if i % 6 == 0:
            ax.set_ylabel('Difficulty level', fontsize=12 * PX * 1.47)
        if i >= 12:
            ax.set_xlabel('Training day', fontsize=15 * PX * 1.97)
        for side in ('top', 'right'):
            ax.spines[side].set_visible(False)
        for side in ('left', 'bottom'):
            ax.spines[side].set_linewidth(0.8333 * PX)
            ax.spines[side].set_color('#262626')
        ax.yaxis.set_major_formatter(matplotlib.ticker.FuncFormatter(lambda v, _: f'{v:g}'))
        ax.tick_params(colors='#262626', labelsize=12 * PX * 1.3, width=0.8333 * PX, length=3, direction='in')
        assert max(float(np.nanmax(line.get_ydata())) for line in ax.get_lines()) <= ax.get_ylim()[1] and len(ax.get_lines()) == 51, g
    fig.savefig(png, dpi=300, facecolor='white')
    fig.savefig(pdf, facecolor='white', metadata={'CreationDate': None})
    plt.close(fig)


def main():
    OUT.mkdir(exist_ok=True)
    F, order = source()
    F.to_csv(OUT / 'figure2_source.csv', index=False, lineterminator='\n')
    obs = {(r.participant, r.game, int(r.day)): float(r.level_last_session) for r in F.itertuples()}
    rows = []
    for pid in order:
        for g in GAMES:
            y, sts = series(obs, pid, g)
            rows += [dict(participant=pid, game=g, panel_title=TITLES[g], day=k + 1, level=y[k], status=sts[k]) for k in range(NDAYS)]
    V = pd.DataFrame(rows)
    V.to_csv(OUT / 'Figure2_plotted_values.csv', index=False, lineterminator='\n')
    draw(V, order, OUT / 'Figure2.png', OUT / 'Figure2.pdf')
    print(f'figure2_source.csv: {len(F)} cells; Figure2_plotted_values.csv: {len(V)} rows; Figure2.png and Figure2.pdf written')


if __name__ == '__main__':
    main()
