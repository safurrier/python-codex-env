# BigQuery Utility CLI

The `bq-util` command line interface turns the original monolithic script into a
modular, test-backed tool. It integrates with Google BigQuery to inspect job
history, analyse execution plans, and run ad-hoc SQL queries.

## Installation

Install the project in editable mode with the optional `cli` dependency group
to pull in the Google Cloud and pandas dependencies:

```bash
uv pip install -e .[cli]
# or, using pip
pip install -e .[cli]
```

The base package already depends on `click` and `rich`, so importing
`bq_util.cli` works even when the optional dependencies are missing. Commands
that require BigQuery gracefully notify you when the Google Cloud SDK is not
available.

## Configuration and Defaults

Configuration is stored in the XDG config directory (typically
`~/.config/bq_util/config.json`). Manage defaults via the `config` subcommand:

```bash
bq-util config --show
bq-util config --set-project analytics-project
bq-util config --reset
```

The CLI records the last executed job automatically so you can rerun analysis
with `bq-util analyze --last`.

## Analysing Jobs

Analyse any BigQuery job by ID or interactively:

```bash
# Interactive selection: choose a project and then a job
bq-util analyze

# Specify project and job explicitly
bq-util analyze analytics-project:job_1234

# Review the most recent job saved by `bq-util query`
bq-util analyze --last

# Fetch structured JSON data for tooling integrations
bq-util analyze --last --format json

# Optimise prompt engineering workflows
bq-util analyze --last --llm
```

Verbose output links query plan stages to the originating SQL statements to
help you identify bottlenecks quickly.

## Running Queries

Run SQL files directly against BigQuery from the command line:

```bash
bq-util query path/to/query.sql --project analytics-project

# Save results and run analysis automatically
bq-util query query.sql --output results.parquet --analyze

# Persist the project as the default for future commands
bq-util query query.sql --set-default-project
```

The command shows execution statistics, previews the first few rows, and can
store results as CSV, JSON Lines, or Parquet. Queries that contain dbt `ref()`
macros are rewritten to fully qualified table references for quick iteration.

## Optional Interactive Dependencies

Interactive project and job selection is powered by
[InquirerPy](https://github.com/kazhala/InquirerPy). If the package is not
installed, the CLI falls back to sensible defaults and prompts for manual input
instead of failing outright.

## Testing

Comprehensive unit tests exercise configuration management, query execution
invocation, and job analysis flows using Click's `CliRunner`. The BigQuery
client is injected via thin wrappers, keeping the code testable without network
access or Google Cloud credentials.
