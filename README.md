![Code Quality Checks](https://github.com/safurrier/python-collab-template/workflows/Code%20Quality%20Checks/badge.svg) [![codecov](https://codecov.io/gh/safurrier/python-collab-template/branch/master/graph/badge.svg)](https://codecov.io/gh/safurrier/python-collab-template)

# Python Project Template

A modern Python project template with best practices for development and collaboration.

## Features
- 🚀 Fast dependency management with [uv](https://github.com/astral-sh/uv)
- ✨ Code formatting with [ruff](https://github.com/astral-sh/ruff)
- 🔍 Type checking with [mypy](https://github.com/python/mypy)
- 🧪 Testing with [pytest](https://github.com/pytest-dev/pytest)
- 🐳 Docker support for development and deployment
- 👷 CI/CD with GitHub Actions
- 📊 Production-ready BigQuery CLI built with [Click](https://click.palletsprojects.com/)

## Python Version
This template requires Python 3.9 or higher and defaults to Python 3.12. To use a different version:

```bash
# List available Python versions
uv python list

# Use a specific version (e.g., 3.11)
make setup PYTHON_VERSION=3.11  # or UV_PYTHON_VERSION=3.11 make setup

# View installed Python versions
uv python list --installed
```

uv will automatically download and manage Python versions as needed.

## Quickstart
```bash
# Clone this repo and change directory
git clone git@github.com:safurrier/python-collab-template.git my-project-name
cd my-project-name

# Initialize a new project
make init

# Follow the prompts to configure your project
```

This will:
- Configure project metadata (name, description, author)
- Handle example code (keep, simplify, or remove)
- Initialize a fresh git repository
- Set up development environment
- Configure pre-commit hooks (optional, enabled by default)

Pre-commit hooks will automatically run these checks before each commit:
- Type checking (mypy)
- Linting (ruff)
- Formatting (ruff)
- Tests (pytest)

Alternatively, you can set up manually:
```bash
# Install dependencies and set up the environment
make setup

# Run the suite of tests and checks
make check

# Optional: Remove example code to start fresh
make clean-example
```

## BigQuery Utility CLI

The repository now ships with a fully fledged BigQuery helper named `bq-util`.
It wraps the Google Cloud BigQuery APIs with an ergonomic Click interface for
analysing historical jobs, executing SQL files, and managing local defaults.

### Installation

Install the project in editable mode with the `cli` optional dependency group:

```bash
uv pip install -e .[cli]
# or using pip
pip install -e .[cli]
```

This pulls in `google-cloud-bigquery`, `pandas`, `InquirerPy`, and other
required libraries. The base installation already depends on `click` and
`rich`, so the CLI can still be imported without the optional extras (the
commands will raise informative errors if BigQuery dependencies are missing).

### Configuration

`bq-util` persists configuration in the XDG config directory
(`~/.config/bq_util/config.json` by default). Manage it from the command line:

```bash
bq-util config --show          # Display current configuration
bq-util config --set-project my-project-id
bq-util config --reset
```

The CLI automatically tracks the last executed job so you can re-run analysis
with `bq-util analyze --last`.

### Analysing Jobs

The `analyze` command fetches detailed execution statistics, query plans, and
human-friendly summaries:

```bash
# Interactive project and job selection
bq-util analyze

# Analyse a specific job
bq-util analyze my-project:job_abc123

# Export JSON for downstream processing
bq-util analyze --last --format json
```

Verbose mode adds query-plan-to-SQL mapping hints, while `--llm` emits a
machine-friendly summary for further processing.

### Executing Queries

Run SQL files against BigQuery directly from the CLI. The command captures job
statistics, previews the results, and optionally triggers an immediate
analysis:

```bash
bq-util query path/to/query.sql --project my-project --analyze

# Save results to Parquet and remember the project for future runs
bq-util query query.sql --output results.parquet --set-default-project
```

Queries that use dbt `ref()` macros are automatically rewritten to fully
qualified table references for ad-hoc execution.

## Development Commands

### Quality Checks
```bash
make check      # Run all checks (test, mypy, lint, format)
make test       # Run tests with coverage
make mypy       # Run type checking
make lint       # Run linter
make format     # Run code formatter
```

### Example Code
The repository includes a simple example showing:
- Type hints
- Dataclasses
- Unit tests
- Modern Python practices

To remove the example code and start fresh:
```bash
make clean-example
```
## Container Support (Docker/Podman)

### Development Environment

The project automatically detects and uses either Docker or Podman:

```bash
make dev-env    # Uses podman if available, otherwise docker

# Or explicitly choose:
CONTAINER_ENGINE=docker make dev-env
CONTAINER_ENGINE=podman make dev-env

# Check which engine will be used:
make container-info
```

This creates a container with:
- All dependencies installed
- Source code mounted (changes reflect immediately)
- Development tools ready to use
- Automatic UID/GID mapping for file permissions

### Production Image
```bash
make build-image    # Build production image
make push-image     # Push to container registry
```

## Project Structure
```
.
├── src/                # Source code
├── tests/             # Test files
├── docker/            # Container configuration (Docker/Podman)
├── .github/           # GitHub Actions workflows
├── pyproject.toml     # Project configuration
└── Makefile          # Development commands
```

## Contributing
1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Run `make check` to ensure all tests pass
5. Submit a pull request

## License
This project is licensed under the MIT License - see the LICENSE file for details.
