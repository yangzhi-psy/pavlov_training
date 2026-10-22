"""No-outlier-removal mixed-model sensitivity (aligned processed dump)."""
import numpy as np
import pandas as pd
from shared import OUTCOMES, inputs, lrt, sample, save


def main():
    data, _ = inputs(untrimmed=True)
    rows = []
    for outcome, column in OUTCOMES.items():
        observations = sample(data,'AB',column)
        if not np.isfinite(observations.y).all():
            rows.append(dict(outcome=outcome,column=column,chi2=np.nan,p=np.nan,
                             note='Nonfinite GoNogo_d in processed no-outlier data; no valid fit'))
            continue
        result, _, _ = lrt(observations,'AB')
        rows.append(dict(outcome=outcome,column=column, **result,note='aligned processed; duplicate pretests masked'))
    save('Text_no_outlier_sensitivity',pd.DataFrame(rows),'sensitivity',data.loc[data.group.isin(['A','B'])],
         'Experiment 1 no-outlier-removal sensitivity')


if __name__ == '__main__':
    main()
