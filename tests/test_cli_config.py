"""Tests for the configuration command of the bq-util CLI."""

from __future__ import annotations

import json
from pathlib import Path

from click.testing import CliRunner

from bq_util.cli import cli


def _read_config(base_dir: Path) -> dict[str, object | None]:
    config_file = base_dir / "bq_util" / "config.json"
    assert config_file.exists(), "expected configuration file to be written"
    return json.loads(config_file.read_text())


def test_config_show_initialises_file(tmp_path, monkeypatch):
    """Showing the config should create a config file with defaults."""

    monkeypatch.setenv("XDG_CONFIG_HOME", str(tmp_path))
    runner = CliRunner()

    result = runner.invoke(cli, ["config", "--show"])

    assert result.exit_code == 0, result.output
    config = _read_config(tmp_path)
    assert config == {
        "default_project": None,
        "last_job_id": None,
        "last_job_project": None,
    }


def test_config_set_project_persists(tmp_path, monkeypatch):
    """Setting the default project should persist to the config file."""

    monkeypatch.setenv("XDG_CONFIG_HOME", str(tmp_path))
    runner = CliRunner()

    result = runner.invoke(cli, ["config", "--set-project", "demo-project"])

    assert result.exit_code == 0, result.output
    config = _read_config(tmp_path)
    assert config["default_project"] == "demo-project"
