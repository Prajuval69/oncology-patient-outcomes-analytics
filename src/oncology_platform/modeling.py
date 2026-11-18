from __future__ import annotations

import json

import joblib
import numpy as np
import pandas as pd
from sklearn.calibration import calibration_curve
from sklearn.compose import ColumnTransformer
from sklearn.ensemble import RandomForestClassifier
from sklearn.impute import SimpleImputer
from sklearn.inspection import permutation_importance
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import (average_precision_score, confusion_matrix, f1_score,
                             precision_score, recall_score, roc_auc_score,
                             roc_curve, precision_recall_curve)
from sklearn.model_selection import StratifiedKFold, cross_validate, train_test_split
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder, StandardScaler

from .config import Settings


FEATURES = ["age_at_diagnosis", "sex", "race_ethnicity", "region", "insurance_type", "cancer_type", "stage", "biomarker_status", "ecog_status", "diabetes", "cardiovascular_disease", "chronic_kidney_disease", "chronic_pulmonary_disease", "smoking_history", "comorbidity_count", "first_treatment_class"]
NUMERIC = ["age_at_diagnosis", "ecog_status", "diabetes", "cardiovascular_disease", "chronic_kidney_disease", "chronic_pulmonary_disease", "smoking_history", "comorbidity_count"]
CATEGORICAL = [c for c in FEATURES if c not in NUMERIC]


def _preprocessor() -> ColumnTransformer:
    return ColumnTransformer([
        ("numeric", Pipeline([("impute", SimpleImputer(strategy="median")), ("scale", StandardScaler())]), NUMERIC),
        ("categorical", Pipeline([
            ("impute_none", SimpleImputer(strategy="constant", fill_value="Unknown", missing_values=None)),
            ("impute_nan", SimpleImputer(strategy="most_frequent")),
            ("onehot", OneHotEncoder(handle_unknown="ignore", sparse_output=False)),
        ]), CATEGORICAL),
    ])


def _metrics(y_true: pd.Series, probability: np.ndarray) -> dict[str, float]:
    prediction = (probability >= 0.5).astype(int)
    return {
        "roc_auc": float(roc_auc_score(y_true, probability)), "pr_auc": float(average_precision_score(y_true, probability)),
        "precision": float(precision_score(y_true, prediction, zero_division=0)), "recall": float(recall_score(y_true, prediction, zero_division=0)),
        "f1": float(f1_score(y_true, prediction, zero_division=0)), "prevalence": float(np.mean(y_true)),
    }


def train_models(cohort: pd.DataFrame, settings: Settings = Settings()) -> dict[str, object]:
    x, y = cohort[FEATURES].copy(), cohort.responder.astype(int)
    x_train, x_test, y_train, y_test = train_test_split(x, y, test_size=.25, random_state=settings.seed, stratify=y)
    models = {
        "logistic_regression": LogisticRegression(max_iter=1200, class_weight="balanced", random_state=settings.seed),
        "random_forest": RandomForestClassifier(n_estimators=350, min_samples_leaf=5, class_weight="balanced", random_state=settings.seed, n_jobs=-1),
    }
    cv = StratifiedKFold(n_splits=5, shuffle=True, random_state=settings.seed)
    results: dict[str, object] = {"target": "responder", "prediction_point": "after diagnosis and first-treatment selection, before outcome assessment", "features": FEATURES, "models": {}}
    fitted = {}
    curves = []
    for name, estimator in models.items():
        pipe = Pipeline([("preprocess", _preprocessor()), ("model", estimator)])
        scores = cross_validate(pipe, x_train, y_train, cv=cv, scoring={"roc_auc": "roc_auc", "pr_auc": "average_precision", "f1": "f1"}, n_jobs=-1)
        pipe.fit(x_train, y_train)
        probability = pipe.predict_proba(x_test)[:, 1]
        result = _metrics(y_test, probability)
        result.update({f"cv_{m}_mean": float(scores[f"test_{m}"].mean()) for m in ["roc_auc", "pr_auc", "f1"]})
        result.update({f"cv_{m}_std": float(scores[f"test_{m}"].std()) for m in ["roc_auc", "pr_auc", "f1"]})
        result["confusion_matrix"] = confusion_matrix(y_test, probability >= .5).tolist()
        results["models"][name] = result
        fitted[name] = pipe
        fpr, tpr, _ = roc_curve(y_test, probability)
        precision, recall, _ = precision_recall_curve(y_test, probability)
        curves.append(pd.DataFrame({"model": name, "curve": "ROC", "x": fpr, "y": tpr}))
        curves.append(pd.DataFrame({"model": name, "curve": "PR", "x": recall, "y": precision}))
        prob_true, prob_pred = calibration_curve(y_test, probability, n_bins=10, strategy="quantile")
        pd.DataFrame({"model": name, "mean_predicted_probability": prob_pred, "observed_fraction_positive": prob_true}).to_csv(settings.processed_dir / f"calibration_{name}.csv", index=False)
        pd.DataFrame({"patient_id": cohort.loc[x_test.index, "patient_id"], "observed": y_test, "predicted_probability": probability, "model": name}).to_csv(settings.processed_dir / f"predictions_{name}.csv", index=False)
        joblib.dump(pipe, settings.artifact_dir / "models" / f"{name}.joblib")
    pd.concat(curves, ignore_index=True).to_csv(settings.processed_dir / "model_curves.csv", index=False)

    rf = fitted["random_forest"]
    feature_names = rf.named_steps["preprocess"].get_feature_names_out()
    importance = pd.DataFrame({"feature": feature_names, "importance": rf.named_steps["model"].feature_importances_}).sort_values("importance", ascending=False)
    importance.to_csv(settings.processed_dir / "feature_importance.csv", index=False)
    explainability = _explain_model(rf, x_test, y_test, feature_names, settings)
    results["explainability_method"] = explainability
    (settings.processed_dir / "model_metrics.json").write_text(json.dumps(results, indent=2), encoding="utf-8")
    return results


def _explain_model(pipe: Pipeline, x_test: pd.DataFrame, y_test: pd.Series, feature_names: np.ndarray, settings: Settings) -> str:
    transformed = pipe.named_steps["preprocess"].transform(x_test)
    sample = transformed[: min(250, len(transformed))]
    try:
        import shap
        explainer = shap.TreeExplainer(pipe.named_steps["model"])
        values = explainer.shap_values(sample)
        if isinstance(values, list):
            values = values[-1]
        values = np.asarray(values)
        if values.ndim == 3:
            values = values[:, :, -1]
        mean_abs = np.abs(values).mean(axis=0)
        method = "TreeSHAP mean absolute contribution"
    except Exception:
        perm = permutation_importance(pipe, x_test, y_test, n_repeats=8, random_state=settings.seed, scoring="roc_auc", n_jobs=-1)
        pd.DataFrame({"feature": FEATURES, "mean_absolute_contribution": np.abs(perm.importances_mean), "method": "held-out permutation importance fallback"}).sort_values("mean_absolute_contribution", ascending=False).to_csv(settings.processed_dir / "explainability.csv", index=False)
        return "held-out permutation importance fallback"
    pd.DataFrame({"feature": feature_names, "mean_absolute_contribution": mean_abs, "method": method}).sort_values("mean_absolute_contribution", ascending=False).to_csv(settings.processed_dir / "explainability.csv", index=False)
    return method
