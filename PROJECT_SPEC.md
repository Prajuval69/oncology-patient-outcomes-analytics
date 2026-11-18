# Project Specification

## Project name
Oncology Patient Outcomes & Treatment Pathway Analytics Platform

## Business context
An oncology analytics team wants an integrated view of patient characteristics, disease stage, treatment pathways, response, survival, comorbidities, and healthcare utilization.

## Data entities
Design a relational model containing at least:
- patients
- diagnoses
- treatments
- treatment_events
- outcomes
- comorbidities
- utilization

Recommended keys:
- patient_id
- diagnosis_id
- treatment_event_id
- outcome_id
- comorbidity_id
- utilization_id

## Synthetic data
Generate a realistic but clearly synthetic cohort. Include:
- age
- sex
- geography/region
- cancer type
- diagnosis date
- stage
- biomarker/status fields where appropriate
- comorbidity indicators
- ECOG-like performance category if used, explicitly labeled synthetic
- treatment line
- treatment modality/class
- treatment start/end dates
- response category
- progression/event indicator
- survival/follow-up time
- hospitalization/visit/utilization measures
- cost/utilization fields where appropriate

Use plausible dependencies while avoiding claims that synthetic relationships represent clinical truth.

## SQL layer
Implement reusable SQL for:
- cohort inclusion
- baseline characteristics
- treatment sequencing
- treatment-line summaries
- response summaries
- survival-analysis input
- utilization summaries
- KPI tables

## Statistical layer
Include:
- counts and percentages
- mean/median/IQR
- missingness
- group comparisons where appropriate
- confidence intervals where appropriate
- Kaplan–Meier analysis
- log-rank comparison where appropriate
- Cox proportional-hazards model
- logistic regression for a binary outcome

## ML layer
Build at least one predictive model for a clearly defined outcome such as response/non-response. Compare a simple baseline against a tree-based model when justified.

Include:
- train/test split
- cross-validation
- ROC-AUC
- PR-AUC
- confusion matrix
- precision/recall
- calibration assessment where feasible
- feature importance
- SHAP explanations when package compatibility allows

Avoid leakage: features must be available at the prediction time.

## Dashboard
Streamlit dashboard should contain:
1. Overview
2. Cohort demographics
3. Disease/stage distribution
4. Treatment pathways
5. Response analysis
6. Survival analysis
7. Predictive model performance
8. Explainability
9. Data quality

Add filters for meaningful cohort dimensions.

## Reporting
Generate:
- KPI CSV
- summary tables
- key charts
- model metrics
- survival results
- a concise stakeholder report in Markdown or HTML
- data dictionary

## Limitations
Explicitly document:
- synthetic data
- observational nature
- selection bias
- confounding
- missing data
- measurement limitations
- no causal inference
- no clinical validation
- no real patient use
