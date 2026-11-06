# Reading notes: Maule, Jassas, Su (6-point format)

Reading depth is stated per paper. Re-read each before submission.

## Maule, Emmerich, Rosenblum (2008) - FULL TEXT READ
1. **Citation:** Impact analysis of database schema changes. ICSE'08, May 10-18 2008, Leipzig. pp. 451-460. DOI 10.1145/1368088.1368150.
2. **Problem:** Predict which application locations are affected when a relational schema changes; manual estimation by experts is fragile.
3. **Method:** Static analysis: program slicing to shrink the program, k-CFA dataflow analysis to recover the queries an application may run, then impact calculation with relational programs (CrocoPat). Prototype tool SUITE (C#, SQL Server).
4. **Data:** Case study of a commercial CMS (irPublish): 62 schema versions over two years; three versions with the biggest changes analysed; the version shown has about 78K lines of C#, 88 tables, 536 columns, 476 stored procedures.
5. **Main result:** No false negatives and a low level of false positives (per abstract); errors were predicted more accurately than warnings; analysis took about 1 min 39 s on average; context sensitivity k=2 was the minimum needed in the case study.
6. **Limitations / difference from this work:** Single case study and prototype maturity issues (authors' own threats); C# + SQL Server only; rule/static analysis with no learning; target is application code, not data pipelines. Useful idea: the paper separates *errors* from *warnings* (changes that run but may behave differently), which supports our scoping decision to label only exceptions and to list silent semantic changes as an exclusion.

## Jassas and Mahmoud (2022) - FULL TEXT READ (pasted by the author)
1. **Citation:** Analysis of job failure and prediction model for cloud computing using machine learning. Sensors 22(5):2035, 5 March 2022, DOI 10.3390/s22052035. Ontario Tech University. Open access (CC BY).
2. **Problem:** Characterize failed vs finished cloud jobs/tasks and predict failure before execution, to reduce wasted resources.
3. **Method:** Failure analysis of three public traces, then seven classifiers (Decision Tree, Random Forest, KNN, QDA, Gradient Boosting, XGBoost, Naive Bayes) with a 75%/25% train/test split and three feature-selection methods (SelectKBest, feature importance, RFE); metrics: accuracy, precision, recall, F1, ROC/AUC. Implemented with scikit-learn.
4. **Data:** Google cluster trace (29 days, 672,074 jobs, over 28 million tasks), LANL Mustang (about 2.1 million jobs, 2011-2016) and LANL Trinity (25,237 jobs; 20,277 observations used).
5. **Main result:** Decision Tree and Random Forest were best. Google 29-day trace: precision/recall/F1 98%/95%/97%, rising to 99% each with RFE feature selection. Mustang: RF 95/94/95 (DT 94/94/94). Trinity: RF 89/88/89 and DT 88/89/89, up to 90/88/90 with feature importance + RF. DT trained much faster than RF (53.8 s vs 247.6 s on the 29-day Google trace). They selected RF as the model that generalized best. Failures correlated with requested resources, priority and scheduling class.
6. **Limitations / difference from this work:** Resource/scheduling features, not schema changes; offline training; small Mustang/Trinity samples (authors' own note). **Our own reading (not the authors' claim):** the reported top features for the Google trace included identifier-like fields (job ID, task index, machine ID), and the evaluation is a single 75/25 split; with such features a random split can inflate scores. Our study avoids this by excluding identifiers and splitting by pipeline.

## Su et al. (2026), arXiv:2610.04940 - SUBSTANTIAL TEXT READ EARLIER IN THIS WORK; re-read before citing numbers
1. **Citation:** Software world models: from consequence prediction to decision value. Preprint, 2026.
2. **Problem:** Predict which downstream components a change will break before executing it.
3. **Method:** Learn from consequences observed by executing changes in controlled worlds; compare with a typed-reachability (dependency-graph) baseline; fine-tuned language models.
4. **Data:** Synthetic worlds plus real software projects (see the paper for details).
5. **Main result (as summarized in our matrix):** Learned prediction beats pure reachability, especially where the extracted dependency graph is incomplete.
6. **Limitations / difference:** Different setting (code/services), model family and change taxonomy; preprint, not peer reviewed to our knowledge. **Closest approach found: this limits novelty claims.**
