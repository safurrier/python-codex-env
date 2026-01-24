# Getting Started with bq-util

This guide covers the essentials for installing `bq-util`, configuring access to
Google BigQuery, and running your first commands.

## Prerequisites

- Python 3.9 or later
- `gcloud` CLI authenticated with Application Default Credentials
- Access to the Google Cloud projects you plan to query

## Installation

Clone the repository and install the CLI with optional BigQuery dependencies:

```bash
git clone https://github.com/safurrier/python-codex-env.git
cd python-codex-env
uv pip install -e .[cli]
# or: pip install -e .[cli]
```

If you prefer not to clone the repository, you can install directly from a Git
URL:

```bash
pip install 'bq-util @ git+https://github.com/safurrier/python-codex-env.git#egg=bq-util&subdirectory=.'
```

## Authenticate with Google Cloud

`bq-util` relies on Application Default Credentials. If you have not already
set them up, run:

```bash
gcloud auth application-default login
```

You can optionally set a gcloud default project:

```bash
gcloud config set project my-analytics-project
```

## Configure the CLI

The first time you run a command the CLI will look for a stored default project
in `~/.config/bq_util/config.json`. Use the `config` command to inspect or
update settings:

```bash
# Show current configuration
bq-util config --show

# Persist a default project
bq-util config --set-project my-analytics-project
```

## Run a Query

Create a SQL file, then execute it with the CLI:

```bash
cat <<'SQL' > example.sql
SELECT 'hello world' AS greeting
SQL

bq-util query example.sql --project my-analytics-project --analyze
```

The query command will execute the SQL, display key statistics, show a preview
of the results, and optionally jump straight into the `analyze` workflow. The
job ID is stored in the configuration file so you can revisit it with
`bq-util analyze --last`.

## Next Steps

- Explore the [BigQuery CLI guide](bq-util.md) for in-depth command
  documentation and advanced flags.
- Read the [container setup](container-setup.md) notes if you run the CLI from a
  Docker or Podman environment.
- Generate API docs with `make docs-build` to explore the Python modules.
