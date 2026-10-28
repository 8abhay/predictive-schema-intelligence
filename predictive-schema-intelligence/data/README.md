# Data

`dataset.csv` (generated, not downloaded) is a **fully synthetic, execution-grounded benchmark**.
No production or real enterprise data is used. Regenerate with `python src/build_dataset.py`
(seed 42; SHA-256 fingerprint of the generated pipelines is stored in `dataset_meta.json`).

* One row = one proposed schema change applied to one synthetic pipeline.
* `failed` = 1 if at least one downstream SQL job raised an exception when run in DuckDB after the change.
* Columns starting with `s_` (schema-change), `d_` (static lineage) and `p_` (pre-change data profile) are model inputs.
* `failed`, `n_failed_jobs`, `first_error_type`, `first_error_msg`, `status` are **post-execution outcomes**; they are never features.
* 386 proposed type changes were rejected by the database engine at migration time and are excluded (see `dataset_meta.json`).
* No real-world public dataset of schema-change/pipeline-failure outcomes was located during the literature search; this is a limitation.
