"""Deterministic, entirely synthetic oncology-style relational data."""

from __future__ import annotations

from dataclasses import replace
from pathlib import Path

import numpy as np
import pandas as pd

from .config import Settings


CANCERS = ["Breast", "Lung", "Colorectal", "Prostate", "Melanoma"]
STAGES = ["I", "II", "III", "IV"]
RESPONSES = ["Complete response", "Partial response", "Stable disease", "Progressive disease", "Unknown"]


def _sigmoid(x: np.ndarray) -> np.ndarray:
    return 1.0 / (1.0 + np.exp(-x))


def generate_synthetic_data(n_patients: int = 1500, seed: int = 20260923) -> dict[str, pd.DataFrame]:
    if n_patients < 1:
        raise ValueError("n_patients must be positive")
    rng = np.random.default_rng(seed)
    patient_ids = [f"SYN-P{i:05d}" for i in range(1, n_patients + 1)]
    cancer = rng.choice(CANCERS, n_patients, p=[0.25, 0.24, 0.20, 0.19, 0.12])
    sex = []
    for c in cancer:
        if c == "Prostate":
            sex.append("Male")
        elif c == "Breast":
            sex.append(rng.choice(["Female", "Male"], p=[0.985, 0.015]))
        else:
            sex.append(rng.choice(["Female", "Male"], p=[0.49, 0.51]))
    sex = np.asarray(sex)
    age = np.clip(np.rint(rng.normal(64, 11, n_patients)), 25, 90).astype(int)
    region = rng.choice(["Northeast", "Midwest", "South", "West"], n_patients, p=[0.19, 0.22, 0.37, 0.22])
    race = rng.choice(["White", "Black", "Asian", "Hispanic", "Other/Unknown"], n_patients, p=[0.54, 0.16, 0.11, 0.14, 0.05])
    insurance = rng.choice(["Commercial", "Medicare", "Medicaid", "Other"], n_patients, p=[0.39, 0.43, 0.13, 0.05])
    patients = pd.DataFrame({
        "patient_id": patient_ids, "age_at_diagnosis": age, "sex": sex,
        "race_ethnicity": race, "region": region, "insurance_type": insurance,
        "synthetic_record": 1,
    })

    stage = rng.choice(STAGES, n_patients, p=[0.20, 0.29, 0.29, 0.22])
    # Later stage and comorbidity are associated with poorer performance status by construction.
    stage_num = pd.Series(stage).map({"I": 1, "II": 2, "III": 3, "IV": 4}).to_numpy()
    ecog_prob = np.clip((stage_num - 1) * 0.10 + (age - 50) * 0.004, 0.05, 0.72)
    ecog = np.where(rng.random(n_patients) < ecog_prob, rng.choice([1, 2, 3], n_patients, p=[0.55, 0.35, 0.10]), 0)
    dx_start = np.datetime64("2018-01-01")
    diagnosis_date = pd.to_datetime(dx_start + rng.integers(0, 2191, n_patients).astype("timedelta64[D]"))
    biomarker = []
    for c in cancer:
        choices = {
            "Breast": (["HR+/HER2-", "HER2+", "Triple-negative", "Unknown"], [0.57, 0.18, 0.17, 0.08]),
            "Lung": (["EGFR+", "ALK+", "PD-L1 high", "No actionable marker", "Unknown"], [0.17, 0.05, 0.22, 0.43, 0.13]),
            "Colorectal": (["RAS wild-type", "RAS mutated", "MSI-high", "Unknown"], [0.38, 0.42, 0.08, 0.12]),
            "Prostate": (["Hormone-sensitive", "Castration-resistant", "Unknown"], [0.66, 0.25, 0.09]),
            "Melanoma": (["BRAF+", "BRAF wild-type", "Unknown"], [0.43, 0.47, 0.10]),
        }[c]
        biomarker.append(rng.choice(choices[0], p=choices[1]))
    # Explicit, realistic optional missingness.
    biomarker = np.asarray(biomarker, dtype=object)
    biomarker[rng.random(n_patients) < 0.045] = None
    ecog_float = ecog.astype(float)
    ecog_float[rng.random(n_patients) < 0.035] = np.nan
    diagnoses = pd.DataFrame({
        "diagnosis_id": [f"DX{i:05d}" for i in range(1, n_patients + 1)],
        "patient_id": patient_ids, "cancer_type": cancer,
        "diagnosis_date": diagnosis_date.strftime("%Y-%m-%d"), "stage": stage,
        "biomarker_status": biomarker, "ecog_status": ecog_float,
    })

    smoking = np.where(cancer == "Lung", rng.binomial(1, 0.65, n_patients), rng.binomial(1, 0.22, n_patients))
    diabetes = rng.binomial(1, _sigmoid(-2.5 + 0.035 * (age - 45)))
    cardio = rng.binomial(1, _sigmoid(-3.0 + 0.045 * (age - 45)))
    renal = rng.binomial(1, _sigmoid(-4.0 + 0.04 * (age - 45)))
    pulmonary = np.maximum(rng.binomial(1, 0.08, n_patients), smoking * rng.binomial(1, 0.20, n_patients))
    comorbidity_count = diabetes + cardio + renal + pulmonary
    comorbidities = pd.DataFrame({
        "comorbidity_id": [f"CM{i:05d}" for i in range(1, n_patients + 1)],
        "patient_id": patient_ids, "diabetes": diabetes, "cardiovascular_disease": cardio,
        "chronic_kidney_disease": renal, "chronic_pulmonary_disease": pulmonary,
        "smoking_history": smoking, "comorbidity_count": comorbidity_count,
    })

    treatments = pd.DataFrame([
        ("TRT01", "Cytotoxic combination", "Chemotherapy"),
        ("TRT02", "Checkpoint inhibitor", "Immunotherapy"),
        ("TRT03", "Oral targeted agent", "Targeted therapy"),
        ("TRT04", "Endocrine regimen", "Hormone therapy"),
        ("TRT05", "Definitive radiation", "Radiation"),
        ("TRT06", "Surgical resection", "Surgery"),
    ], columns=["treatment_id", "regimen_name", "treatment_class"])
    allowed_by_cancer = {
        "Breast": ["TRT01", "TRT03", "TRT04", "TRT05", "TRT06"],
        "Lung": ["TRT01", "TRT02", "TRT03", "TRT05", "TRT06"],
        "Colorectal": ["TRT01", "TRT02", "TRT03", "TRT05", "TRT06"],
        "Prostate": ["TRT01", "TRT03", "TRT04", "TRT05", "TRT06"],
        "Melanoma": ["TRT01", "TRT02", "TRT03", "TRT05", "TRT06"],
    }
    treatment_rows = []
    event_no = 1
    first_treatment_ids: list[str] = []
    max_lines_list: list[int] = []
    last_end_dates: list[pd.Timestamp] = []
    for i, pid in enumerate(patient_ids):
        max_lines = int(rng.choice([1, 2, 3], p=[0.58, 0.30, 0.12] if stage_num[i] < 4 else [0.40, 0.38, 0.22]))
        max_lines_list.append(max_lines)
        start = diagnosis_date[i] + pd.Timedelta(days=int(rng.integers(7, 76)))
        prior = None
        for line in range(1, max_lines + 1):
            options = allowed_by_cancer[cancer[i]].copy()
            weights = np.ones(len(options), dtype=float)
            if stage_num[i] <= 2 and "TRT06" in options:
                weights[options.index("TRT06")] = 3.4
            if stage_num[i] >= 3 and "TRT01" in options:
                weights[options.index("TRT01")] = 2.5
            if prior in options and len(options) > 1:
                weights[options.index(prior)] *= 0.25
            treatment_id = rng.choice(options, p=weights / weights.sum())
            if line == 1:
                first_treatment_ids.append(treatment_id)
            duration = int(rng.integers(35, 211))
            end = start + pd.Timedelta(days=duration)
            treatment_rows.append((f"TE{event_no:06d}", pid, treatment_id, line, start.strftime("%Y-%m-%d"), end.strftime("%Y-%m-%d"), duration))
            event_no += 1
            prior = treatment_id
            start = end + pd.Timedelta(days=int(rng.integers(14, 91)))
        last_end_dates.append(end)
    treatment_events = pd.DataFrame(treatment_rows, columns=[
        "treatment_event_id", "patient_id", "treatment_id", "treatment_line",
        "treatment_start_date", "treatment_end_date", "duration_days",
    ])

    first_class = pd.Series(first_treatment_ids).map(treatments.set_index("treatment_id")["treatment_class"]).to_numpy()
    ecog_imputed = np.nan_to_num(ecog_float, nan=1.0)
    favorable_marker = np.array([0 if x is None or x == "Unknown" or "No actionable" in str(x) else 1 for x in biomarker])
    response_logit = 0.75 - 0.68 * (stage_num - 2) - 0.52 * ecog_imputed - 0.23 * comorbidity_count - 0.017 * (age - 60) + 0.56 * favorable_marker
    response_logit += np.isin(first_class, ["Targeted therapy", "Immunotherapy"]) * 0.40
    responder = rng.binomial(1, np.clip(_sigmoid(response_logit), 0.10, 0.85))
    response_category = []
    for r in responder:
        response_category.append(rng.choice(["Complete response", "Partial response"], p=[0.22, 0.78]) if r else rng.choice(["Stable disease", "Progressive disease", "Unknown"], p=[0.45, 0.48, 0.07]))

    # Synthetic overall-survival process with administrative censoring.
    hazard_multiplier = np.exp(0.48 * (stage_num - 2) + 0.30 * ecog_imputed + 0.12 * comorbidity_count + 0.008 * (age - 60) - 0.38 * responder)
    latent_survival = rng.exponential(scale=1750 / hazard_multiplier).astype(int) + 30
    administrative = (pd.Timestamp("2025-12-31") - diagnosis_date).days.to_numpy()
    random_loss = rng.integers(365, 2200, n_patients)
    censor_time = np.minimum(administrative, random_loss)
    survival_days = np.maximum(1, np.minimum(latent_survival, censor_time))
    event = (latent_survival <= censor_time).astype(int)
    progression_prob = np.clip(_sigmoid(-0.1 + 0.55 * (stage_num - 2) + 0.32 * ecog_imputed - 0.65 * responder), 0.08, 0.90)
    progression = rng.binomial(1, progression_prob)
    progression_days = np.where(progression == 1, np.maximum(20, (survival_days * rng.uniform(0.25, 0.85, n_patients)).astype(int)), np.nan)
    outcomes = pd.DataFrame({
        "outcome_id": [f"OUT{i:05d}" for i in range(1, n_patients + 1)],
        "patient_id": patient_ids, "response_category": response_category,
        "responder": responder, "progression_event": progression,
        "progression_days": progression_days, "survival_days": survival_days,
        "death_event": event,
        "last_followup_date": (diagnosis_date + pd.to_timedelta(survival_days, unit="D")).strftime("%Y-%m-%d"),
    })

    treatment_count = np.asarray(max_lines_list)
    outpatient = rng.poisson(4 + 2.3 * treatment_count + 1.5 * comorbidity_count + 1.2 * progression)
    emergency = rng.poisson(0.35 + 0.28 * comorbidity_count + 0.5 * progression)
    inpatient = rng.poisson(0.18 + 0.24 * (stage_num - 1) + 0.34 * comorbidity_count + 0.55 * progression)
    total_cost = np.round(4200 + outpatient * 580 + emergency * 1900 + inpatient * 8700 + treatment_count * 14500 + rng.normal(0, 3500, n_patients), 2)
    utilization = pd.DataFrame({
        "utilization_id": [f"UTL{i:05d}" for i in range(1, n_patients + 1)],
        "patient_id": patient_ids, "outpatient_visits": outpatient,
        "emergency_visits": emergency, "inpatient_admissions": inpatient,
        "total_cost_usd": np.maximum(0, total_cost),
    })
    return {
        "patients": patients, "diagnoses": diagnoses, "treatments": treatments,
        "treatment_events": treatment_events, "outcomes": outcomes,
        "comorbidities": comorbidities, "utilization": utilization,
    }


def write_synthetic_data(settings: Settings = Settings()) -> dict[str, pd.DataFrame]:
    settings.ensure_directories()
    tables = generate_synthetic_data(settings.n_patients, settings.seed)
    for name, frame in tables.items():
        frame.to_csv(settings.raw_dir / f"{name}.csv", index=False)
    return tables


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--patients", type=int, default=1500)
    parser.add_argument("--seed", type=int, default=20260923)
    args = parser.parse_args()
    write_synthetic_data(replace(Settings(), n_patients=args.patients, seed=args.seed))
