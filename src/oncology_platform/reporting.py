from __future__ import annotations

import json
from pathlib import Path

import pandas as pd

from .config import Settings


def generate_report(settings: Settings = Settings()) -> Path:
    kpi = pd.read_csv(settings.processed_dir / "kpis.csv").iloc[0]
    stage = pd.read_csv(settings.processed_dir / "outcomes_by_stage.csv")
    km = pd.read_csv(settings.processed_dir / "km_summary.csv")
    cox = pd.read_csv(settings.processed_dir / "cox_results.csv")
    tests = pd.read_csv(settings.processed_dir / "statistical_tests.csv")
    validation = pd.read_csv(settings.processed_dir / "validation_results.csv")
    metrics = json.loads((settings.processed_dir / "model_metrics.json").read_text(encoding="utf-8"))
    sequences = pd.read_csv(settings.processed_dir / "treatment_sequences.csv").treatment_sequence.value_counts().head(5)
    rf = metrics["models"]["random_forest"]
    lines = [
        "# Oncology Patient Outcomes & Treatment Pathway Analytics — Stakeholder Report",
        "", "> **Synthetic-data demonstration.** Every record is generated; this is not clinical decision support and contains no PHI.",
        "", "## Executive overview", "",
        f"The analytical cohort contains **{int(kpi.patients):,} synthetic patients**, **{int(kpi.treatment_events):,} treatment events**, a **{kpi.response_rate_percent:.1f}%** binary response rate, and a **{kpi.progression_rate_percent:.1f}%** progression-event rate. These results describe constructed associations only; they do not estimate treatment effectiveness.",
        "", "## Cohort snapshot", "",
        f"Median follow-up was **{pd.read_csv(settings.processed_dir / 'descriptive_summary.csv').iloc[0].median_followup_days:,.0f} days**. Mean modeled cost was **${kpi.mean_total_cost_usd:,.0f}** per patient. Age, cancer type, stage, region, race/ethnicity, performance status, biomarkers, comorbidities, and treatment class are available for stratified exploration.",
        "", "## Treatment pathways", "", "The five most frequent ordered treatment-class pathways were:", "",
    ]
    lines += [f"- {name}: {count:,} patients" for name, count in sequences.items()]
    lines += ["", "## Outcomes and statistical associations", ""]
    for _, row in stage.iterrows():
        lines.append(f"- Stage {row.stage}: {int(row.patients):,} patients; response {row.response_rate:.1f}%; progression {row.progression_rate:.1f}%.")
    lines += ["", f"The stage–response chi-square association test yielded p={tests.iloc[0].p_value:.3g}. This is an association in synthetic observational-style data, not a causal comparison.", "", "## Survival", ""]
    for _, row in km.iterrows():
        median = "not reached" if pd.isna(row.median_survival_days) else f"{row.median_survival_days:,.0f} days"
        label = "Overall" if row.group == "Overall" else f"Stage {row.group}"
        lines.append(f"- {label}: {int(row.events):,}/{int(row.patients):,} events; median survival {median}.")
    top_cox = cox.assign(abs_coef=cox.coef.abs()).sort_values("abs_coef", ascending=False).head(3)
    lines += ["", "The Cox model reports adjusted hazard-ratio associations. The largest modeled coefficient magnitudes were " + ", ".join(f"{r.term} (HR {r.hazard_ratio:.2f})" for _, r in top_cox.iterrows()) + ". Proportional-hazards diagnostics are provided separately.", "", "## Predictive modeling", "",
        f"On the held-out test set, the random forest achieved ROC-AUC **{rf['roc_auc']:.3f}**, PR-AUC **{rf['pr_auc']:.3f}**, precision **{rf['precision']:.3f}**, recall **{rf['recall']:.3f}**, and F1 **{rf['f1']:.3f}**. Five-fold training-set cross-validation and calibration outputs are included. Performance on synthetic data does not establish clinical utility or transportability.",
        "", "## Data quality", "", f"Automated validation passed **{(validation.status == 'pass').sum()}/{len(validation)}** rules; critical failures: **{((validation.status == 'fail') & (validation.severity == 'critical')).sum()}**. Missing biomarker and ECOG values are intentional and handled through model-pipeline imputation.",
        "", "## Limitations", "", "- Fully synthetic data; constructed dependencies are not clinical truth.", "- Observational-style analyses are subject to confounding, selection bias, and measurement limitations.", "- Response is a simplified patient-level endpoint and is not a validated oncology endpoint.", "- Treatment classes and costs are generalized; sequencing does not encode dose, adherence, or clinical rationale.", "- Missingness is simulated and may not resemble operational data.", "- No causal inference, clinical validation, fairness certification, or treatment recommendation is intended.",
    ]
    path = settings.root / "reports" / "stakeholder_report.md"
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")
    return path

