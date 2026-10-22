"""Section 3.1 robustness checks for Experiment 1 (ADT vs LDT), from this release's data/ files only.

- Text_exp1_age_adjusted: group x time LRT for the five primary outcomes without and with centred age at test as a
  fixed covariate (age centred at the mean of the analysed ADT/LDT participants), the change in chi-square, and BH-FDR
  within each model.
- Text_accuracy_nback: group x time LRT for N-back 2-vs-0 accuracy and the within-group |dz| of the pre-post change.
- Text_ANT_networks: group x time LRT for ANT alerting and orienting (Experiment 1).
All models: ML random-intercept MixedLM, LRT chi-square(1) (shared.lrt).
"""
import numpy as np
import pandas as pd
from statsmodels.stats.multitest import multipletests
from shared import OUTCOMES, inputs, lrt, sample, save


def dz(data, group, column):
    subset = data.loc[data.group == group, ['participant_id', 'time', column]]
    pivot = subset.pivot(index='participant_id', columns='time', values=column).dropna()
    change = pivot[1] - pivot[0]
    return abs(change.mean() / change.std()), len(pivot)


def main():
    data, people = inputs()
    analysed = people[people.group.isin(['A', 'B']) & people.participant_id.isin(data.participant_id)]
    center = analysed.age_at_test.mean()
    rows = []
    for outcome, column in OUTCOMES.items():
        observations = sample(data, 'AB', column)
        without, _, _ = lrt(observations, 'AB', 'without_age')
        centred = observations.copy()
        centred['age'] = centred.age - center
        with_age, _, _ = lrt(centred, 'AB', 'age')
        rows.append(dict(outcome=outcome, column=column,
                         n_adt=observations.loc[observations.group == 'A', 'ID'].nunique(),
                         n_ldt=observations.loc[observations.group == 'B', 'ID'].nunique(),
                         chi2_without_age=without['chi2'], p_without_age=without['p'],
                         chi2_with_age=with_age['chi2'], p_with_age=with_age['p']))
    age = pd.DataFrame(rows)
    age['pFDR_without_age'] = multipletests(age.p_without_age, method='fdr_bh')[1]
    age['pFDR_with_age'] = multipletests(age.p_with_age, method='fdr_bh')[1]
    age['delta_chi2'] = age.chi2_with_age - age.chi2_without_age
    age['age_center'] = center
    ab = data.loc[data.group.isin(['A', 'B'])]
    save('Text_exp1_age_adjusted', age, 'section31_checks', ab, 'Experiment 1 group x time tests without and with centred age')

    result, _, _ = lrt(sample(data, 'AB', 'Nback_2VS0_ACC'), 'AB')
    dz_adt, n_adt = dz(data, 'A', 'Nback_2VS0_ACC')
    dz_ldt, n_ldt = dz(data, 'B', 'Nback_2VS0_ACC')
    accuracy = pd.DataFrame([dict(outcome='N-back 2-vs-0 ACC', column='Nback_2VS0_ACC', chi2=result['chi2'], p=result['p'],
                                  beta=result['beta'], n_participants=result['n_participants'],
                                  dz_adt=dz_adt, paired_n_adt=n_adt, dz_ldt=dz_ldt, paired_n_ldt=n_ldt)])
    save('Text_accuracy_nback', accuracy, 'section31_checks', ab, 'Experiment 1 accuracy-based N-back')

    rows = []
    for outcome, column in (('ANT alerting', 'ANT_alert'), ('ANT orienting', 'ANT_orientation')):
        result, _, _ = lrt(sample(data, 'AB', column), 'AB')
        rows.append(dict(outcome=outcome, column=column, chi2=result['chi2'], p=result['p'], beta=result['beta'],
                         n_participants=result['n_participants']))
    save('Text_ANT_networks', pd.DataFrame(rows), 'section31_checks', ab, 'Experiment 1 ANT alerting and orienting')

    nback = age.loc[age.column == 'Nback_2VS0_RT', 'delta_chi2'].iloc[0]
    others = age.loc[age.column != 'Nback_2VS0_RT', 'delta_chi2'].abs().max()
    print(f'age-adjusted: N-back delta chi2 {nback:+.3f}; other outcomes max |delta| {others:.3f}')
    a = accuracy.iloc[0]
    print(f'accuracy N-back: chi2(1) = {a.chi2:.2f}, p = {a.p:.3f}; dz {dz_adt:.2f} / {dz_ldt:.2f}')
    for r in rows:
        print(f"{r['outcome']}: chi2(1) = {r['chi2']:.2f}, p = {r['p']:.2f}")


if __name__ == '__main__':
    main()
