# Literature search protocol (Phase 3) - honest record

**This was a structured but informal search, not a systematic review. No PRISMA flow is reported because screening counts were not recorded.**

- **Search dates:** 23-28 Oct 2026.
- **Engines actually used:** general web search with scholarly sources returned (arXiv, publisher and DBLP pages, ACM, MDPI, VLDB, university repositories), plus direct fetches of paper PDFs/pages. Google Scholar, Semantic Scholar, Crossref, IEEE Xplore and SpringerLink were **not** queried directly.
- **Queries (representative):** schema evolution data pipeline failure prediction machine learning; schema evolution impact analysis breaking changes; data pipeline quality failures root causes; data validation for machine learning; predicting data pipeline job failures ETL Airflow; predicting breaking schema changes downstream consumers; data contracts producer consumer; Wikipedia schema evolution; just-in-time quality assurance; ACM open access APC; DuckDB SIGMOD 2019; SchemaPile; column-level data lineage extraction impact analysis SQL.
- **Inclusion:** peer-reviewed or clearly identified preprints on schema evolution/impact, data validation or quality, pipeline failures, failure/defect prediction; metadata verifiable from the publisher, arXiv, an index page or the paper itself.
- **Exclusion:** blogs, vendor material, patents, theses (kept only as grey-literature signals); items whose metadata could not be verified.
- **Duplicates / screening:** manual; counts not recorded.
- **Outcome:** 14 entries (see `literature_matrix.md`); full text read for Qiu, Schelter, Maule and Jassas (the last pasted by the author), substantial text for Su, the rest abstract or metadata level.
- **Known limitations:** small corpus; no direct Scholar/Crossref/IEEE/Springer search; data contracts, lineage and observability covered only by grey literature; no dataset search beyond web queries (no public schema-change + failure-label dataset located; **not proven absent**).
- **Dataset check (Phase 5):** no verified public dataset with schema-change history and failure labels was located; SchemaPile (verified; 221,171 schemas, no execution outcomes per its abstract) is the largest public schema corpus found. Route chosen: Option B (clearly labelled synthetic, execution-grounded).
