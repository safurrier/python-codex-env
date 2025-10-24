# Auto-docs Bot

The auto-docs bot is a GitHub App service that automates documentation updates for pull
requests by orchestrating a pluggable agent worker with BAML-backed authoring prompts.

## Workflow overview

1. **Trigger** – A pull request labelled `docs:auto` receives a slash command comment such
   as `/docs update fix the API docs`. The webhook service reacts with 👀 and schedules a
   job.
2. **Context gathering** – The worker fetches pull request metadata and changed files,
   then distils lightweight summaries (touched code/doc paths, diff snippets, notable
   findings) that seed the BAML prompts without cloning the repository.
3. **Patch generation** – Depending on the mode, the selected strategy invokes either the
   Claude Code + BAML authoring flow or an external Codex CLI to obtain Markdown patches,
   which are validated to ensure only documentation files are touched.
4. **Commit & PR** – The bot creates a branch named `auto-docs/<head>-<timestamp>` from
   the PR head, commits the patches via the GitHub Contents API, and opens a companion PR
   targeting the original base branch.
5. **Reporting** – After completion, the bot reacts with 🎉 on the triggering comment and
   posts the companion PR link. If no documentation changes were necessary it instead
   posts a no-op message.

## Implementation details

- **Webhook service** – Implemented with FastAPI. Webhooks are verified via
  `X-Hub-Signature-256` before dispatching actions.
- **GitHub integration** – `GitHubApp` exchanges installation tokens with JWTs generated
  from the app's private key, while `GitHubClient` (built on `githubkit`) handles
  reactions, comments, refs, contents, and pull requests.
- **Agent runner** – `AgentRunner` coordinates the selected agent strategy, summarises
  pull request files for the prompts, validates patches, and authors the companion PR.
- **Agent strategies** – `ClaudeCodeAgentStrategy` uses the Claude Agent SDK with BAML
  prompts, while `CodexCliAgentStrategy` shells out to a Codex CLI. Both produce patches
  alongside PR titles/bodies so that GitHub updates remain strategy-agnostic.
- **BAML orchestration** – `DocAuthoringService` provides a small bridge to the generated
  BAML client, normalising patches and surfacing clear error messages when the client is
  missing.
- **Testing** – Unit tests exercise command parsing, branch naming, payload summarising,
  and webhook flows using fakes so that external dependencies remain optional.

Environment variables control runtime behaviour and credentials (`GITHUB_APP_ID`,
`GITHUB_PRIVATE_KEY`, `CLAUDE_API_KEY`, `BAML_ENV`, etc.). `AUTO_DOCS_AGENT_BACKEND`
switches between the `claude` (default) and `codex` strategies, and `CODEX_CLI_PATH`
customises the Codex executable path. For local development, you can instantiate the
FastAPI app via `auto_docs_bot.create_app()` after ensuring the BAML client has been
generated.
