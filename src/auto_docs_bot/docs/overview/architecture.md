# Auto Docs Bot — Architecture

## System overview
The service exposes a FastAPI webhook that authenticates GitHub events, translates qualifying `/docs` commands into agent jobs, and pushes resulting documentation patches through GitHubKit.

```mermaid
flowchart LR
    github[GitHub Webhook] --> app[FastAPI create_app]
    app --> handler[WebhookHandler]
    handler --> queue[BackgroundTasks]
    queue --> runner[AgentRunner]
    runner --> gh[GitHubAPI]
    gh --> prs[GitHub Pull Requests]
```
Updated: 2025-02-14

## Agent orchestration
AgentRunner retrieves pull-request context, invokes the configured strategy, and writes files back via GitHub.

```mermaid
flowchart LR
    context[Pull Request context] --> summarise[AgentContext]
    summarise --> strategy[AgentStrategy]
    strategy --> artifacts[AgentArtifacts]
    artifacts --> apply[Runner apply_changes]
    apply --> files[Markdown updates]
```
Updated: 2025-02-14

## Slash command sequence

```mermaid
flowchart LR
    commenter[Comment with /docs] --> webhook[WebhookHandler.validate]
    webhook --> reactionEyes[Add 👀 reaction]
    reactionEyes --> runner[AgentRunner.run]
    runner --> branch[ensure_branch]
    branch --> commit[upsert_files]
    commit --> pr[create_pull_request]
    pr --> reactionHooray[Add 🎉 reaction]
```
Updated: 2025-02-14
