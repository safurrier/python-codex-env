# Discord API research notes (safe implementation)

Date: 2026-02-14

## Scope

Validated implementation against Discord Developer Docs patterns for **bot-token REST clients**:
- API base versioning (`/api/v10`)
- bot auth header format (`Authorization: Bot <token>`)
- route families for guild/channel/message primitives
- message history pagination primitives (`limit`, `before`, `after`)
- reaction route shape
- search retry behavior support in this codebase (`202 retry_after`, `429 Retry-After`)

## Important security/compliance note

This project does **not** implement user-token/self-bot/modded-client authentication.
Using user tokens for automated clients is out of scope here and intentionally unsupported.

## Verification output mapping

- Wrapper route and payload correctness is asserted via unit tests in `tests/test_routes_contract.py`.
- Retry/rate-limit and index-not-ready handling is asserted in `tests/test_client.py`.
- Mentions search/fallback strategy behavior is asserted in `tests/test_search_mentions.py`.
- Env-gated live-contract checks are in `tests/e2e/test_discord_e2e.py`.
