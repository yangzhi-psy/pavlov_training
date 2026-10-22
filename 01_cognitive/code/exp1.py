"""Experiment 1 primary LRTs, paired descriptives, and change CIs."""
import numpy as np
import pandas as pd
from scipy.stats import t as student_t
from shared import OUTCOMES, adjust, inputs, lrt, sample, save


def main():
    data, people = inputs()
    rows, descriptions, intervals = [], [], []
    for outcome, column in OUTCOMES.items():
        observations = sample(data, 'AB', column)
        result, _, full = lrt(observations, 'AB')
        result.update(outcome=outcome, column=column, n_adt=observations.loc[observations.group=='A','ID'].nunique(),
                      n_ldt=observations.loc[observations.group=='B','ID'].nunique())
        rows.append(result)
        intervals.append(dict(**result,
                              adt_minus_ldt_improvement=result['beta'] if 'RT' in column else -result['beta']))
        for group in 'ABC':
            subset = data.loc[data.group==group, ['participant_id', 'time', column]]
            pivot = subset.pivot(index='participant_id', columns='time', values=column).dropna()
            change = pivot[1]-pivot[0]
            pre, post = (subset.loc[subset.time==point, column].dropna() for point in (0,1))
            paired_t = change.mean()/(change.std()/np.sqrt(len(change)))
            descriptions.append(dict(outcome=outcome, column=column, group=group,
                                     pre_n=len(pre), pre_mean=pre.mean(), pre_sd=pre.std(),
                                     post_n=len(post), post_mean=post.mean(), post_sd=post.std(),
                                     paired_n=len(pivot), dz=abs(change.mean()/change.std()),
                                     paired_t=paired_t, paired_p=2*student_t.sf(abs(paired_t),len(change)-1)))
    results = adjust(pd.DataFrame(rows))
    descriptive = pd.DataFrame(descriptions)
    table = results.merge(descriptive.loc[descriptive.group=='A', ['column','dz','paired_n','pre_mean','post_mean']]
                          .add_prefix('adt_'), left_on='column', right_on='adt_column').drop(columns='adt_column')
    table = table.merge(descriptive.loc[descriptive.group=='B', ['column','dz','paired_n','pre_mean','post_mean']]
                        .add_prefix('ldt_'), left_on='column', right_on='ldt_column').drop(columns='ldt_column')
    save('Table_3', table, 'exp1', data.loc[data.group.isin(['A','B'])], 'Experiment 1: ADT versus LDT')
    save('Table_S3', descriptive, 'exp1', data, 'Observed pre/post descriptions and paired change')
    save('Table_3_CI', pd.DataFrame(intervals), 'exp1', data.loc[data.group.isin(['A','B'])], 'Difference-in-change Wald 95% confidence intervals')


if __name__ == '__main__':
    main()
