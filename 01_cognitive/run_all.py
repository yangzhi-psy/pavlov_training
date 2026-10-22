"""Run all analyses using only this release's data/ files."""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent / 'code'))
import demographics
import exp1
import exp2
import matching
import age_time
import bayes
import sensitivity
import figure1
import section31_checks
import methods_numbers


def main():
    for module in (demographics, exp1, exp2, matching, age_time, bayes, sensitivity, figure1, section31_checks, methods_numbers):
        print('Running', module.__name__, flush=True)
        module.main()
    print('All cognitive outputs generated.')


if __name__ == '__main__':
    main()
