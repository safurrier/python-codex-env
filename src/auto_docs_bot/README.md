# Auto Docs Bot

An installable GitHub App that reacts to `/docs` slash commands on pull requests and opens a companion documentation PR using a pluggable agent backend.

## Quick Start

Configure environment variables and run the webhook service locally:

```bash
uv run uvicorn auto_docs_bot.app:create_app --factory --host 0.0.0.0 --port 8000
```

Documentation
- [Tour — Quickstart walkthrough](docs/overview/tour.md)
- [Module Brief — High-level overview](docs/overview/module_brief.md)
- [Architecture — System design](docs/overview/architecture.md)
- [Interfaces — APIs and boundaries](docs/implementation/interfaces.md)
- [Data & State — Models and persistence](docs/implementation/data_state.md)
- [Tests — Testing setup](docs/implementation/tests.md)
- [Onboarding Exercises — Developer learning tasks](docs/onboarding/exercises.md)

Links
- [Reference guide](../../docs/reference/auto-docs-bot.md)
- [Project README](../../README.md)
