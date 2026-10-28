# Novelty assessment table (Phase 1)

| Existing research area | What is already known | What remains insufficiently addressed | Evidence supporting the gap | Proposed contribution | Overlap risk |
|---|---|---|---|---|---|
| Schema evolution studies | Schemas change often; add column/table/datatype change are frequent (Qiu 2013, Curino 2008) | Whether a given change breaks a given pipeline | Those studies measure code co-change, not execution failure | Execution-labelled benchmark of change outcomes | Low |
| Schema change impact analysis | Static dataflow analysis predicts impacted code with no false negatives in one case study (Maule 2008) | Learning-based, pipeline-level prediction; SQL jobs | Static, rule-based, application code | ML vs rule comparison on SQL jobs | Medium |
| Data validation / quality tooling | Schema-based validation and declarative checks on arriving data (Breck 2019, Schelter 2018) | Pre-execution warning about a proposed schema change | They check data, not change proposals | Pre-execution prediction protocol | Medium |
| Pipeline quality | Taxonomy of influencing factors; incorrect data types a major root cause (Foidl 2023/24) | Prediction | Descriptive study | Motivates type-change focus | Low |
| Failure prediction (cloud jobs, JIT defects) | Classical ML predicts job failure and risky code changes (Jassas 2022, Kamei 2013) | Schema-change features and SQL pipelines | Different features and domains | Feature set and benchmark for schema changes | Low |
| Execution-labelled breakage prediction | Learning from executed changes beats pure dependency reachability in software systems (Su 2026 preprint) | SQL pipelines, column-level schema changes, lightweight models | Different setting and taxonomy | Transfer to SQL pipelines + open benchmark | **High (closest work)** |
| Column-level lineage / impact analysis | LineageX extracts column lineage from SQL statically and demonstrates impact analysis (Zhang 2025, demo) | Predicting whether an upstream change will actually fail downstream | Demo; no prediction | Could supply real lineage features in future work | Low |
| Data contracts, observability | Mostly practitioner and grey literature found | Not assessed academically yet | Search incomplete | None claimed | Unknown |

**Conclusion:** a narrow, defensible gap exists *only as far as the sources checked show*. It is a transfer-and-benchmark contribution, not a new idea. Not claimed: "first", "novel framework", "state of the art".
