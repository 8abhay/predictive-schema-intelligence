"""Central experiment configuration (all seeds and sizes live here)."""
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DATA_DIR = ROOT / "data"
RESULTS_DIR = ROOT / "results"

GLOBAL_SEED = 42           # seed for pipeline + change generation
N_PIPELINES = 500          # synthetic pipelines generated
N_ROWS = 150               # rows per source table
CHANGES_PER_PIPELINE = 20  # schema changes sampled per pipeline
POST_CHANGE_BATCH = 20     # rows of "new upstream data" appended after a nullability relaxation

CV_FOLDS = 5
CV_SEEDS = (42, 43, 44)    # 3 repetitions of grouped 5-fold CV
PREVALENCE_SEEDS = 10
