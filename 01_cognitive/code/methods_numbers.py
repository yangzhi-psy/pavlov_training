"""Methods numbers (Sections 2.1 and 2.8.5), from this release's data/ files only.

- Text_outlier_counts: observations removed by the 1.5 x IQR screening, per primary outcome and group (A = ADT,
  B = LDT, C = recreational gaming): present in cognitive_long_no_outlier_removal.csv but missing in cognitive_long.csv.
- Text_power: post hoc sensitivity of the analysed Experiment 1 sample (ADT 51, LDT 47; two-sided alpha .05,
  independent-samples t test) and the per-group n needed for d = 0.31 and 0.28 at 80% power.
"""
import math

import pandas as pd
from statsmodels.stats.power import TTestIndPower
from shared import DATA, OUTCOMES, inputs, save


def main():
    columns = list(OUTCOMES.values())
    screened = pd.read_csv(DATA / 'cognitive_long.csv', usecols=['participant_id', 'group', 'time', *columns]).set_index(['participant_id', 'time'])
    raw = pd.read_csv(DATA / 'cognitive_long_no_outlier_removal.csv', usecols=['participant_id', 'group', 'time', *columns]).set_index(['participant_id', 'time'])
    raw = raw.loc[raw.index.intersection(screened.index)]
    rows = []
    for outcome, column in OUTCOMES.items():
        removed = raw[column].notna() & screened.loc[raw.index, column].isna()
        counts = {g: int((removed & (raw.group == g)).sum()) for g in 'ABC'}
        rows.append(dict(outcome=outcome, column=column, removed_adt=counts['A'], removed_ldt=counts['B'], removed_control=counts['C'],
                         removed_total=sum(counts.values())))
    save('Text_outlier_counts', pd.DataFrame(rows), 'methods_numbers', raw.reset_index(), 'Observations removed by the 1.5 x IQR screening')

    data, people = inputs()
    analysed = data.loc[data.group.isin(['A', 'B'])].groupby('group').participant_id.nunique()
    n_adt, n_ldt = int(analysed['A']), int(analysed['B'])
    power = TTestIndPower()
    rows = [dict(quantity='minimum detectable d', power=p, d=power.solve_power(nobs1=n_adt, ratio=n_ldt / n_adt, alpha=.05, power=p),
                 n_per_group=None, n_adt=n_adt, n_ldt=n_ldt) for p in (.80, .90)]
    for d in (.31, .28):
        n = power.solve_power(effect_size=d, alpha=.05, power=.80, ratio=1.0)
        rows.append(dict(quantity='n per group for d', power=.80, d=d, n_per_group=n, n_per_group_rounded_up=math.ceil(n)))
    save('Text_power', pd.DataFrame(rows), 'methods_numbers', pd.DataFrame({'group': ['A', 'B'], 'n': [n_adt, n_ldt]}),
         'Post hoc power (independent-samples t test, two-sided alpha .05)')
    print(pd.DataFrame(rows).round(3).to_string(index=False))


if __name__ == '__main__':
    main()
