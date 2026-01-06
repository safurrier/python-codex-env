# Auto-docs Bot

The auto-docs bot is a GitHub App service that automates documentation updates for pull
requests by orchestrating a Claude Agent SDK worker with BAML-backed authoring prompts.

## Workflow overview

1. **Trigger** – A pull request labelled `docs:auto` receives a slash command comment such
   as `/docs update fix the API docs`. The webhook service reacts with 👀 and schedules a
   job.
2. **Context gathering** – The worker fetches pull request metadata, changed files, and
   generates repository insights without a static schema. Those insights seed the BAML
   prompts.
3. **Patch generation** – Depending on the mode, the worker invokes one of the BAML
   functions (`write_quickstart`, `update_from_diff`, or `deep_update`) to obtain Markdown
   patches, which are validated to ensure only documentation files are touched.
4. **Commit & PR** – The bot creates a branch named `auto-docs/<head>-<timestamp>` from
   the PR head, commits the patches via the GitHub Contents API, and opens a companion PR
   targeting the original base branch.
5. **Reporting** – After completion, the bot reacts with 🎉 on the triggering comment and
   posts the companion PR link. If no documentation changes were necessary it instead
   posts a no-op message.

## Implementation details

- **Webhook service** – Implemented with FastAPI (or the provided fallback stubs for unit
  tests). Webhooks are verified via `X-Hub-Signature-256` before dispatching actions.
- **GitHub integration** – `GitHubApp` exchanges installation tokens with JWTs generated
  from the app's private key, while `GitHubAPI` wraps REST endpoints for reactions,
  comments, refs, contents, and pull requests.
- **Agent runner** – `AgentRunner` coordinates the Claude agent, repository intelligence
  collection, patch validation, and PR authoring. It enforces Markdown-only edits.
- **BAML orchestration** – `DocAuthoringService` provides a small bridge to the generated
  BAML client, normalising patches and surfacing clear error messages when the client is
  missing.
- **Testing** – Unit tests exercise command parsing, branch naming, repo insight
  generation, and webhook flows using fakes so that external dependencies remain
  optional.

Environment variables control runtime behaviour and credentials (`GITHUB_APP_ID`,
`GITHUB_PRIVATE_KEY`, `CLAUDE_API_KEY`, `BAML_ENV`, etc.). For local development, you can
instantiate the FastAPI app via `auto_docs_bot.create_app()` after ensuring the BAML
client has been generated.
