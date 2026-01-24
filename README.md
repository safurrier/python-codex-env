# bq-util

`bq-util` is a command line companion for Google BigQuery. It turns the
original monolithic inspection script into a modular, Click-powered CLI for
running queries, exploring recent jobs, and understanding how workloads spend
slots.

![Tests](https://github.com/safurrier/python-codex-env/workflows/Code%20Quality%20Checks/badge.svg)

## Features

- 🎯 **Project-aware execution** – discover projects from gcloud, remember your
  preferred default, and switch on demand.
- 📊 **Deep job analytics** – inspect execution plans, slot usage, and table
  references from past jobs or freshly submitted ones.
- 🧠 **Insightful summaries** – surface likely bottlenecks and optionally emit an
  LLM-friendly JSON payload.
- 🛠️ **Query runner** – execute SQL files, rewrite dbt `ref()` macros, preview
  results, and export to CSV/JSON/Parquet.
- 💾 **Stateful configuration** – persist default projects and the most recent
  job for quick follow-up analysis.

## Installation

`bq-util` targets Python 3.9+. Install the CLI together with the Google Cloud
extras:

```bash
uv pip install -e .[cli]
# or with pip
git clone https://github.com/safurrier/python-codex-env.git
cd python-codex-env
pip install -e .[cli]
```

The optional `cli` dependency group brings in `google-cloud-bigquery`,
`google-cloud-bigquery-storage`, `pandas`, and other integrations required for
query execution. The base package only depends on `click` and `rich`, so the
CLI can still start up and explain which extras are missing.

## Authenticating with BigQuery

The CLI uses Application Default Credentials. Make sure the active account can
access the relevant projects:

```bash
# Login once if you have not already
gcloud auth application-default login

# Optionally set a default project for gcloud itself
gcloud config set project my-analytics-project
```

You can override the project per command or persist a default inside the CLI.

## Usage

### Configuration

`bq-util` keeps its configuration in the XDG config directory (for most
systems: `~/.config/bq_util/config.json`). Manage it with:

```bash
bq-util config --show
bq-util config --set-project my-analytics-project
bq-util config --reset
```

### Analysing jobs

Analyse an existing job or interactively select one:

```bash
# Choose a project and job through interactive prompts
bq-util analyze

# Inspect a specific job (project:job syntax is supported)
bq-util analyze analytics-project:job_abc123

# Re-run analysis for the most recent job executed through the CLI
bq-util analyze --last

# Emit a JSON payload for tooling integrations
bq-util analyze --last --format json
```

Verbose mode links the query plan to SQL fragments, while `--llm` produces a
compact schema tailor-made for downstream processing.

### Running queries

Execute SQL from a file and review the results inline:

```bash
# Run a SQL file and view a results preview
bq-util query path/to/query.sql --project analytics-project

# Persist the project as default and immediately analyse the job
bq-util query query.sql --set-default-project --analyze

# Export results to Parquet
bq-util query query.sql --output results.parquet
```

If the query contains dbt `ref()` macros the CLI rewrites them to fully
qualified tables using the selected project.

## Documentation

Additional guides live under the `docs/` directory and are published with
MkDocs. The key entry points are:

- [Getting started](docs/getting-started.md) – installation, authentication, and
  first-run walkthroughs.
- [CLI guide](docs/bq-util.md) – detailed command reference with examples.
- [API reference](docs/reference/api.md) – module documentation generated via
  `mkdocstrings`.

Serve the docs locally with:

```bash
make docs-serve
```

## Development

We use [`uv`](https://github.com/astral-sh/uv) to manage virtual environments.
Run the full suite of checks before submitting changes:

```bash
make setup
make check
```

Individual commands are also available:

```bash
make test    # pytest with coverage
make mypy    # strict type checking
make lint    # Ruff linting
make format  # Ruff formatting
```

## Contributing

Issues and pull requests are welcome! Please make sure tests and quality checks
pass, and update documentation when behaviour changes. See
[CONTRIBUTING.md](CONTRIBUTING.md) for more details.

## License

This project is licensed under the MIT License. See [LICENSE](LICENSE).
