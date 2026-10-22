"""Regenerate every result, table and figure of the release from the files in this folder.

Run from any directory:  python run_all.py
Steps: 01_cognitive (Figure 1, Tables 2-4, S3, S5, S6, Bayes factors, sensitivity analyses, Section 3.1 checks),
       02_gamelog (Table S7, Section 2.7, Figure 2), 03_validity (Figure 3, Tables S4 and S8).
Each step overwrites its outputs/ folder in place. All paths are relative to this file.
"""
import subprocess
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parent
STEPS = [
    ('01_cognitive', ['run_all.py']),
    ('02_gamelog', ['code/table_s7_section27.py']),
    ('02_gamelog', ['code/figure2.py']),
    ('03_validity', ['run_figure3_tableS4_tableS8.py']),
]


def main():
    for folder, args in STEPS:
        start = time.time()
        print(f'== {folder}: {" ".join(args)}', flush=True)
        subprocess.run([sys.executable, *args], cwd=ROOT / folder, check=True)
        print(f'== {folder}: done in {time.time() - start:.0f} s', flush=True)
    print('All steps finished.')


if __name__ == '__main__':
    main()
