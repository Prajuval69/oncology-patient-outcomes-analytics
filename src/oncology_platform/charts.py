from __future__ import annotations

import json

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import pandas as pd
import seaborn as sns

from .config import Settings


PALETTE = ["#2457A7", "#E09F3E", "#688E26", "#B56576", "#6C757D"]


def _save(fig: plt.Figure, name: str, settings: Settings) -> None:
    fig.tight_layout()
    fig.savefig(settings.artifact_dir / "charts" / f"{name}.png", dpi=160, bbox_inches="tight")
    plt.close(fig)


def create_charts(settings: Settings = Settings()) -> None:
    sns.set_theme(style="whitegrid", font_scale=.9)
    cohort = pd.read_csv(settings.processed_dir / "cohort.csv")
    fig, ax = plt.subplots(figsize=(8, 4.5)); order = cohort.cancer_type.value_counts().index
    sns.countplot(data=cohort, y="cancer_type", order=order, color=PALETTE[0], ax=ax); ax.set(title="Synthetic cohort by cancer type", xlabel="Patients", ylabel=""); _save(fig, "cohort_by_cancer", settings)
    seq = pd.read_csv(settings.processed_dir / "treatment_sequences.csv").treatment_sequence.value_counts().head(10).sort_values()
    fig, ax = plt.subplots(figsize=(9, 5)); ax.barh(seq.index, seq.values, color=PALETTE[1]); ax.set(title="Most common treatment-class pathways", xlabel="Patients", ylabel=""); _save(fig, "treatment_pathways", settings)
    stage = pd.read_csv(settings.processed_dir / "outcomes_by_stage.csv")
    fig, ax = plt.subplots(figsize=(7, 4)); ax.bar(stage.stage, stage.response_rate, color=PALETTE[0]); ax.set(title="Response rate by stage", xlabel="Synthetic stage", ylabel="Response rate (%)", ylim=(0, 100)); _save(fig, "response_by_stage", settings)
    km = pd.read_csv(settings.processed_dir / "km_curve.csv"); fig, ax = plt.subplots(figsize=(8, 5))
    for i, (group, frame) in enumerate(km[km.group != "Overall"].groupby("group")):
        ax.step(frame.timeline_days, frame.survival_probability, where="post", label=f"Stage {group}", color=PALETTE[i]); ax.fill_between(frame.timeline_days, frame.ci_lower, frame.ci_upper, step="post", alpha=.10, color=PALETTE[i])
    ax.set(title="Kaplan–Meier overall survival by stage", xlabel="Days from diagnosis", ylabel="Survival probability", ylim=(0, 1.02)); ax.legend(); _save(fig, "kaplan_meier_stage", settings)
    curves = pd.read_csv(settings.processed_dir / "model_curves.csv"); fig, axes = plt.subplots(1, 2, figsize=(10, 4.3))
    for ax, curve, title in zip(axes, ["ROC", "PR"], ["Held-out ROC curves", "Held-out precision–recall curves"]):
        for i, (model, frame) in enumerate(curves[curves.curve == curve].groupby("model")):
            ax.plot(frame.x, frame.y, label=model.replace("_", " ").title(), color=PALETTE[i])
        ax.set(title=title, xlabel="False positive rate" if curve == "ROC" else "Recall", ylabel="True positive rate" if curve == "ROC" else "Precision"); ax.legend()
    _save(fig, "model_curves", settings)
    fi = pd.read_csv(settings.processed_dir / "feature_importance.csv").head(12).sort_values("importance")
    fig, ax = plt.subplots(figsize=(8, 5)); ax.barh(fi.feature.str.replace("categorical__", "").str.replace("numeric__", ""), fi.importance, color=PALETTE[0]); ax.set(title="Random forest feature importance", xlabel="Mean decrease in impurity", ylabel=""); _save(fig, "feature_importance", settings)
    miss = pd.read_csv(settings.processed_dir / "missingness_profile.csv"); miss = miss[miss.missing_count > 0].sort_values("missing_percent")
    fig, ax = plt.subplots(figsize=(7, 3.5)); ax.barh(miss.table + "." + miss.column, miss.missing_percent, color=PALETTE[4]); ax.set(title="Intentional synthetic missingness", xlabel="Missing (%)", ylabel=""); _save(fig, "missingness", settings)

