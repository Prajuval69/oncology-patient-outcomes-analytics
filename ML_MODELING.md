# Machine Learning Specification

Build a reproducible predictive workflow.

Recommended target:
- binary response/non-response at a clearly defined prediction point.

Requirements:
- leakage review
- preprocessing pipeline
- missing-value handling
- categorical encoding
- baseline model
- tree-based model where appropriate
- cross-validation
- held-out test set
- ROC-AUC
- PR-AUC
- precision
- recall
- F1
- confusion matrix
- calibration where feasible
- feature importance
- SHAP explanations or a documented compatible fallback

Save model metrics in machine-readable form.

Do not claim clinical utility or production readiness.
