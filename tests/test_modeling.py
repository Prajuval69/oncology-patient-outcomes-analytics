import numpy as np
import pandas as pd

from oncology_platform.modeling import CATEGORICAL, FEATURES, NUMERIC, _metrics, _preprocessor


def test_preprocessing_handles_missing_optional_values():
    row = {feature: 1 for feature in NUMERIC}
    row.update({feature: "value" for feature in CATEGORICAL})
    frame = pd.DataFrame([row, row])
    frame.loc[0, "ecog_status"] = np.nan
    frame.loc[0, "biomarker_status"] = None
    transformed = _preprocessor().fit_transform(frame[FEATURES])
    assert transformed.shape[0] == 2
    assert np.isfinite(transformed).all()


def test_metric_calculation_is_numerically_valid():
    metrics = _metrics(pd.Series([0, 0, 1, 1]), np.array([0.1, 0.4, 0.6, 0.9]))
    assert metrics["roc_auc"] == 1.0
    assert metrics["f1"] == 1.0

