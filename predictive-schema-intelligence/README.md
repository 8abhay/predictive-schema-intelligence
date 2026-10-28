# Predictive Schema Intelligence (experimental prototype)

Repository: https://github.com/8abhay/predictive-schema-intelligence

Execution-grounded synthetic benchmark + leakage-aware evaluation of whether schema-change
characteristics and static lineage predict downstream SQL-pipeline failures *before* execution.
This is a proof-of-concept study on **synthetic** data, not a production system.

## Install
```bash
python -m venv .venv && source .venv/bin/activate      # Windows: .venv\Scripts\activate
pip install -r requirements.txt
```
Tested with Python 3.12, DuckDB 2.0.0, scikit-learn 1.8.0 (see `results/run_config.json`).

## Run
```bash
python src/run_all.py                 # ~5-8 min on a laptop CPU
# or step by step (run from src/):
python build_dataset.py               # generate pipelines, execute every change in DuckDB -> data/dataset.csv
python train_eval.py                  # grouped CV, baselines, ablation, leave-one-change-type-out, prevalence
python robustness.py                  # lineage-incompleteness experiment
python make_report.py                 # results/tables.md + results/figures/*.png
python ../paper/build_manuscript.py   # paper/manuscript.md (tables inserted from results/)
python -m pytest -q tests             # 8 tests
```
Seeds/sizes: `src/config.py`. Results are deterministic given the same package versions.

## Layout
`src/schema_generator.py` pipelines + change taxonomy | `src/execute.py` DuckDB execution -> labels |
`src/features.py` pre-execution features | `src/baselines.py` rule baselines (fixed before experiments) |
`src/train_eval.py` models/CV | `src/robustness.py` | `src/make_report.py` | `paper/` manuscript, bib, literature matrix.

## Paper PDF and licence
`pip install pypandoc_binary weasyprint` then `python paper/build_pdf.py` builds `paper/manuscript.pdf` from `paper/manuscript.md`. Code is released under the MIT licence (`LICENSE`).
