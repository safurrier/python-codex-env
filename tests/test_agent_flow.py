from __future__ import annotations

from pathlib import Path

from obsidian_srs_agent.app.agent import ObsidianSRSAgent, PipelineConfig


def test_agent_generate_and_write(tmp_path):
    agent = ObsidianSRSAgent()
    config = PipelineConfig(
        vault_path=str(tmp_path),
        domain="science",
        topic="memory",
        raw_text="Spaced repetition improves memory retention. Use flashcards regularly.",
        num_cards=2,
    )

    preview = agent.generate(config)
    assert preview.cards
    assert len(preview.cards) <= config.num_cards

    result = agent.write(preview, config)
    written_path = Path(result.path)
    assert written_path.exists()
    assert written_path.read_text(encoding="utf-8").count("::") >= 1
