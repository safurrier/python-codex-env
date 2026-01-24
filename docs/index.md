# bq-util

Welcome to the documentation for `bq-util`, a Click-based command line
application for exploring and executing Google BigQuery workloads. The tool
wraps the BigQuery APIs with a workflow-friendly interface that remembers your
favourite projects, inspects historical jobs, and runs SQL from disk.

## Why bq-util?

- **Accelerated troubleshooting** – fetch detailed query plans, slot
  consumption, and bottleneck hints without visiting the Cloud Console.
- **Scriptable workflows** – run queries from CI or local scripts, export
  structured JSON, and chain to other tooling.
- **Stateful ergonomics** – persist default projects and analyse the last job
  you executed with a single flag.

## Quick Start

1. Install the package with the CLI extras:
   ```bash
   uv pip install -e .[cli]
   # or pip install -e .[cli]
   ```
2. Authenticate with Application Default Credentials if necessary:
   ```bash
   gcloud auth application-default login
   ```
3. Inspect a recent job:
   ```bash
   bq-util analyze --last
   ```

## Command Overview

- `bq-util config` – manage persisted defaults such as the preferred project and
  location of the config file.
- `bq-util analyze` – explore existing jobs, view execution plans, and emit
  machine-readable summaries.
- `bq-util query` – run SQL files, rewrite dbt `ref()` macros, preview results,
  and optionally trigger job analysis immediately.

Dive deeper with the [Getting Started guide](getting-started.md) or jump
straight to the [CLI walkthrough](bq-util.md) for detailed examples.
