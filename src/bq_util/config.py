"""Configuration management for the bq_util CLI."""

from __future__ import annotations

import json
import os
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any

APP_NAME = "bq_util"
CONFIG_FILENAME = "config.json"


@dataclass()
class Config:
    """Simple container for persisted configuration values."""

    default_project: str | None = None
    last_job_id: str | None = None
    last_job_project: str | None = None

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> Config:
        """Create a :class:`Config` instance from persisted JSON data."""

        return cls(
            default_project=data.get("default_project"),
            last_job_id=data.get("last_job_id"),
            last_job_project=data.get("last_job_project"),
        )

    def to_dict(self) -> dict[str, Any]:
        """Serialise the configuration to a JSON compatible dictionary."""

        return asdict(self)


def get_config_dir() -> Path:
    """Return the directory used to store configuration files."""

    base = os.environ.get("XDG_CONFIG_HOME")
    base_path = Path(base).expanduser() if base else Path.home() / ".config"
    return base_path / APP_NAME


def get_config_path() -> Path:
    """Return the location of the configuration file."""

    return get_config_dir() / CONFIG_FILENAME


def load_config(path: Path | None = None) -> Config:
    """Load configuration from ``path`` or return defaults if missing."""

    config_path = path or get_config_path()
    if not config_path.exists():
        return Config()

    try:
        raw_data = json.loads(config_path.read_text())
    except Exception:
        return Config()

    return Config.from_dict(raw_data)


def save_config(config: Config, path: Path | None = None) -> None:
    """Persist the provided configuration to disk."""

    config_path = path or get_config_path()
    config_path.parent.mkdir(parents=True, exist_ok=True)
    config_path.write_text(json.dumps(config.to_dict(), indent=2))
