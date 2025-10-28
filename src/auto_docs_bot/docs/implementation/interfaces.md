# Interfaces

## Web entrypoints
- **`POST /github/webhook`** — Validates HMAC signature, parses pull request label and issue comment events, and enqueues `AgentJobPayload` for qualifying `/docs` commands.
- **`GET /healthz`** — Returns `{ "status": "ok" }` for uptime checks.

## Command parsing
- `parse_command(text: str) -> Command | None` in `commands.py` extracts `/docs <mode> [notes]` directives.
- `DocsMode` enum guards the allowed values: `quickstart`, `update`, `deep-update`.

## Agent strategies
- `ClaudeCodeAgentStrategy.generate(context)` — Uses the BAML authoring service to request patches derived from repository hints, diff snippets, or findings depending on mode.
- `CodexCliAgentStrategy.generate(context)` — Shells out to a Codex CLI executable, passing repository metadata as JSON and expecting structured patches in the response.

## GitHub integration
Implemented through `GitHubAPI` (githubkit wrapper):
- `get_pull_request(repo, number)` and `get_pull_request_files(repo, number)` collect metadata for agent context.
- `ensure_branch(repo, branch, sha)` creates or force-updates the docs branch from the pull request head.
- `upsert_files(repo, branch, message, files)` writes generated markdown content via the Contents API.
- `create_pull_request(repo, head, base, title, body)` opens the companion PR.
- Reaction helpers (`add_comment_reaction`) and comment posting support feedback loops from `WebhookHandler`.

## Background execution
- `WebhookHandler.handle(request, background_tasks)` attaches `BackgroundTasks.add_task` to invoke `AgentRunner.run` asynchronously so webhook responses stay under GitHub timeouts.
- Failures bubble up; there is no silent fallback or retry path.
