from __future__ import annotations

import json
from collections.abc import Callable

import pandas as pd

from .config import Settings
from .generate_data import RESPONSES, STAGES


def validate_tables(tables: dict[str, pd.DataFrame]) -> pd.DataFrame:
    p, d, te, o, u = (tables[k] for k in ("patients", "diagnoses", "treatment_events", "outcomes", "utilization"))
    checks: list[tuple[str, int, str, str]] = []

    def add(rule: str, failures: int, severity: str, detail: str) -> None:
        checks.append((rule, int(failures), severity, detail))

    add("patient_id_not_null", p.patient_id.isna().sum(), "critical", "Patient identifiers are required.")
    add("patient_id_unique", p.patient_id.duplicated().sum(), "critical", "One row per patient is required.")
    add("age_plausible", (~p.age_at_diagnosis.between(18, 100)).sum(), "high", "Age must be 18-100.")
    add("stage_allowed", (~d.stage.isin(STAGES)).sum(), "high", "Stage must be I-IV.")
    add("response_allowed", (~o.response_category.isin(RESPONSES)).sum(), "high", "Response must use the controlled vocabulary.")
    add("event_binary", (~o.death_event.isin([0, 1])).sum() + (~o.progression_event.isin([0, 1])).sum(), "critical", "Event flags must be binary.")
    add("followup_non_negative", (o.survival_days < 0).sum(), "critical", "Follow-up time cannot be negative.")
    add("treatment_event_id_unique", te.treatment_event_id.duplicated().sum(), "critical", "Treatment-event identifiers must be unique.")
    dx = d.set_index("patient_id").diagnosis_date.pipe(pd.to_datetime)
    starts = pd.to_datetime(te.treatment_start_date)
    add("diagnosis_before_treatment", (te.patient_id.map(dx) > starts).sum(), "critical", "Diagnosis must precede every treatment start.")
    add("treatment_date_order", (starts > pd.to_datetime(te.treatment_end_date)).sum(), "critical", "Treatment start must not follow end.")
    for name, frame in tables.items():
        if name not in {"patients", "treatments"} and "patient_id" in frame:
            add(f"{name}_patient_fk", (~frame.patient_id.isin(p.patient_id)).sum(), "critical", f"All {name} patient keys must resolve.")
    add("treatment_reference_fk", (~te.treatment_id.isin(tables["treatments"].treatment_id)).sum(), "critical", "All treatment IDs must resolve.")
    numeric = ["outpatient_visits", "emergency_visits", "inpatient_admissions", "total_cost_usd"]
    add("utilization_non_negative", (u[numeric] < 0).sum().sum(), "high", "Utilization and costs cannot be negative.")
    add("line_sequence_contiguous", _line_sequence_failures(te), "high", "Treatment lines must begin at one and be contiguous per patient.")
    result = pd.DataFrame(checks, columns=["rule", "failure_count", "severity", "detail"])
    result["status"] = result.failure_count.map(lambda x: "pass" if x == 0 else "fail")
    return result[["rule", "status", "severity", "failure_count", "detail"]]


def _line_sequence_failures(events: pd.DataFrame) -> int:
    failures = 0
    for _, group in events.groupby("patient_id"):
        observed = sorted(group.treatment_line.astype(int).tolist())
        failures += int(observed != list(range(1, len(observed) + 1)))
    return failures


def missingness_profile(tables: dict[str, pd.DataFrame]) -> pd.DataFrame:
    rows = []
    for table, frame in tables.items():
        for column in frame.columns:
            count = int(frame[column].isna().sum())
            rows.append({"table": table, "column": column, "missing_count": count, "missing_percent": round(100 * count / len(frame), 3)})
    return pd.DataFrame(rows)


def save_validation(tables: dict[str, pd.DataFrame], settings: Settings = Settings()) -> pd.DataFrame:
    result = validate_tables(tables)
    result.to_csv(settings.processed_dir / "validation_results.csv", index=False)
    missingness_profile(tables).to_csv(settings.processed_dir / "missingness_profile.csv", index=False)
    summary = {
        "checks": int(len(result)), "passed": int((result.status == "pass").sum()),
        "failed": int((result.status == "fail").sum()), "critical_failures": int(((result.status == "fail") & (result.severity == "critical")).sum()),
    }
    (settings.processed_dir / "validation_summary.json").write_text(json.dumps(summary, indent=2), encoding="utf-8")
    return result

