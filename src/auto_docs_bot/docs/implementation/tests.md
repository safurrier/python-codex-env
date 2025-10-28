# Tests

## Test suite
- `tests/test_auto_docs_bot.py` covers command parsing, webhook validation, agent runner behaviour, and GitHub interactions via fixtures.
- `tests/test_docs_setup.py` ensures documentation build wiring remains optional when dependencies such as PyYAML are unavailable.

## Running tests
```bash
uv run pytest tests/test_auto_docs_bot.py
```
This command exercises the module-specific tests while keeping runtime under a minute.

## Fixtures and patterns
- **`githubkit_mock`** — Simulates installation tokens and REST calls without network access.
- **`agent_strategy_stub`** — Provides deterministic patches for runner assertions.
- **`background_tasks`** — Uses FastAPI `BackgroundTasks` to validate webhook scheduling.

## Conventions
- Each new interface should ship with a focused test covering success and failure cases.
- Avoid mocking the strategies in unit tests that target GitHub plumbing; instead, use small `DocPatch` payloads to observe branch and PR operations.
