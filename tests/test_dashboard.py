import importlib.util
from pathlib import Path

import pandas as pd


def _load_dashboard():
    path = Path(__file__).resolve().parents[1] / "dashboard" / "app.py"
    spec = importlib.util.spec_from_file_location("oncology_dashboard", path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_dashboard_imports_and_filters():
    app = _load_dashboard()
    frame = pd.DataFrame({"cancer_type": ["Lung", "Breast"], "stage": ["IV", "II"], "sex": ["Male", "Female"], "region": ["South", "West"]})
    result = app.apply_filters(frame, ["Lung"], [], [], [])
    assert len(result) == 1

