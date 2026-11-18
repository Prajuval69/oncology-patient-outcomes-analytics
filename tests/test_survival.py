import pandas as pd

from oncology_platform.survival import km_for_subset


def test_all_censored_and_single_category_survival():
    frame = pd.DataFrame({"survival_days": [20, 40, 80], "death_event": [0, 0, 0], "stage": ["II", "II", "II"]})
    curve = km_for_subset(frame, "stage")
    assert curve.survival_probability.eq(1.0).all()
    assert curve.group.nunique() == 1


def test_empty_survival_subset():
    frame = pd.DataFrame(columns=["survival_days", "death_event", "stage"])
    assert km_for_subset(frame, "stage").empty

