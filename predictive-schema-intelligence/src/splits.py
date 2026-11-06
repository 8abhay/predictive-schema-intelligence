"""Group-based CV splits: all rows of a pipeline land in exactly one fold."""
import numpy as np


def group_folds(groups, n_splits, seed):
    groups = np.asarray(groups)
    uniq = np.unique(groups)
    rng = np.random.default_rng(seed)
    perm = rng.permutation(uniq)
    fold_of = {g: i % n_splits for i, g in enumerate(perm)}
    return np.array([fold_of[g] for g in groups])
