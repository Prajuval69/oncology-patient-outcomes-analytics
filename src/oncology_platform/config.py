from dataclasses import dataclass
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]


@dataclass(frozen=True)
class Settings:
    root: Path = ROOT
    seed: int = 20260923
    n_patients: int = 1500

    @property
    def raw_dir(self) -> Path:
        return self.root / "data" / "raw"

    @property
    def processed_dir(self) -> Path:
        return self.root / "data" / "processed"

    @property
    def artifact_dir(self) -> Path:
        return self.root / "artifacts"

    @property
    def database_path(self) -> Path:
        return self.root / "data" / "oncology.db"

    def ensure_directories(self) -> None:
        for path in (
            self.raw_dir,
            self.processed_dir,
            self.artifact_dir / "charts",
            self.artifact_dir / "models",
            self.root / "reports",
        ):
            path.mkdir(parents=True, exist_ok=True)

