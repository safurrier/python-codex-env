from __future__ import annotations

from obsidian_srs_agent.app.models import SourceDoc
from obsidian_srs_agent.app.tools import chunk_document


def test_chunking_respects_overlap():
    text = "A" * 9000
    doc = SourceDoc(text=text)

    chunks = chunk_document(doc)

    assert len(chunks) == 2
    assert chunks[0].text.endswith("A" * 500)
    assert chunks[1].text.startswith("A" * 500)

