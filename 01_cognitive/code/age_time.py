"""Age-by-time likelihood ratio tests and full-design collinearity."""
import numpy as np
import pandas as pd
from scipy.stats import chi2, norm, pointbiserialr, ttest_ind
from statsmodels.stats.outliers_influence import variance_inflation_factor
from shared import OUTCOMES, adjust, inputs, lrt, model_pair, sample, save


def main():
    data, people = inputs()
    rows = []
    for groups in ('AB','AC'):
        participants = people.loc[people.group.isin(list(groups)) & people.participant_id.isin(data.participant_id)]
        center = participants.age_at_test.mean()
        first = participants.loc[participants.group=='A','age_at_test']
        second = participants.loc[participants.group==groups[1],'age_at_test']
        for outcome, column in OUTCOMES.items():
            obs = sample(data,groups,column)
            obs['age_c'] = obs.age-center
            age_full = model_pair(obs,'age')[1]
            reduced, full = model_pair(obs,'age_time')
            result, _, _ = lrt(obs,groups,'age_time',center)
            chi = max(0.,2*(full.llf-age_full.llf))
            term = full.params['age_c:time']; se = full.bse['age_c:time']
            names = full.model.exog_names
            rows.append(dict(groups=groups, outcome=outcome, column=column, n_participants=obs.ID.nunique(),
                             age_center_mean=center, age_time_chi2=chi, age_time_lr_p=chi2.sf(chi,1),
                             age_time_beta=term, age_time_se=se, age_time_ci_lower=term-norm.ppf(.975)*se,
                             age_time_ci_upper=term+norm.ppf(.975)*se,
                             group_time_chi2=result['chi2'], group_time_p=result['p'],
                             vif_group_time=variance_inflation_factor(full.model.exog,names.index(f'C(group)[T.{groups[1]}]:time')),
                             vif_age_time=variance_inflation_factor(full.model.exog,names.index('age_c:time')),
                             age_adt_mean=first.mean(), age_other_mean=second.mean(),
                             welch_p=ttest_ind(second,first,equal_var=False).pvalue,
                             point_biserial_r=pointbiserialr((participants.group==groups[1]).astype(int),participants.age_at_test).statistic))
    frame = pd.DataFrame(rows)
    for groups in ('AB','AC'):
        index = frame.groups==groups
        frame.loc[index,'age_time_fdr_p'] = adjust(frame.loc[index].rename(columns={'age_time_lr_p':'p'})).pFDR.to_numpy()
    save('Table_S6', frame, 'age_time', data, 'Age-by-time tests and design collinearity')


if __name__ == '__main__':
    main()
