"""Corrected Experiment 1 demographic summary (analysed sample: ADT 51, LDT 47)."""
import pandas as pd
from scipy.stats import ttest_ind, chi2_contingency, fisher_exact
from shared import inputs, save


def main():
    data, people = inputs()
    # analysed sample only (participants with cognitive data: ADT 51, LDT 47; roster-only completer P149 excluded)
    selection = people[people.group.isin(['A','B']) & people.participant_id.isin(data.participant_id)].copy()
    rows = []
    for group in 'AB':
        cohort = selection[selection.group==group]
        rows.append(dict(group=group, n=len(cohort), with_cognitive_data=cohort.participant_id.isin(data.participant_id).sum(),
                         age_mean=cohort.age_at_test.mean(),age_sd=cohort.age_at_test.std(),
                         male=(cohort.sex==1).sum(),female=(cohort.sex==2).sum(),
                         stage_1=(cohort.education_stage==1).sum(),stage_2=(cohort.education_stage==2).sum()))
    frame = pd.DataFrame(rows)
    age_adt = selection.loc[selection.group=='A','age_at_test']
    age_ldt = selection.loc[selection.group=='B','age_at_test']
    frame['age_t'] = ttest_ind(age_adt,age_ldt,equal_var=True).statistic
    frame['age_p'] = ttest_ind(age_adt,age_ldt,equal_var=True).pvalue
    for field in ('sex','education_stage'):
        table = pd.crosstab(selection.group,selection[field])
        _, p, _, expected = chi2_contingency(table,correction=False)
        frame[f'{field}_p'] = fisher_exact(table.to_numpy()).pvalue if (expected<5).any() else p
    save('Table_2',frame,'demographics',selection,'Experiment 1 demographics, analysed sample (ADT 51 / LDT 47)')


if __name__ == '__main__':
    main()
