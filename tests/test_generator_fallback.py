from __future__ import annotations

from obsidian_srs_agent.app.baml_client import CardGenerator
from obsidian_srs_agent.app.models import CardGenControls, SourceDoc


def test_fallback_generator_produces_cards_when_baml_missing():
    generator = CardGenerator()
    doc = SourceDoc(text="AI helps humans. AI augments abilities.")
    controls = CardGenControls(num_cards=2, style="basic")

    result = generator.generate(doc=doc, controls=controls, fallback=True)

    assert result.cards
    assert all(card.front for card in result.cards)

