"""Regenerate this output from the public data directory."""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[2] / 'code'))
from exp2 import main
main()
