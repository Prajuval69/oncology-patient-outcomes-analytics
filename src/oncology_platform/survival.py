from __future__ import annotations

import json

import numpy as np
import pandas as pd
from lifelines import CoxPHFitter, KaplanMeierFitter
from lifelines.statistics import multivariate_logrank_test, proportional_hazard_test

from .config import Settings


def run_survival_analysis(survival: pd.DataFrame, settings: Settings = Settings()) -> dict[str, pd.DataFrame]:
    data = survival.copy()
    data["ecog_status"] = data.ecog_status.fillna(data.ecog_status.median())
    curve_rows, summary_rows, risk_rows = [], [], []
    for label, frame in [("Overall", data), *list(data.groupby("stage", observed=True))]:
        kmf = KaplanMeierFitter(label=str(label)).fit(frame.survival_days, frame.death_event)
        sf = kmf.survival_function_.reset_index()
        sf.columns = ["timeline_days", "survival_probability"]
        sf["group"] = str(label)
        curve_rows.append(sf)
        ci = kmf.confidence_interval_survival_function_.reset_index()
        ci.columns = ["timeline_days", "ci_lower", "ci_upper"]
        curve_rows[-1] = curve_rows[-1].merge(ci, on="timeline_days", how="left")
        median = float(kmf.median_survival_time_)
        summary_rows.append({"group": str(label), "patients": len(frame), "events": int(frame.death_event.sum()), "median_survival_days": median if np.isfinite(median) else np.nan})
        for t in [0, 365, 730, 1095, 1460, 1825]:
            risk_rows.append({"group": str(label), "time_days": t, "number_at_risk": int((frame.survival_days >= t).sum())})
    curves = pd.concat(curve_rows, ignore_index=True)
    summaries = pd.DataFrame(summary_rows)
    at_risk = pd.DataFrame(risk_rows)
    logrank = multivariate_logrank_test(data.survival_days, data.stage, data.death_event)

    cox = data[["survival_days", "death_event", "age_at_diagnosis", "sex", "stage", "ecog_status", "comorbidity_count", "first_treatment_class"]].copy()
    cox["stage"] = cox.stage.map({"I": 1, "II": 2, "III": 3, "IV": 4})
    cox = pd.get_dummies(cox, columns=["sex", "first_treatment_class"], drop_first=True, dtype=float)
    cph = CoxPHFitter(penalizer=0.02)
    cph.fit(cox, duration_col="survival_days", event_col="death_event")
    cox_results = cph.summary.reset_index().rename(columns={"covariate": "term", "exp(coef)": "hazard_ratio", "exp(coef) lower 95%": "ci_lower", "exp(coef) upper 95%": "ci_upper"})
    cox_results = cox_results[["term", "coef", "hazard_ratio", "ci_lower", "ci_upper", "p"]].rename(columns={"p": "p_value"})
    ph = proportional_hazard_test(cph, cox, time_transform="rank").summary.reset_index().rename(columns={"index": "term", "p": "p_value"})

    outputs = {"km_curve": curves, "km_summary": summaries, "number_at_risk": at_risk, "cox_results": cox_results, "ph_assumption_tests": ph}
    for name, frame in outputs.items():
        frame.to_csv(settings.processed_dir / f"{name}.csv", index=False)
    (settings.processed_dir / "survival_tests.json").write_text(json.dumps({
        "stage_logrank_statistic": float(logrank.test_statistic), "stage_logrank_p_value": float(logrank.p_value),
        "cox_concordance_index": float(cph.concordance_index_), "ph_terms_below_0_05": int((ph.p_value < .05).sum()),
    }, indent=2), encoding="utf-8")
    return outputs


def km_for_subset(frame: pd.DataFrame, group_column: str | None = None) -> pd.DataFrame:
    if frame.empty:
        return pd.DataFrame(columns=["timeline_days", "survival_probability", "group"])
    groups = [("Overall", frame)] if not group_column else list(frame.groupby(group_column, observed=True))
    rows = []
    for label, group in groups:
        kmf = KaplanMeierFitter().fit(group.survival_days, group.death_event)
        curve = kmf.survival_function_.reset_index()
        curve.columns = ["timeline_days", "survival_probability"]
        curve["group"] = str(label)
        rows.append(curve)
    return pd.concat(rows, ignore_index=True)

