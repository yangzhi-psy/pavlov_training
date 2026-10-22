"""Full-sample Experiment 2: three age specifications."""
import pandas as pd
from shared import OUTCOMES, adjust, inputs, lrt, sample, save


def main():
    data, people = inputs()
    center = people.loc[people.group.isin(['A','C']), 'age_at_test'].mean()
    rows = []
    for outcome, column in OUTCOMES.items():
        observations = sample(data, 'AC', column)
        for specification in ('without_age','age','age_time'):
            result, _, full = lrt(observations, 'AC', specification, center)
            rows.append(dict(outcome=outcome, column=column, specification=specification,
                             age_center_mean=center, **result,
                             age_time_beta=full.params.get('age_c:time'),
                             age_time_wald_p=full.pvalues.get('age_c:time')))
    frame = adjust(pd.DataFrame(rows), 'specification')
    save('Table_4', frame, 'exp2', data.loc[data.group.isin(['A','C'])],
         'Experiment 2 full sample: three age specifications')


if __name__ == '__main__':
    main()
