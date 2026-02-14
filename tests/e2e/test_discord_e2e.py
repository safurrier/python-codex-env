from __future__ import annotations

import os
import uuid

import pytest
from click.testing import CliRunner

from discord_reader.client import DiscordClient
from dread.cli import cli

pytestmark = pytest.mark.e2e


def _require_env(name: str) -> str:
    value = os.getenv(name)
    if not value:
        pytest.skip(f"Missing {name}")
    return value


def _seed(channel_id: str, text: str) -> str:
    token = _require_env("DREAD_TEST_DISCORD_TOKEN")
    client = DiscordClient(token)
    created = client.post(f"channels/{channel_id}/messages", json={"content": text})
    return created["id"]


def test_t1_guild_ls_contains_test_guild(monkeypatch) -> None:
    token = _require_env("DREAD_TEST_DISCORD_TOKEN")
    guild_id = _require_env("DREAD_TEST_GUILD_ID")
    monkeypatch.setenv("DISCORD_TOKEN", token)
    result = CliRunner().invoke(cli, ["guild", "ls", "--json"])
    assert result.exit_code == 0
    assert guild_id in result.output


def test_t3_msg_ls_returns_seeded_message(monkeypatch) -> None:
    token = _require_env("DREAD_TEST_DISCORD_TOKEN")
    channel_id = _require_env("DREAD_TEST_CHANNEL_ID")
    marker = f"hello-from-e2e-{uuid.uuid4()}"
    _seed(channel_id, marker)
    monkeypatch.setenv("DISCORD_TOKEN", token)
    result = CliRunner().invoke(
        cli, ["msg", "ls", channel_id, "--limit", "10", "--json"]
    )
    assert result.exit_code == 0
    assert marker in result.output
