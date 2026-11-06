"""Reproduce everything: dataset -> models -> robustness -> tables/figures -> manuscript."""
import subprocess, sys
from pathlib import Path

SRC = Path(__file__).resolve().parent
for step in ["build_dataset.py", "train_eval.py", "robustness.py", "make_report.py", "make_architecture_fig.py", "../paper/build_manuscript.py"]:
    print("==>", step, flush=True)
    subprocess.run([sys.executable, str(SRC / step)], check=True, cwd=SRC)
