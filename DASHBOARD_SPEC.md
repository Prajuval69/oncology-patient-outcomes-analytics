# Dashboard Specification

Build a Streamlit application.

## Pages/sections
### Overview
KPIs:
- patients
- diagnoses
- treatment events
- response rate
- progression/event rate
- median follow-up
- utilization measures

### Cohort
Demographic and disease distributions.

### Treatment Pathways
Treatment line, modality/class, sequence, and duration summaries.

### Outcomes
Response and progression summaries.

### Survival
Interactive Kaplan–Meier visualizations and subgroup filters.

### Predictive Modeling
Model metrics and confusion matrix/ROC/PR visuals.

### Explainability
Feature importance and SHAP-style visualizations.

### Data Quality
Missingness, duplicate checks, invalid dates, and validation results.

Use cached loading for stable data and keep dashboard startup reliable.
