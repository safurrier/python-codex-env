"""Tests for the analyze command in the bq-util CLI."""

from __future__ import annotations

import json
from datetime import datetime, timedelta, timezone
from typing import Any

from click.testing import CliRunner

import bq_util.cli as cli_module


class FakeJob:
    """A tiny subset of the QueryJob interface used in the CLI."""

    def __init__(self) -> None:
        now = datetime.now(timezone.utc)
        self.job_id = "recent-job"
        self.project = "demo-project"
        self.location = "us-central1"
        self.created = now - timedelta(minutes=5)
        self.started = self.created
        self.ended = now
        self.state = "DONE"
        self.error_result = None
        self.user_email = "user@example.com"
        self.job_type = "query"
        self.query = "SELECT 1"
        self.total_bytes_processed = 100
        self.total_bytes_billed = 100
        self.slot_millis = 1000
        self.billing_tier = None
        self.cache_hit = False
        self.destination = None
        self.query_plan: list[Any] = []
        self.referenced_tables: list[Any] = []


class FakeClient:
    def __init__(self, job: FakeJob) -> None:
        self._job = job

    def get_job(self, job_id: str, project: str | None = None) -> FakeJob:
        assert job_id == self._job.job_id
        assert project == self._job.project
        return self._job


def test_analyze_uses_last_job_from_config(monkeypatch, tmp_path):
    monkeypatch.setenv("XDG_CONFIG_HOME", str(tmp_path))

    config_dir = tmp_path / "bq_util"
    config_dir.mkdir()
    (config_dir / "config.json").write_text(
        json.dumps(
            {
                "default_project": None,
                "last_job_id": "recent-job",
                "last_job_project": "demo-project",
            }
        )
    )

    fake_job = FakeJob()
    monkeypatch.setattr(
        cli_module, "get_bigquery_client", lambda project=None: FakeClient(fake_job)
    )

    runner = CliRunner()
    result = runner.invoke(cli_module.cli, ["analyze", "--last", "--format", "json"])

    assert result.exit_code == 0, result.output
    assert "recent-job" in result.output
