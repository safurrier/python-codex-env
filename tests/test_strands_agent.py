from __future__ import annotations

import pytest

from obsidian_srs_agent.app.agent import ObsidianSRSAgent

strands = pytest.importorskip("strands")


def test_create_strands_agent_registers_tools(monkeypatch):
    monkeypatch.delenv("SR_STRANDS_MODEL", raising=False)
    agent = ObsidianSRSAgent()

    strands_agent = agent.create_strands_agent(model=None)
    tool_names = set(strands_agent.tool_names)
    assert {"fetch_and_extract", "generate_cards", "write_obsidian"}.issubset(
        tool_names
    )
