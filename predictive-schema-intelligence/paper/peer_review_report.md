# Strict peer-review report (Phase 12), with status after revision

Verdict a reviewer would likely give today: **not ready for a full journal; plausible as a workshop/short paper or preprint**, if claims stay as scoped. No acceptance is guaranteed.

| ID | Severity | Issue | Why it matters | Evidence needed | Correction / status |
|---|---|---|---|---|---|
| 1 | Critical | All data are synthetic | No evidence of real-world performance | Real schema histories replayed against real queries/tests | **Unresolved.** Scope and abstract state this; title now says "Synthetic Benchmark" |
| 2 | Critical | Near-deterministic benchmark (F1 about 0.999) | Models may only recover engine semantics | Second engine, noisy lineage parsed from real SQL, engine-aware rule baseline | **Unresolved.** Discussed in 10-11; lineage-incompleteness experiment added earlier |
| 3 | Critical | Literature search incomplete; not a systematic review | Related-work and gap claims may be wrong | Direct Scholar/Crossref/IEEE/Springer search; screening log | **Partly addressed:** protocol documented honestly, 14 entries, 5 read deeply; still informal and incomplete (no direct Scholar/Crossref/IEEE/Springer search; data contracts and observability not covered academically) |
| 4 | Major | Closest work (Su et al. 2026) overlaps in approach | Novelty limited | Full read and explicit comparison | **Addressed in text**; re-read needed |
| 5 | Major | Rule R2 written by the author with knowledge of the generator | May favour the rule on structural changes | Independent baseline design | Unresolved; stated in threats |
| 6 | Major | Lineage features come from idealised job metadata | Real lineage is noisy | Parse real SQL with a lineage tool | Unresolved; partly probed by Table 8 |
| 7 | Major | Label = any job exception; silent wrong output ignored | Misses a common failure class | Output-comparison labels | Unresolved; scoped out explicitly (Maule's error/warning distinction cited) |
| 8 | Major | One engine (DuckDB) | Engine-specific casting rules | SQLite/Postgres/Spark runs | Unresolved |
| 9 | Moderate | 15 CV evaluations are not independent; no significance tests | Spread is descriptive | Repeated independent datasets | Stated; no significance claims made |
| 10 | Moderate | Base rate (about 41%) set by sampling | Not realistic prevalence | Prevalence analysis | Table 6 added earlier |
| 11 | Moderate | 386 type changes excluded (engine rejected migration) | Selection effect | Report as rejected class | Reported in Table 1 and Limitations |
| 12 | Moderate | Calibration only by Brier score; explanation only by permutation importance | Risk-score validity | Reliability curves on real data | Table 9 added; rest unresolved |
| 13 | Moderate | RQ4 (integration) is conceptual | Cannot claim feasibility | Prototype integration | Labelled proposed; no claim |
| 14 | Minor | Reference metadata checks | Citation accuracy | Publisher pages | **Resolved** for Qiu, Kamei, Breck, Foidl, Jassas, DuckDB; LineageX proceedings entry still to check (`citation_audit.md`) |
| 15 | Minor | Code repository URL missing | Required for code availability | Author upload | Affiliation, e-mail, MIT licence and single-author statement added; repository URL still to be added after upload |

## Title validation (Phase 9)
Your original title ("... A Machine Learning Framework for Early Detection of Database Pipeline Failures ...") implies a validated framework and real failure detection. The work supports a *prototype evaluated on a synthetic benchmark*. Recommended title (applied): "Towards Predictive Schema Intelligence: Predicting Downstream SQL-Pipeline Failures from Schema Changes on an Execution-Grounded Synthetic Benchmark". Keeps your brand phrase, states the evidence type.
