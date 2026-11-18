# Model governance

## Intended use

This portfolio model demonstrates a reproducible response-prediction workflow on deterministic synthetic oncology-style data. It may be used to inspect engineering, validation, and explainability patterns.

## Out-of-scope use

It must not support diagnosis, prognosis, treatment selection, patient outreach, benefit decisions, or any real clinical or operational decision. It is not clinically validated or production-ready.

## Target and prediction point

The binary target is `responder`, defined as complete or partial response at a simplified synthetic patient-level assessment. Prediction occurs after diagnosis and first-treatment selection but before outcome assessment. Only demographics, diagnosis/stage, biomarker, synthetic ECOG-like status, baseline comorbidity, and first treatment class are used.

## Controls

- Leakage: outcome, survival, progression, later treatment lines, utilization, and cost are excluded.
- Missing data: median numeric and most-frequent categorical imputation are fitted inside the pipeline and cross-validation folds.
- Validation: stratified 75/25 holdout plus deterministic five-fold stratified cross-validation.
- Reproducibility: fixed generator, split, model, and explanation seeds.
- Explainability: tree SHAP when compatible; held-out permutation importance is the recorded fallback.
- Subgroups: dashboard filters support descriptive review. No fairness certification is claimed.

## Review checklist

- [ ] Confirm data are synthetic and the intended use remains educational.
- [ ] Recheck target definition and prediction-time feature availability.
- [ ] Review class prevalence, missingness, discrimination, calibration, and confusion matrix.
- [ ] Compare holdout and cross-validation metrics for instability.
- [ ] Review subgroup performance before any expanded demonstration.
- [ ] Confirm explanations are not described as causal or clinically important.
- [ ] Do not deploy or use for patient-level decisions.

