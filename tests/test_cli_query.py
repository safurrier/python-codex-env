"""Tests for the query command in the bq-util CLI."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from click.testing import CliRunner

import bq_util.cli as cli_module


class FakeJob:
    """Minimal stub of a BigQuery job for the CLI tests."""

    job_id = "fake-job"
    job_type = "query"
    query = "SELECT 1"
    total_bytes_processed = 100
    total_bytes_billed = 100
    slot_millis = 1000
    cache_hit = False

    def __init__(self) -> None:
        self.referenced_tables: list[Any] = []

    def to_dataframe(self):  # pragma: no cover - not expected to be used
        raise AssertionError("to_dataframe should not be called in tests")


def _load_config(base_dir: Path) -> dict[str, Any]:
    config_path = base_dir / "bq_util" / "config.json"
    return json.loads(config_path.read_text())


def test_query_command_updates_config_and_runs_analysis(monkeypatch, tmp_path):
    """Executing a query should store the job id and optionally analyse it."""

    monkeypatch.setenv("XDG_CONFIG_HOME", str(tmp_path))
    runner = CliRunner()

    query_file = tmp_path / "query.sql"
    query_file.write_text("select 1;")

    fake_job = FakeJob()
    analyze_calls: list[tuple[tuple[Any, ...], dict[str, Any]]] = []

    monkeypatch.setattr(cli_module, "get_project", lambda project=None: "demo-project")
    monkeypatch.setattr(
        cli_module, "run_query", lambda query, project: (fake_job, 0.42)
    )
    monkeypatch.setattr(
        cli_module, "format_query_stats", lambda job, execution_time: "stats"
    )
    monkeypatch.setattr(
        cli_module, "get_query_results_preview", lambda job, max_rows=5: "preview"
    )

    def fake_analyze(job_id: str, project: str, **kwargs: Any) -> None:
        analyze_calls.append(((job_id, project), kwargs))

    monkeypatch.setattr(cli_module, "analyze_job", fake_analyze)

    result = runner.invoke(cli_module.cli, ["query", str(query_file), "--analyze"])

    assert result.exit_code == 0, result.output
    config = _load_config(tmp_path)
    assert config["last_job_id"] == "fake-job"
    assert analyze_calls == [(("fake-job", "demo-project"), {"verbose": False})]
