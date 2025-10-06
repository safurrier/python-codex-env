"""CLI entry point for the Obsidian SRS agent."""
from __future__ import annotations

import argparse
import logging
from typing import Optional

from .agent import ObsidianSRSAgent, PipelineConfig

LOGGER = logging.getLogger(__name__)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Generate Obsidian SR decks from content")
    parser.add_argument("--vault", required=True, help="Path to the Obsidian vault root")
    parser.add_argument("--domain", required=True, help="Domain name for the deck")
    parser.add_argument("--topic", required=True, help="Topic name for the deck")
    parser.add_argument("--url", help="URL to fetch via Jina Reader")
    parser.add_argument("--text", help="Raw text to process if URL is not provided")
    parser.add_argument("--num_cards", type=int, default=10, help="Number of cards to request")
    parser.add_argument("--difficulty", choices=["easy", "medium", "hard"], help="Card difficulty")
    parser.add_argument("--focus_area", help="Focus area tag to include on cards")
    parser.add_argument("--style", choices=["basic", "reversed", "cloze"], help="Card style")
    parser.add_argument("--force-baml", action="store_true", help="Require BAML instead of fallback")
    parser.add_argument("--file", help="Optional file basename override")
    return parser


def main(argv: Optional[list[str]] = None) -> int:
    logging.basicConfig(level=logging.INFO)
    parser = build_parser()
    args = parser.parse_args(argv)

    if not args.url and not args.text:
        parser.error("Provide either --url or --text")

    config = PipelineConfig(
        vault_path=args.vault,
        domain=args.domain,
        topic=args.topic,
        url=args.url,
        raw_text=args.text,
        num_cards=args.num_cards,
        difficulty=args.difficulty,
        focus_area=args.focus_area,
        style=args.style,
        file_basename=args.file,
        force_baml=args.force_baml,
    )

    agent = ObsidianSRSAgent()
    preview = agent.generate(config)
    LOGGER.info("Generated %s candidate cards", len(preview.cards))
    result = agent.write(preview, config)
    LOGGER.info("Deck written to %s", result.path)
    return 0


if __name__ == "__main__":  # pragma: no cover
    raise SystemExit(main())

