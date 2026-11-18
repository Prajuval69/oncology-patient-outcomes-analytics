# Architecture and lineage

```text
deterministic generator
  -> raw CSVs (7 relational entities)
  -> validation results + missingness profile
  -> constrained SQLite database
  -> modular SQL analytical marts
  -> descriptive/statistical + KM/Cox analyses
  -> logistic baseline + random forest + explanations
  -> charts + stakeholder report + Streamlit dashboard
```

The pipeline fails before database creation if any required validation rule fails. SQL marts have explicit grain comments and are persisted both in SQLite (`mart_*`) and CSV for inspectability. `artifacts/run_manifest.json` inventories the successful run.

