"""Deterministic 1:1 greedy age rematching (Table S5).

The birth-date-distance sensitivity match of Table S5 (32 pairs) needs birth-date information that is not part of the
public data; that row is available from the authors on request."""
import numpy as np
import pandas as pd
from scipy.stats import ttest_ind, chi2_contingency, fisher_exact
from shared import OUTCOMES, adjust, inputs, lrt, sample, save


def match(people, caliper):
    adt = people.loc[people.group=='A'].sort_values('participant_id')
    control = people.loc[people.group=='C'].sort_values('participant_id')
    key = 'age_at_test'
    used, rows = set(), []
    for subject in adt.itertuples(index=False):
        available = control.loc[(control.sex==subject.sex) &
                                (control.education_stage==subject.education_stage) &
                                ~control.participant_id.isin(used)].copy()
        available['distance'] = abs(available[key] - getattr(subject,key))
        available = available.loc[available.distance <= caliper].sort_values(['distance','participant_id'])
        if available.empty:
            continue
        chosen = available.iloc[0]
        used.add(chosen.participant_id)
        rows.extend([dict(pair=len(used), participant_id=identifier, distance_years=chosen.distance)
                     for identifier in (subject.participant_id,chosen.participant_id)])
    return pd.DataFrame(rows).merge(people, on='participant_id', validate='one_to_one')


def main():
    data, people = inputs()
    samples = [('primary_025',.25,19), ('age_010',.10,13)]
    rows, pairs = [], []
    for label, caliper, expected in samples:
        paired = match(people, caliper)
        assert paired.pair.nunique() == expected, (label, paired.pair.nunique())
        paired.insert(0,'matching_rule',label)
        pairs.append(paired)
        matched = data[data.participant_id.isin(paired.participant_id)]
        for outcome, column in OUTCOMES.items():
            result, _, _ = lrt(sample(matched,'AC',column),'AC')
            rows.append(dict(matching_rule=label, pairs=expected, outcome=outcome,
                             column=column, age_adt_mean=paired.loc[paired.group=='A','age_at_test'].mean(),
                             age_control_mean=paired.loc[paired.group=='C','age_at_test'].mean(), **result))
    frame = adjust(pd.DataFrame(rows),'matching_rule')
    source = pd.concat(pairs, ignore_index=True)
    save('Table_S5', frame, 'matching', source, 'Experiment 2 demographic rematching')
    source.to_csv((__import__('shared').OUTPUT / 'Table_S5' / 'matched_pairs.csv'),index=False,lineterminator='\n')
    primary = pairs[0]
    first = primary.loc[primary.group=='A','age_at_test']
    second = primary.loc[primary.group=='C','age_at_test']
    sex = pd.crosstab(primary.group, primary.sex).reindex(index=['A','C'], columns=[1,2], fill_value=0)
    chi, probability, _, expected = chi2_contingency(sex, correction=False)
    sex_p = fisher_exact(sex.to_numpy()).pvalue if (expected < 5).any() else probability
    demographics = primary.groupby('group').agg(n=('participant_id','count'), age_mean=('age_at_test','mean'),
                                                 age_sd=('age_at_test','std'), male=('sex',lambda x:(x==1).sum()),
                                                 female=('sex',lambda x:(x==2).sum()),
                                                 stage_1=('education_stage',lambda x:(x==1).sum()),
                                                 stage_2=('education_stage',lambda x:(x==2).sum())).reset_index()
    demographics['age_t'] = ttest_ind(first,second,equal_var=True).statistic
    demographics['age_p'] = ttest_ind(first,second,equal_var=True).pvalue
    demographics['sex_p'] = sex_p
    save('Table_S5_demographics', demographics, 'matching', primary, 'Experiment 2 matched demographics (corrected new match)')


if __name__ == '__main__':
    main()
