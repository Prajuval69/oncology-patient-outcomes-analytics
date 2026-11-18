from __future__ import annotations

import json

import numpy as np
import pandas as pd
import statsmodels.api as sm
from scipy.stats import chi2_contingency, mannwhitneyu

from .config import Settings


def descriptive_analysis(cohort: pd.DataFrame, settings: Settings = Settings()) -> dict[str, pd.DataFrame]:
    age = cohort.age_at_diagnosis
    overall = pd.DataFrame([{
        "patients": len(cohort), "age_mean": round(age.mean(), 2), "age_median": round(age.median(), 2),
        "age_q1": round(age.quantile(.25), 2), "age_q3": round(age.quantile(.75), 2),
        "response_rate_percent": round(100 * cohort.responder.mean(), 2),
        "progression_rate_percent": round(100 * cohort.progression_event.mean(), 2),
        "median_followup_days": round(cohort.survival_days.median(), 2),
        "median_cost_usd": round(cohort.total_cost_usd.median(), 2),
    }])
    outcomes_by_stage = cohort.groupby("stage", observed=True).agg(
        patients=("patient_id", "nunique"), responders=("responder", "sum"),
        response_rate=("responder", "mean"), progression_rate=("progression_event", "mean"),
        median_followup_days=("survival_days", "median"),
    ).reset_index()
    outcomes_by_stage[["response_rate", "progression_rate"]] *= 100
    outcomes_by_cancer = cohort.groupby("cancer_type", observed=True).agg(
        patients=("patient_id", "nunique"), response_rate=("responder", "mean"),
        progression_rate=("progression_event", "mean"), median_followup_days=("survival_days", "median")
    ).reset_index()
    outcomes_by_cancer[["response_rate", "progression_rate"]] *= 100
    for name, frame in {"descriptive_summary": overall, "outcomes_by_stage": outcomes_by_stage, "outcomes_by_cancer": outcomes_by_cancer}.items():
        frame.to_csv(settings.processed_dir / f"{name}.csv", index=False)
    return {"overall": overall, "by_stage": outcomes_by_stage, "by_cancer": outcomes_by_cancer}


def statistical_tests(cohort: pd.DataFrame, settings: Settings = Settings()) -> pd.DataFrame:
    rows = []
    stage_table = pd.crosstab(cohort.stage, cohort.responder)
    chi2, p, dof, _ = chi2_contingency(stage_table)
    rows.append({"test": "Chi-square", "question": "Response differs by stage", "statistic": chi2, "degrees_of_freedom": dof, "p_value": p, "interpretation": "Association test; not causal."})
    a = cohort.loc[cohort.responder == 1, "age_at_diagnosis"]
    b = cohort.loc[cohort.responder == 0, "age_at_diagnosis"]
    stat, p = mannwhitneyu(a, b, alternative="two-sided")
    rows.append({"test": "Mann-Whitney U", "question": "Age distribution differs by response", "statistic": stat, "degrees_of_freedom": np.nan, "p_value": p, "interpretation": "Unadjusted distribution comparison."})
    result = pd.DataFrame(rows)
    result.to_csv(settings.processed_dir / "statistical_tests.csv", index=False)
    return result


def logistic_association_model(cohort: pd.DataFrame, settings: Settings = Settings()) -> pd.DataFrame:
    model_data = cohort[["responder", "age_at_diagnosis", "sex", "stage", "ecog_status", "comorbidity_count", "first_treatment_class"]].copy()
    model_data["ecog_status"] = model_data.ecog_status.fillna(model_data.ecog_status.median())
    model_data["stage"] = model_data.stage.map({"I": 1, "II": 2, "III": 3, "IV": 4})
    x = pd.get_dummies(model_data.drop(columns="responder"), drop_first=True, dtype=float)
    x = sm.add_constant(x.astype(float))
    fitted = sm.Logit(model_data.responder.astype(float), x).fit(disp=False, maxiter=200)
    conf = fitted.conf_int()
    result = pd.DataFrame({
        "term": fitted.params.index, "coefficient": fitted.params.values,
        "odds_ratio": np.exp(fitted.params.values), "ci_lower": np.exp(conf[0].values),
        "ci_upper": np.exp(conf[1].values), "p_value": fitted.pvalues.values,
    })
    result.to_csv(settings.processed_dir / "logistic_association_results.csv", index=False)
    (settings.processed_dir / "logistic_model_summary.json").write_text(json.dumps({"n": len(model_data), "pseudo_r_squared": fitted.prsquared, "converged": bool(fitted.mle_retvals["converged"])}, indent=2), encoding="utf-8")
    return result

