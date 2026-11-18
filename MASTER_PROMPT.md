# MASTER PROMPT — Oncology Patient Outcomes & Treatment Pathway Analytics Platform

Build the complete **Oncology Patient Outcomes & Treatment Pathway Analytics Platform** from start to finish.

## Objective
Create a portfolio-grade, reproducible healthcare analytics project using synthetic/public-safe oncology-style data. The project must demonstrate SQL, Python, statistics, epidemiology/biostatistics concepts, machine learning, explainability, visualization, dashboarding, testing, documentation, and stakeholder-oriented interpretation.

## Core requirements
1. Inspect the workspace before changing anything.
2. Read this file and every supporting `.md` file in the workspace.
3. Implement the complete project rather than scaffolding.
4. Use synthetic data unless a public dataset is already available and clearly licensed for use.
5. Do not use real patient data or protected health information.
6. Make the workflow reproducible with deterministic seeds.
7. Build:
   - synthetic oncology data generation
   - relational data model
   - SQLite database
   - SQL cohort construction and analytical marts
   - data-quality validation
   - descriptive statistics
   - treatment-line/pathway analysis
   - Kaplan–Meier survival analysis
   - logistic regression
   - Cox proportional-hazards model where technically supported
   - model diagnostics and validation
   - feature importance and SHAP-style explainability where feasible
   - Streamlit dashboard
   - stakeholder-ready reporting outputs
   - automated tests
   - documentation
8. Include clear clinical/analytical limitations. This is an analytics demonstration, not a clinical decision-support system.
9. Never imply causal treatment effectiveness from observational/synthetic analyses.
10. Prefer interpretable, well-tested implementations over unnecessary complexity.

## Suggested stack
Python 3.11+, pandas, NumPy, SciPy, statsmodels, scikit-learn, lifelines, matplotlib, seaborn only if useful, Plotly, Streamlit, SQLAlchemy/SQLite, pytest, SHAP where compatible.

## Required analytical questions
- Who is in the oncology cohort?
- How do demographics, stage, tumor type, comorbidities, and treatment lines differ?
- What are treatment-pathway patterns?
- How does time-to-event differ across selected descriptive groups?
- Which variables are associated with response?
- Which variables are associated with survival in a multivariable model?
- Which features drive predictive model output?
- What data-quality issues and missingness patterns exist?
- What KPIs would an oncology analytics stakeholder monitor?

## Required outputs
Create a clean repository with:
- source code
- SQL scripts
- synthetic input data or deterministic generator
- generated analytical datasets
- model artifacts where appropriate
- charts
- dashboard
- tests
- documentation
- reproducible run instructions
- requirements file
- `.gitignore`

Do not leave temporary files, caches, virtual environments, notebook checkpoints, or unnecessary documentation.

## Quality gate
Before declaring completion:
- run the complete pipeline
- run all tests
- fix failures
- verify generated files
- verify dashboard startup/importability
- verify SQL queries against the database
- verify survival/model outputs are numerically valid
- verify no real PHI is included
- ensure README accurately reflects what was actually implemented
- clean unnecessary files
- provide a concise final implementation summary with tests and key outputs.
