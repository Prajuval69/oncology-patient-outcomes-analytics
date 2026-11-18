# Oncology Patient Outcomes & Treatment Pathway Analytics Platform

A complete, reproducible healthcare analytics portfolio project built entirely from deterministic **synthetic** oncology-style data. It integrates relational modeling, SQL cohorting, data quality, biostatistics, survival analysis, predictive modeling, explainability, reporting, and an interactive Streamlit dashboard.

> This is an analytics demonstration—not clinical decision support. It contains no real patient records or PHI, makes no causal treatment-effect claims, and is not clinically validated.

## Business problem

The platform gives an oncology analytics stakeholder a unified view of cohort composition, disease stage, comorbidity, treatment sequences, response, progression, time-to-event outcomes, utilization, modeled costs, predictive performance, and data quality.

## Workflow

`Synthetic generator → raw CSVs → validation → SQLite → SQL marts → statistics/survival → ML/explainability → charts/report/dashboard`

See [architecture](docs/ARCHITECTURE.md) and the full [data dictionary](docs/DATA_DICTIONARY.md).

## Data model

Seven normalized source tables are implemented: `patients`, `diagnoses`, `treatments`, `treatment_events`, `outcomes`, `comorbidities`, and `utilization`. Foreign keys and check constraints are enforced in SQLite. Reusable SQL builds cohort, baseline, stage, treatment-line, pathway, response, survival, utilization, KPI, and quality marts.

## Technology

Python 3.11+, pandas, NumPy, SciPy, statsmodels, scikit-learn, lifelines, SHAP (with permutation fallback), SQLite, Plotly, Matplotlib/Seaborn, Streamlit, and pytest.

## Setup and run

PowerShell:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
$env:PYTHONPATH = "src"
python -m oncology_platform.pipeline
python -m pytest
streamlit run dashboard/app.py
```

macOS/Linux:

```bash
python -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
PYTHONPATH=src python -m oncology_platform.pipeline
PYTHONPATH=src python -m pytest
streamlit run dashboard/app.py
```

Regenerate with a different deterministic configuration:

```powershell
$env:PYTHONPATH = "src"
python -m oncology_platform.pipeline --patients 2000 --seed 12345
```

## Analytical methodology

- Counts, percentages, mean/median/IQR, missingness, stage-stratified outcomes, chi-square, and Mann–Whitney comparisons.
- Kaplan–Meier overall and stage curves with confidence intervals, number-at-risk tables, median survival, and stage log-rank test.
- Penalized multivariable Cox model with hazard ratios, confidence intervals, concordance, and proportional-hazards tests.
- Statsmodels logistic association model with odds ratios and confidence intervals.
- Prediction target: simplified binary response after diagnosis and first-treatment selection. A regularized logistic baseline and random forest share leakage-controlled preprocessing, a stratified holdout, and five-fold training-set CV.
- ROC-AUC, PR-AUC, precision, recall, F1, confusion matrix, calibration, impurity importance, and TreeSHAP/permutation explainability.

Associations are descriptive or adjusted statistical associations—not causal effects.

## Dashboard

The Streamlit app provides Overview, Cohort, Treatment Pathways, Outcomes, Survival, Predictive Modeling, Explainability, and Data Quality sections. Cancer, stage, sex, and region filters share a consistent cohort scope; data loading is cached.

## Outputs

- `data/raw/`: seven generated source CSVs
- `data/oncology.db`: source tables plus analytical marts
- `data/processed/`: cohort/mart CSVs, statistical results, survival results, model metrics, predictions, calibration, and validation evidence
- `artifacts/charts/`: stakeholder-ready PNG charts
- `artifacts/models/`: serialized sklearn pipelines (generated locally; gitignored)
- `artifacts/run_manifest.json`: run inventory and verification metadata
- `reports/stakeholder_report.md`: concise decision-oriented narrative
- `docs/`: architecture, data dictionary, and model governance

## Tests

`pytest` covers deterministic generation, empty input rejection, key/date/line integrity, missing optional values, deliberately duplicated/invalid rows, SQLite and SQL marts, KPI/cohort reconciliation, all-censored and empty survival subsets, preprocessing, metrics, and dashboard import/filter behavior.

## Limitations

Synthetic relationships do not represent clinical truth. The project simplifies staging, treatment, response, follow-up, comorbidity, utilization, and cost. Observational-style comparisons remain vulnerable to confounding, selection bias, missing data, measurement error, and model misspecification. There is no external validation, clinical validation, production hardening, prospective evaluation, causal inference, or individual treatment recommendation.

## Project structure

```text
dashboard/                 Streamlit application
data/raw/                  deterministic synthetic source data
data/processed/            SQL and analytical outputs
docs/                      architecture, dictionary, governance
artifacts/charts/          rendered figures
artifacts/models/          trained pipelines
reports/                   stakeholder report
sql/                       schema and reusable marts
src/oncology_platform/     generation, validation, analytics, modeling, reporting
tests/                     deterministic pytest suite
```

