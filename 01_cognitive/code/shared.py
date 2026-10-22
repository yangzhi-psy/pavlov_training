"""Shared public-data loaders, MixedLM inference, and output packaging."""
import math
import warnings
from pathlib import Path

import numpy as np
import pandas as pd
from scipy.integrate import quad
from scipy.stats import chi2, norm
from statsmodels.formula.api import mixedlm
from statsmodels.stats.multitest import multipletests

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / 'data'
OUTPUT = ROOT / 'outputs'
OUTCOMES = {
    'MRT rotation RT': 'MRT_rotate_RT',
    'Raven >=2-element ACC': 'Raven_2more_ACC',
    'N-back 2-vs-0 RT': 'Nback_2VS0_RT',
    'ANT executive RT': 'ANT_execution',
    "Go/No-Go d'": 'GoNogo_d',
}
warnings.filterwarnings('ignore', category=UserWarning)
warnings.filterwarnings('ignore', category=RuntimeWarning)


def inputs(untrimmed=False):
    filename = 'cognitive_long_no_outlier_removal.csv' if untrimmed else 'cognitive_long.csv'
    data = pd.read_csv(DATA / filename)
    people = pd.read_csv(DATA / 'participants.csv')
    assert data.participant_id.nunique() == 148
    data = data.merge(people[['participant_id', 'age_at_test']], on='participant_id', validate='many_to_one')
    return data, people


def sample(data, groups, column):
    return data.loc[data.group.isin(list(groups)), ['participant_id', 'group', 'time', 'age_at_test', column]].dropna().rename(
        columns={'participant_id': 'ID', 'age_at_test': 'age', column: 'y'})


def model_pair(observations, specification='without_age'):
    reduced, full = {
        'without_age': ('y ~ C(group) + time', 'y ~ C(group) * time'),
        'age': ('y ~ C(group) + time + age', 'y ~ C(group) * time + age'),
        'age_time': ('y ~ C(group) + time + age_c + age_c:time',
                     'y ~ C(group) * time + age_c + age_c:time'),
    }[specification]
    fits = [mixedlm(formula, observations, groups=observations.ID).fit(
        reml=False, method='powell', disp=False) for formula in (reduced, full)]
    return fits


def lrt(observations, groups, specification='without_age', center=None):
    observations = observations.copy()
    if center is not None:
        observations['age_c'] = observations.age - center
    reduced, full = model_pair(observations, specification)
    assert reduced.converged and full.converged
    delta = max(0., 2 * (full.llf - reduced.llf))
    name = f'C(group)[T.{groups[1]}]:time'
    beta, se = full.params[name], full.bse[name]
    return dict(chi2=delta, p=chi2.sf(delta, 1), beta=beta, se=se,
                ci_lower=beta-norm.ppf(.975)*se, ci_upper=beta+norm.ppf(.975)*se,
                n_observations=len(observations), n_participants=observations.ID.nunique()), reduced, full


def adjust(frame, by=None):
    frame = frame.copy()
    if by:
        for _, subset in frame.groupby(by, sort=False):
            frame.loc[subset.index, 'pFDR'] = multipletests(subset.p, method='fdr_bh')[1]
    else:
        frame['pFDR'] = multipletests(frame.p, method='fdr_bh')[1]
    return frame


def save(name, frame, script, source, title=None):
    directory = OUTPUT / name
    directory.mkdir(parents=True, exist_ok=True)
    frame.to_csv(directory / f'{name}.csv', index=False, float_format='%.17g', lineterminator='\n')
    (directory / f'{name}.md').write_text(f'# {title or name}\n\n' + frame.to_markdown(index=False, floatfmt='.6g') + '\n', newline='\n')
    source.to_csv(directory / 'source_data.csv', index=False, float_format='%.17g', lineterminator='\n')
    (directory / 'build.py').write_text(
        '"""Regenerate this output from the public data directory."""\n'
        'import sys\nfrom pathlib import Path\n'
        "sys.path.insert(0, str(Path(__file__).resolve().parents[2] / 'code'))\n"
        f'from {script} import main\nmain()\n', newline='\n')


def jzs_bf10(t_value, df, n_effective, scale=math.sqrt(2)/2):
    def integrand(position):
        if position == 0:
            return 0.
        multiplier = 1 + n_effective*scale**2/(2*position**2)
        log_ratio = (-math.log(multiplier)/2 + (df+1)/2 *
                     (math.log1p(t_value**2/df) - math.log1p(t_value**2/(df*multiplier))))
        return 2/math.sqrt(math.pi)*math.exp(-position**2+log_ratio)
    result, error = quad(integrand, 0, np.inf, epsabs=1e-11, epsrel=1e-11)
    assert error < 1e-8
    return result
