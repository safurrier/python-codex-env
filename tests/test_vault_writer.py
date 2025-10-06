from __future__ import annotations

import tempfile
from pathlib import Path

from obsidian_srs_agent.app.models import Card
from obsidian_srs_agent.app.vault import MarkdownVaultWriter


def test_vault_writer_creates_expected_structure():
    card = Card(front="What is AI?", back="Artificial Intelligence", style="basic")

    with tempfile.TemporaryDirectory() as tmpdir:
        root = Path(tmpdir)
        (root / "Decks").mkdir()
        writer = MarkdownVaultWriter(root=str(root))
        path = writer.write_cards(
            cards=[card],
            source_title="Test Doc",
            source_url="https://example.com",
            domain="example.com",
            topic="ai",
        )

        written = Path(path)
        assert written.exists()
        content = written.read_text(encoding="utf-8")
        assert "sr_deck: True" in content
        assert "#deck/example-com/ai" in content
        assert "What is AI?::Artificial Intelligence" in content
