from dataclasses import replace

import pandas as pd

from oncology_platform.config import Settings
from oncology_platform.database import build_database, build_marts, connect
from oncology_platform.generate_data import generate_synthetic_data


def test_database_schema_and_sql_marts(tmp_path):
    settings = replace(Settings(), root=tmp_path, n_patients=90, seed=8)
    (tmp_path / "sql").mkdir()
    source_sql = Settings().root / "sql"
    for path in source_sql.glob("*.sql"):
        (tmp_path / "sql" / path.name).write_text(path.read_text(encoding="utf-8"), encoding="utf-8")
    settings.ensure_directories()
    tables = generate_synthetic_data(90, 8)
    build_database(tables, settings)
    marts = build_marts(settings)
    assert len(marts["cohort"]) == 90
    assert marts["cohort"].patient_id.is_unique
    assert int(marts["kpis"].iloc[0].patients) == 90
    assert set(marts["survival_input"].death_event.unique()) <= {0, 1}
    assert marts["data_quality_checks"].failures.sum() == 0
    with connect(settings.database_path) as connection:
        assert pd.read_sql_query("SELECT COUNT(*) n FROM treatment_events", connection).iloc[0].n == len(tables["treatment_events"])

