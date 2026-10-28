<!-- dataset -->
| change_type | executed | failure_rate | migration_rejected |
|---|---|---|---|
| type_change | 4239 | 0.136 | 386 |
| drop_column | 1875 | 0.811 | 0 |
| rename_column | 1846 | 0.593 | 0 |
| nullability_relax | 760 | 0.568 | 0 |
| add_column | 622 | 0.492 | 0 |
| nullability_tighten | 272 | 0.000 | 0 |

<!-- main -->
| Method | Features | Precision | Recall | F1 | PR-AUC | ROC-AUC | FPR | FNR |
|---|---|---|---|---|---|---|---|---|
| Always-fail | - | 0.409 ± 0.018 | 1.000 ± 0.000 | 0.580 ± 0.018 | - | - | 1.000 ± 0.000 | 0.000 ± 0.000 |
| Rule R1 (schema-only) | - | 0.460 ± 0.015 | 0.813 ± 0.018 | 0.587 ± 0.012 | - | - | 0.659 ± 0.011 | 0.187 ± 0.018 |
| Rule R2 (lineage-aware) | - | 0.662 ± 0.013 | 1.000 ± 0.000 | 0.797 ± 0.009 | - | - | 0.353 ± 0.020 | 0.000 ± 0.000 |
| Logistic Regression | S | 0.685 ± 0.029 | 0.757 ± 0.020 | 0.719 ± 0.017 | 0.763 ± 0.023 | 0.852 ± 0.009 | 0.240 ± 0.019 | 0.243 ± 0.020 |
| Logistic Regression | S+D | 0.938 ± 0.011 | 0.882 ± 0.014 | 0.909 ± 0.009 | 0.949 ± 0.008 | 0.972 ± 0.003 | 0.040 ± 0.006 | 0.118 ± 0.014 |
| Logistic Regression | S+D+P | 0.938 ± 0.011 | 0.882 ± 0.014 | 0.909 ± 0.009 | 0.949 ± 0.008 | 0.972 ± 0.003 | 0.040 ± 0.006 | 0.118 ± 0.014 |
| Decision Tree | S | 0.659 ± 0.026 | 0.759 ± 0.027 | 0.705 ± 0.014 | 0.713 ± 0.024 | 0.829 ± 0.010 | 0.271 ± 0.022 | 0.241 ± 0.027 |
| Decision Tree | S+D | 0.998 ± 0.002 | 0.999 ± 0.002 | 0.999 ± 0.001 | 0.999 ± 0.001 | 1.000 ± 0.001 | 0.001 ± 0.001 | 0.001 ± 0.002 |
| Decision Tree | S+D+P | 1.000 ± 0.000 | 1.000 ± 0.000 | 1.000 ± 0.000 | 1.000 ± 0.000 | 1.000 ± 0.000 | 0.000 ± 0.000 | 0.000 ± 0.000 |
| Random Forest | S | 0.666 ± 0.029 | 0.697 ± 0.023 | 0.680 ± 0.015 | 0.715 ± 0.030 | 0.827 ± 0.010 | 0.242 ± 0.023 | 0.303 ± 0.023 |
| Random Forest | S+D | 1.000 ± 0.000 | 0.997 ± 0.002 | 0.999 ± 0.001 | 1.000 ± 0.000 | 1.000 ± 0.000 | 0.000 ± 0.000 | 0.003 ± 0.002 |
| Random Forest | S+D+P | 1.000 ± 0.000 | 0.998 ± 0.002 | 0.999 ± 0.001 | 1.000 ± 0.000 | 1.000 ± 0.000 | 0.000 ± 0.000 | 0.002 ± 0.002 |
| Gradient Boosting | S | 0.673 ± 0.028 | 0.739 ± 0.027 | 0.703 ± 0.012 | 0.740 ± 0.020 | 0.842 ± 0.009 | 0.249 ± 0.024 | 0.261 ± 0.027 |
| Gradient Boosting | S+D | 0.999 ± 0.001 | 0.998 ± 0.002 | 0.999 ± 0.001 | 1.000 ± 0.000 | 1.000 ± 0.000 | 0.000 ± 0.001 | 0.002 ± 0.002 |
| Gradient Boosting | S+D+P | 1.000 ± 0.000 | 0.999 ± 0.002 | 0.999 ± 0.001 | 1.000 ± 0.000 | 1.000 ± 0.000 | 0.000 ± 0.000 | 0.001 ± 0.002 |

<!-- pooled -->
| Method | TN | FP | FN | TP | Precision | Recall | F1 |
|---|---|---|---|---|---|---|---|
| Rule R1 (schema-only) | 1940 | 3745 | 738 | 3191 | 0.460 | 0.812 | 0.587 |
| Rule R2 (lineage-aware) | 3683 | 2002 | 0 | 3929 | 0.662 | 1.000 | 0.797 |
| Random Forest (S) | 4283 | 1402 | 1179 | 2750 | 0.662 | 0.700 | 0.681 |
| Random Forest (S+D) | 5684 | 1 | 10 | 3919 | 1.000 | 0.997 | 0.999 |
| Random Forest (S+D+P) | 5685 | 0 | 10 | 3919 | 1.000 | 0.997 | 0.999 |

<!-- typechange -->
| Method | n | failures | TN | FP | FN | TP | Precision | Recall | F1 |
|---|---|---|---|---|---|---|---|---|---|
| Rule R1 (schema-only) | 4239 | 577 | 1024 | 2638 | 0 | 577 | 0.179 | 1.000 | 0.304 |
| Rule R2 (lineage-aware) | 4239 | 577 | 1660 | 2002 | 0 | 577 | 0.224 | 1.000 | 0.366 |
| Random Forest (S) | 4239 | 577 | 3451 | 211 | 482 | 95 | 0.310 | 0.165 | 0.215 |
| Random Forest (S+D) | 4239 | 577 | 3661 | 1 | 10 | 567 | 0.998 | 0.983 | 0.990 |
| Random Forest (S+D+P) | 4239 | 577 | 3662 | 0 | 10 | 567 | 1.000 | 0.983 | 0.991 |

<!-- locto -->
| held_out | Decision Tree | Logistic Regression | Random Forest | Rule R2 (lineage-aware) | failures | n |
|---|---|---|---|---|---|---|
| add_column | 1.0 | 0.0 | 0.0 | 1.0 | 306 | 622 |
| drop_column | 0.042 | 0.469 | 0.603 | 1.0 | 1520 | 1875 |
| nullability_relax | 0.811 | 0.528 | 0.632 | 1.0 | 432 | 760 |
| nullability_tighten | 0.0 | 0.0 | 0.0 | 0.0 | 0 | 272 |
| rename_column | 0.425 | 0.69 | 0.547 | 1.0 | 1094 | 1846 |
| type_change | 0.243 | 0.293 | 0.272 | 0.366 | 577 | 4239 |

<!-- prevalence -->
| prevalence | model | precision | recall | f1 | pr_auc |
|---|---|---|---|---|---|
| 0.05 | Random Forest S | 0.129 | 0.698 | 0.218 | 0.169 |
| 0.05 | Random Forest S+D+P | 1.0 | 0.997 | 0.998 | 1.0 |
| 0.05 | Rule R1 (schema-only) | 0.062 | 0.823 | 0.115 | nan |
| 0.05 | Rule R2 (lineage-aware) | 0.13 | 1.0 | 0.23 | nan |
| 0.1 | Random Forest S | 0.241 | 0.704 | 0.359 | 0.296 |
| 0.1 | Random Forest S+D+P | 1.0 | 0.997 | 0.998 | 1.0 |
| 0.1 | Rule R1 (schema-only) | 0.121 | 0.816 | 0.211 | nan |
| 0.1 | Rule R2 (lineage-aware) | 0.24 | 1.0 | 0.387 | nan |
| 0.2 | Random Forest S | 0.414 | 0.698 | 0.52 | 0.479 |
| 0.2 | Random Forest S+D+P | 1.0 | 0.998 | 0.999 | 1.0 |
| 0.2 | Rule R1 (schema-only) | 0.235 | 0.811 | 0.365 | nan |
| 0.2 | Rule R2 (lineage-aware) | 0.415 | 1.0 | 0.587 | nan |
| natural | Random Forest S | 0.662 | 0.7 | 0.681 | 0.712 |
| natural | Random Forest S+D+P | 1.0 | 0.997 | 0.999 | 1.0 |
| natural | Rule R1 (schema-only) | 0.46 | 0.812 | 0.587 | nan |
| natural | Rule R2 (lineage-aware) | 0.662 | 1.0 | 0.797 | nan |

<!-- robust -->
| Hidden-job prob. q | Method | Precision | Recall | F1 | PR-AUC |
|---|---|---|---|---|---|
| 0.0 | Decision Tree | 0.998 ± 0.002 | 0.999 ± 0.002 | 0.999 ± 0.001 | 0.999 ± 0.001 |
| 0.0 | Logistic Regression | 0.938 ± 0.011 | 0.882 ± 0.014 | 0.909 ± 0.009 | 0.949 ± 0.008 |
| 0.0 | Random Forest | 1.000 ± 0.000 | 0.997 ± 0.002 | 0.999 ± 0.001 | 1.000 ± 0.000 |
| 0.0 | Rule R1 (schema-only) | 0.460 ± 0.015 | 0.813 ± 0.018 | 0.587 ± 0.012 | - |
| 0.0 | Rule R2 (lineage-aware) | 0.662 ± 0.013 | 1.000 ± 0.000 | 0.797 ± 0.009 | - |
| 0.25 | Decision Tree | 0.943 ± 0.013 | 0.850 ± 0.016 | 0.894 ± 0.009 | 0.955 ± 0.006 |
| 0.25 | Logistic Regression | 0.820 ± 0.020 | 0.852 ± 0.013 | 0.836 ± 0.011 | 0.919 ± 0.011 |
| 0.25 | Random Forest | 0.963 ± 0.011 | 0.845 ± 0.020 | 0.900 ± 0.009 | 0.964 ± 0.004 |
| 0.25 | Rule R1 (schema-only) | 0.460 ± 0.015 | 0.813 ± 0.018 | 0.587 ± 0.012 | - |
| 0.25 | Rule R2 (lineage-aware) | 0.666 ± 0.011 | 0.843 ± 0.022 | 0.744 ± 0.011 | - |
| 0.5 | Decision Tree | 0.850 ± 0.018 | 0.740 ± 0.030 | 0.791 ± 0.017 | 0.902 ± 0.012 |
| 0.5 | Logistic Regression | 0.798 ± 0.020 | 0.789 ± 0.016 | 0.793 ± 0.014 | 0.880 ± 0.015 |
| 0.5 | Random Forest | 0.835 ± 0.024 | 0.759 ± 0.023 | 0.795 ± 0.015 | 0.916 ± 0.009 |
| 0.5 | Rule R1 (schema-only) | 0.460 ± 0.015 | 0.813 ± 0.018 | 0.587 ± 0.012 | - |
| 0.5 | Rule R2 (lineage-aware) | 0.671 ± 0.015 | 0.616 ± 0.030 | 0.642 ± 0.018 | - |
| 0.75 | Decision Tree | 0.746 ± 0.032 | 0.703 ± 0.030 | 0.723 ± 0.010 | 0.836 ± 0.011 |
| 0.75 | Logistic Regression | 0.732 ± 0.028 | 0.752 ± 0.022 | 0.741 ± 0.012 | 0.835 ± 0.013 |
| 0.75 | Random Forest | 0.736 ± 0.024 | 0.718 ± 0.023 | 0.726 ± 0.005 | 0.844 ± 0.010 |
| 0.75 | Rule R1 (schema-only) | 0.460 ± 0.015 | 0.813 ± 0.018 | 0.587 ± 0.012 | - |
| 0.75 | Rule R2 (lineage-aware) | 0.674 ± 0.023 | 0.356 ± 0.039 | 0.464 ± 0.033 | - |

<!-- importance -->
| feature | perm_importance_pr_auc |
|---|---|
| d_n_positional | 0.0645 |
| s_change_drop_column | 0.0044 |
| d_role_string_fn | 0.0043 |
| d_n_affected | 0.0030 |
| d_role_filter | 0.0028 |
| d_role_measure | 0.0017 |
| d_role_date_fn | 0.0017 |
| d_n_direct | 0.0015 |
| s_change_nullability_tighten | 0.0010 |
| d_role_notnull_target | 0.0005 |

<!-- calibration -->
| Predictor | Brier score |
|---|---|
| Constant prevalence (reference) | 0.2417 |
| Logistic Regression (S+D) | 0.0590 |
| Decision Tree (S+D) | 0.0010 |
| Random Forest (S) | 0.1713 |
| Random Forest (S+D+P) | 0.0053 |
| Gradient Boosting (S+D+P) | 0.0003 |