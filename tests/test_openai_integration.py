from __future__ import annotations

import os

import pytest

from obsidian_srs_agent.app.baml_client import CardGenerator
from obsidian_srs_agent.app.models import CardGenControls, SourceDoc


@pytest.mark.network
def test_openai_generation_smoke():
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        pytest.skip("OPENAI_API_KEY not set")

    generator = CardGenerator()
    doc = SourceDoc(text="Spaced repetition helps retain information over time.")
    controls = CardGenControls(num_cards=1, style="basic")

    try:
        result = generator.generate(doc=doc, controls=controls)
    except RuntimeError as exc:
        pytest.skip(f"OpenAI generation failed: {exc}")

    assert result.cards
    assert result.model != "heuristic"
