from __future__ import annotations

import sqlite3
from pathlib import Path

import pandas as pd

from .config import Settings


TABLE_ORDER = ["patients", "diagnoses", "treatments", "treatment_events", "outcomes", "comorbidities", "utilization"]


def connect(path: Path) -> sqlite3.Connection:
    connection = sqlite3.connect(path)
    connection.execute("PRAGMA foreign_keys = ON")
    return connection


def build_database(tables: dict[str, pd.DataFrame], settings: Settings = Settings()) -> None:
    settings.ensure_directories()
    if settings.database_path.exists():
        settings.database_path.unlink()
    schema = (settings.root / "sql" / "00_schema.sql").read_text(encoding="utf-8")
    with connect(settings.database_path) as connection:
        connection.executescript(schema)
        for table in TABLE_ORDER:
            tables[table].to_sql(table, connection, if_exists="append", index=False)
        connection.execute("INSERT INTO metadata VALUES (?, ?, ?)", ("synthetic_data", "true", "All records are deterministic synthetic data; no PHI."))


def build_marts(settings: Settings = Settings()) -> dict[str, pd.DataFrame]:
    outputs: dict[str, pd.DataFrame] = {}
    with connect(settings.database_path) as connection:
        for sql_path in sorted((settings.root / "sql").glob("[1-9][0-9]_*.sql")):
            name = sql_path.stem.split("_", 1)[1]
            frame = pd.read_sql_query(sql_path.read_text(encoding="utf-8"), connection)
            frame.to_sql(f"mart_{name}", connection, if_exists="replace", index=False)
            frame.to_csv(settings.processed_dir / f"{name}.csv", index=False)
            outputs[name] = frame
    return outputs

