# Oncology Patient Outcomes & Treatment Pathway Analytics — Stakeholder Report

> **Synthetic-data demonstration.** Every record is generated; this is not clinical decision support and contains no PHI.

## Executive overview

The analytical cohort contains **1,500 synthetic patients**, **2,421 treatment events**, a **60.1%** binary response rate, and a **48.5%** progression-event rate. These results describe constructed associations only; they do not estimate treatment effectiveness.

## Cohort snapshot

Median follow-up was **652 days**. Mean modeled cost was **$42,589** per patient. Age, cancer type, stage, region, race/ethnicity, performance status, biomarkers, comorbidities, and treatment class are available for stratified exploration.

## Treatment pathways

The five most frequent ordered treatment-class pathways were:

- Surgery: 258 patients
- Chemotherapy: 198 patients
- Radiation: 123 patients
- Targeted therapy: 119 patients
- Immunotherapy: 65 patients

## Outcomes and statistical associations

- Stage I: 274 patients; response 79.9%; progression 20.4%.
- Stage II: 448 patients; response 67.0%; progression 40.4%.
- Stage III: 449 patients; response 55.0%; progression 55.7%.
- Stage IV: 329 patients; response 41.0%; progression 72.9%.

The stage–response chi-square association test yielded p=2.41e-23. This is an association in synthetic observational-style data, not a causal comparison.

## Survival

- Overall: 827/1,500 events; median survival 919 days.
- Stage I: 83/274 events; median survival 1,839 days.
- Stage II: 191/448 events; median survival 1,402 days.
- Stage III: 290/449 events; median survival 754 days.
- Stage IV: 263/329 events; median survival 405 days.

The Cox model reports adjusted hazard-ratio associations. The largest modeled coefficient magnitudes were stage (HR 1.72), ecog_status (HR 1.30), comorbidity_count (HR 1.24). Proportional-hazards diagnostics are provided separately.

## Predictive modeling

On the held-out test set, the random forest achieved ROC-AUC **0.669**, PR-AUC **0.719**, precision **0.695**, recall **0.760**, and F1 **0.726**. Five-fold training-set cross-validation and calibration outputs are included. Performance on synthetic data does not establish clinical utility or transportability.

## Data quality

Automated validation passed **18/18** rules; critical failures: **0**. Missing biomarker and ECOG values are intentional and handled through model-pipeline imputation.

## Limitations

- Fully synthetic data; constructed dependencies are not clinical truth.
- Observational-style analyses are subject to confounding, selection bias, and measurement limitations.
- Response is a simplified patient-level endpoint and is not a validated oncology endpoint.
- Treatment classes and costs are generalized; sequencing does not encode dose, adherence, or clinical rationale.
- Missingness is simulated and may not resemble operational data.
- No causal inference, clinical validation, fairness certification, or treatment recommendation is intended.
