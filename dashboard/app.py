"""Streamlit dashboard for the synthetic oncology analytics platform."""

from __future__ import annotations

import json
import sys
from pathlib import Path

import numpy as np
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
from oncology_platform.survival import km_for_subset


COLORS = ["#2457A7", "#E09F3E", "#688E26", "#B56576", "#6C757D"]


@st.cache_data(show_spinner=False)
def load_data(root: str = str(ROOT)) -> dict[str, object]:
    base = Path(root) / "data" / "processed"
    required = ["cohort", "treatment_sequences", "treatment_line_summary", "validation_results", "missingness_profile", "feature_importance", "explainability", "cox_results", "km_summary", "model_curves"]
    data: dict[str, object] = {name: pd.read_csv(base / f"{name}.csv") for name in required}
    data["metrics"] = json.loads((base / "model_metrics.json").read_text(encoding="utf-8"))
    data["survival_tests"] = json.loads((base / "survival_tests.json").read_text(encoding="utf-8"))
    return data


def apply_filters(cohort: pd.DataFrame, cancer: list[str], stage: list[str], sex: list[str], region: list[str]) -> pd.DataFrame:
    frame = cohort.copy()
    for column, selected in [("cancer_type", cancer), ("stage", stage), ("sex", sex), ("region", region)]:
        if selected:
            frame = frame[frame[column].isin(selected)]
    return frame


def _bar(frame: pd.DataFrame, x: str, y: str, title: str, horizontal: bool = False):
    fig = px.bar(frame, x=y if horizontal else x, y=x if horizontal else y, orientation="h" if horizontal else "v", title=title, color_discrete_sequence=[COLORS[0]])
    fig.update_layout(margin=dict(l=10, r=10, t=55, b=10), height=390)
    return fig


def page_overview(frame: pd.DataFrame) -> None:
    st.header("Overview")
    if frame.empty:
        st.warning("No patients match the selected filters."); return
    values = [len(frame), frame.treatment_event_count.sum(), f"{100*frame.responder.mean():.1f}%", f"{100*frame.progression_event.mean():.1f}%", f"{frame.survival_days.median():,.0f} d", f"${frame.total_cost_usd.mean():,.0f}"]
    labels = ["Patients", "Treatment events", "Response rate", "Progression rate", "Median follow-up", "Mean cost"]
    for start in (0, 3):
        cols = st.columns(3)
        for col, label, value in zip(cols, labels[start:start + 3], values[start:start + 3]):
            col.metric(label, value)
    left, right = st.columns(2)
    cancer = frame.cancer_type.value_counts().rename_axis("Cancer type").reset_index(name="Patients")
    stage = frame.stage.value_counts().reindex(["I", "II", "III", "IV"]).dropna().rename_axis("Stage").reset_index(name="Patients")
    left.plotly_chart(_bar(cancer, "Cancer type", "Patients", "Cohort by cancer type", True), use_container_width=True)
    right.plotly_chart(_bar(stage, "Stage", "Patients", "Cohort by synthetic stage"), use_container_width=True)


def page_cohort(frame: pd.DataFrame) -> None:
    st.header("Cohort demographics and disease")
    if frame.empty: st.warning("No matching patients."); return
    c1, c2 = st.columns(2)
    c1.plotly_chart(px.histogram(frame, x="age_at_diagnosis", nbins=20, title="Age at diagnosis", color_discrete_sequence=[COLORS[0]]), use_container_width=True)
    sex = frame.sex.value_counts().rename_axis("Sex").reset_index(name="Patients")
    c2.plotly_chart(px.bar(sex, x="Sex", y="Patients", title="Sex distribution", color_discrete_sequence=[COLORS[1]]), use_container_width=True)
    cross = pd.crosstab(frame.cancer_type, frame.stage).reindex(columns=["I", "II", "III", "IV"], fill_value=0)
    st.plotly_chart(px.bar(cross, barmode="stack", title="Stage composition by cancer type", color_discrete_sequence=COLORS), use_container_width=True)
    st.dataframe(frame[["age_at_diagnosis", "ecog_status", "comorbidity_count", "outpatient_visits", "inpatient_admissions", "total_cost_usd"]].describe().T, use_container_width=True)


def page_pathways(frame: pd.DataFrame, sequences: pd.DataFrame, lines: pd.DataFrame) -> None:
    st.header("Treatment pathways")
    ids = set(frame.patient_id)
    seq = sequences[sequences.patient_id.isin(ids)]
    top = seq.treatment_sequence.value_counts().head(12).sort_values().rename_axis("Sequence").reset_index(name="Patients")
    st.plotly_chart(_bar(top, "Sequence", "Patients", "Most frequent ordered treatment-class sequences", True), use_container_width=True)
    c1, c2 = st.columns(2)
    by_class = frame.first_treatment_class.value_counts().rename_axis("Class").reset_index(name="Patients")
    c1.plotly_chart(px.bar(by_class, x="Class", y="Patients", title="First treatment class", color_discrete_sequence=[COLORS[0]]), use_container_width=True)
    c2.plotly_chart(px.histogram(seq, x="line_count", title="Number of treatment lines", color_discrete_sequence=[COLORS[1]]), use_container_width=True)
    st.caption("Durations and lines are synthetic pathway descriptors and are not treatment recommendations.")


def page_outcomes(frame: pd.DataFrame) -> None:
    st.header("Response and progression")
    if frame.empty: st.warning("No matching patients."); return
    c1, c2 = st.columns(2)
    response = frame.response_category.value_counts().rename_axis("Response").reset_index(name="Patients")
    c1.plotly_chart(_bar(response, "Response", "Patients", "Response categories", True), use_container_width=True)
    stage = frame.groupby("stage", observed=True).agg(response_rate=("responder", "mean"), progression_rate=("progression_event", "mean")).mul(100).reset_index()
    melted = stage.melt("stage", var_name="Outcome", value_name="Percent")
    c2.plotly_chart(px.bar(melted, x="stage", y="Percent", color="Outcome", barmode="group", title="Outcomes by stage", color_discrete_sequence=COLORS), use_container_width=True)


def page_survival(frame: pd.DataFrame) -> None:
    st.header("Kaplan–Meier survival")
    if frame.empty: st.warning("No matching patients."); return
    group = st.selectbox("Curve grouping", ["stage", "cancer_type", "sex", "first_treatment_class", "None"])
    curve = km_for_subset(frame, None if group == "None" else group)
    fig = px.line(curve, x="timeline_days", y="survival_probability", color="group", line_shape="hv", title="Time from diagnosis to synthetic mortality event", color_discrete_sequence=COLORS)
    fig.update_yaxes(range=[0, 1.02], tickformat=".0%")
    st.plotly_chart(fig, use_container_width=True)
    times = [0, 365, 730, 1095, 1460]
    risk = pd.DataFrame({"Day": times, "At risk": [int((frame.survival_days >= t).sum()) for t in times]})
    st.dataframe(risk, hide_index=True, use_container_width=True)
    st.caption("Kaplan–Meier curves are descriptive. Group differences may reflect confounding and constructed synthetic dependencies.")


def page_modeling(data: dict[str, object]) -> None:
    st.header("Predictive modeling")
    metrics = data["metrics"]["models"]
    table = pd.DataFrame(metrics).T.drop(columns="confusion_matrix").reset_index(names="model")
    st.dataframe(table.style.format(precision=3), hide_index=True, use_container_width=True)
    curves = data["model_curves"]
    c1, c2 = st.columns(2)
    for col, kind in zip([c1, c2], ["ROC", "PR"]):
        f = curves[curves.curve == kind]
        col.plotly_chart(px.line(f, x="x", y="y", color="model", title=f"Held-out {kind} curves", color_discrete_sequence=COLORS), use_container_width=True)
    selected = st.selectbox("Confusion matrix model", list(metrics))
    cm = np.asarray(metrics[selected]["confusion_matrix"])
    st.plotly_chart(px.imshow(cm, text_auto=True, x=["Predicted no", "Predicted yes"], y=["Observed no", "Observed yes"], title=f"{selected.replace('_',' ').title()} confusion matrix", color_continuous_scale="Blues"), use_container_width=True)
    st.caption("Target: binary response. Inputs are restricted to diagnosis, baseline comorbidity, and first-treatment features available before outcome assessment.")


def page_explainability(data: dict[str, object]) -> None:
    st.header("Model explainability")
    exp = data["explainability"].head(15).sort_values("mean_absolute_contribution")
    st.plotly_chart(px.bar(exp, x="mean_absolute_contribution", y="feature", orientation="h", title="Global mean absolute model contribution", color_discrete_sequence=[COLORS[0]]), use_container_width=True)
    fi = data["feature_importance"].head(15).sort_values("importance")
    st.plotly_chart(px.bar(fi, x="importance", y="feature", orientation="h", title="Random forest impurity importance", color_discrete_sequence=[COLORS[1]]), use_container_width=True)
    st.info(f"Explainability method: {data['metrics']['explainability_method']}. Importance indicates model influence, not clinical importance or causality.")


def page_quality(data: dict[str, object]) -> None:
    st.header("Data quality")
    validation = data["validation_results"]
    c1, c2, c3 = st.columns(3)
    c1.metric("Rules", len(validation)); c2.metric("Passed", int((validation.status == "pass").sum())); c3.metric("Failed", int((validation.status == "fail").sum()))
    st.dataframe(validation, hide_index=True, use_container_width=True)
    missing = data["missingness_profile"]
    missing = missing[missing.missing_count > 0]
    if not missing.empty:
        st.plotly_chart(px.bar(missing, x="missing_percent", y=missing.table + "." + missing.column, orientation="h", title="Missingness by field", color_discrete_sequence=[COLORS[4]]), use_container_width=True)
    st.caption("Selected optional fields contain intentional missing values to exercise realistic handling. Required-key and integrity checks must pass.")


def main() -> None:
    st.set_page_config(page_title="Oncology Outcomes Analytics", page_icon="◉", layout="wide")
    st.title("Oncology Patient Outcomes & Treatment Pathway Analytics")
    st.caption("Portfolio demonstration using deterministic synthetic data only — not clinical decision support")
    try:
        data = load_data()
    except FileNotFoundError:
        st.error("Generated outputs were not found. Run `python -m oncology_platform.pipeline` first."); st.stop()
    cohort = data["cohort"]
    with st.sidebar:
        st.header("Cohort filters")
        cancer = st.multiselect("Cancer type", sorted(cohort.cancer_type.unique()))
        stage = st.multiselect("Stage", ["I", "II", "III", "IV"])
        sex = st.multiselect("Sex", sorted(cohort.sex.unique()))
        region = st.multiselect("Region", sorted(cohort.region.unique()))
        page = st.radio("Section", ["Overview", "Cohort", "Treatment Pathways", "Outcomes", "Survival", "Predictive Modeling", "Explainability", "Data Quality"])
    frame = apply_filters(cohort, cancer, stage, sex, region)
    pages = {
        "Overview": lambda: page_overview(frame), "Cohort": lambda: page_cohort(frame),
        "Treatment Pathways": lambda: page_pathways(frame, data["treatment_sequences"], data["treatment_line_summary"]),
        "Outcomes": lambda: page_outcomes(frame), "Survival": lambda: page_survival(frame),
        "Predictive Modeling": lambda: page_modeling(data), "Explainability": lambda: page_explainability(data),
        "Data Quality": lambda: page_quality(data),
    }
    pages[page]()
    st.divider(); st.caption("All observations, events, costs, and associations are synthetic. No real patients or protected health information are included.")


if __name__ == "__main__":
    main()
