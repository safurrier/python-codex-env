# Data & State

## Persistent records
The service is stateless; it relies entirely on GitHub for persistence (branches, commits, pull requests, reactions, comments).

## In-memory structures
- `AgentJobPayload` — Deserialized webhook command containing `repository`, `pr_number`, `mode`, `notes`, and the triggering `comment_id`.
- `AgentContext` — Derived summary that combines payload values with pull-request metadata (head/base refs, files) for strategy consumption.
- `DocPatch` — Validated pair of `path: Path` and `content: str` returned by each agent backend. Only `.md` and `.mdx` paths are accepted.

## External services
- **GitHub REST API** — Source of pull-request context and sink for new branches, commits, reactions, and PRs. Authentication flows through GitHub App installation tokens.
- **BAML authoring service** — For the Claude strategy, the `generate_patches(mode, payload)` call returns deterministic patch payloads for quickstart, update, and deep-update runs.
- **Codex CLI** — Optional executable invoked with JSON payloads; it must emit JSON matching the `DocPatch` schema.

## Invariants
- Strategies must return patches targeting markdown files; otherwise `validate_patches` raises and the job fails fast.
- Branch names follow `auto-docs/<head-ref>-<timestamp>` from `AgentJobPayload.branch_name`, avoiding collisions per run.
- Comments and reactions are only added when the webhook sees a valid `/docs` command with the `docs:auto` label present.
