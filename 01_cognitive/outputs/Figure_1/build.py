"""Regenerate Figure 1 from public data and documented manuscript flow counts."""
import sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[2]/'code'))
from figure1 import main
main()
