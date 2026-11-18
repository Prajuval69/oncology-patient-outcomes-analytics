from __future__ import annotations

import argparse
import json
from dataclasses import replace

import pandas as pd

from .analytics import descriptive_analysis, logistic_association_model, statistical_tests
from .charts import create_charts
from .config import Settings
from .database import build_database, build_marts, connect
from .generate_data import write_synthetic_data
from .modeling import train_models
from .reporting import generate_report
from .survival import run_survival_analysis
from .validation import save_validation


def run_pipeline(settings: Settings = Settings()) -> dict[str, object]:
    settings.ensure_directories()
    tables = write_synthetic_data(settings)
    validation = save_validation(tables, settings)
    if (validation.status == "fail").any():
        raise RuntimeError("Data validation failed; inspect data/processed/validation_results.csv")
    build_database(tables, settings)
    marts = build_marts(settings)
    cohort = marts["cohort"]
    descriptive_analysis(cohort, settings)
    statistical_tests(cohort, settings)
    logistic_association_model(cohort, settings)
    survival = run_survival_analysis(marts["survival_input"], settings)
    metrics = train_models(cohort, settings)
    create_charts(settings)
    report = generate_report(settings)
    with connect(settings.database_path) as connection:
        tables_in_db = pd.read_sql_query("SELECT name FROM sqlite_master WHERE type IN ('table','view')", connection).name.tolist()
    manifest = {
        "synthetic": True, "seed": settings.seed, "patients": settings.n_patients,
        "database": str(settings.database_path.relative_to(settings.root)), "database_objects": sorted(tables_in_db),
        "processed_files": sorted(p.name for p in settings.processed_dir.glob("*")),
        "charts": sorted(p.name for p in (settings.artifact_dir / "charts").glob("*.png")),
        "models": sorted(p.name for p in (settings.artifact_dir / "models").glob("*.joblib")),
        "report": str(report.relative_to(settings.root)), "validation_passed": True,
        "random_forest_roc_auc": metrics["models"]["random_forest"]["roc_auc"],
    }
    (settings.artifact_dir / "run_manifest.json").write_text(json.dumps(manifest, indent=2), encoding="utf-8")
    return manifest


def main() -> None:
    parser = argparse.ArgumentParser(description="Run the complete synthetic oncology analytics pipeline.")
    parser.add_argument("--patients", type=int, default=1500)
    parser.add_argument("--seed", type=int, default=20260923)
    args = parser.parse_args()
    manifest = run_pipeline(replace(Settings(), n_patients=args.patients, seed=args.seed))
    print(json.dumps(manifest, indent=2))


if __name__ == "__main__":
    main()
