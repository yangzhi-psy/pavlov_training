"""BIC mixed-model and JZS paired-change Bayes factors."""
import math
import pandas as pd
from scipy.stats import ttest_ind
from shared import inputs, jzs_bf10, model_pair, sample, save


def main():
    data, _ = inputs()
    observations = sample(data,'AB','Nback_2VS0_RT')
    reduced, full = model_pair(observations)
    bic_bf10 = math.exp((reduced.bic-full.bic)/2)
    pivot = observations.pivot(index=['ID','group'],columns='time',values='y').dropna()
    changes = pivot[1]-pivot[0]
    adt = changes.loc[changes.index.get_level_values('group')=='A'].to_numpy()
    ldt = changes.loc[changes.index.get_level_values('group')=='B'].to_numpy()
    statistic = ttest_ind(adt,ldt,equal_var=True).statistic
    jzs = jzs_bf10(statistic,len(adt)+len(ldt)-2,len(adt)*len(ldt)/(len(adt)+len(ldt)))
    frame = pd.DataFrame([dict(outcome='Nback_2VS0_RT', BF_BIC=bic_bf10, BF_JZS=jzs,
                               paired_adt=len(adt), paired_ldt=len(ldt), t=statistic,
                               cauchy_scale=math.sqrt(2)/2)])
    save('Text_Bayes_factors',frame,'bayes',data.loc[data.group.isin(['A','B'])], 'Experiment 1 N-back Bayes factors')


if __name__ == '__main__':
    main()
