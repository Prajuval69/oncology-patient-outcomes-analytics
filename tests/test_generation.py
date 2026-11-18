import pandas as pd
import pytest

from oncology_platform.generate_data import generate_synthetic_data


def test_generation_is_deterministic_and_complete():
    first = generate_synthetic_data(80, 42)
    second = generate_synthetic_data(80, 42)
    assert set(first) == {"patients", "diagnoses", "treatments", "treatment_events", "outcomes", "comorbidities", "utilization"}
    pd.testing.assert_frame_equal(first["patients"], second["patients"])
    pd.testing.assert_frame_equal(first["outcomes"], second["outcomes"])
    assert len(first["patients"]) == 80
    assert first["patients"].synthetic_record.eq(1).all()


def test_generation_rejects_empty_cohort():
    with pytest.raises(ValueError):
        generate_synthetic_data(0, 42)


def test_dates_and_line_derivation_are_valid():
    tables = generate_synthetic_data(120, 7)
    dx = pd.to_datetime(tables["diagnoses"].set_index("patient_id").diagnosis_date)
    events = tables["treatment_events"]
    assert (events.patient_id.map(dx) <= pd.to_datetime(events.treatment_start_date)).all()
    assert (pd.to_datetime(events.treatment_start_date) <= pd.to_datetime(events.treatment_end_date)).all()
    for _, group in events.groupby("patient_id"):
        assert sorted(group.treatment_line.tolist()) == list(range(1, len(group) + 1))

