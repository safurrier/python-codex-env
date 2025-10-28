# Onboarding Exercises

1. Trigger the workflow locally by crafting a sample pull request payload and posting an issue comment event to `/github/webhook`; observe the 👀 reaction request in the logs.
2. Swap `AUTO_DOCS_AGENT_BACKEND` between `claude` and `codex` in your environment and confirm `AgentRunner` picks the expected strategy by reading startup logs.
3. Extend `tests/test_auto_docs_bot.py` with a scenario where the Codex CLI returns multiple patches; verify the branch and PR operations still succeed.
4. Add a new command note to the webhook comment handler and ensure the GitHub comment posted by `WebhookHandler` surfaces it verbatim.
5. Inspect a generated companion PR and trace each changed file back to the originating `DocPatch` to understand validation expectations.
