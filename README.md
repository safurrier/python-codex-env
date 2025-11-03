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

## AdMute Service Overview

The AdMute service monitors HDMI audio from a Roku 4K player and automatically mutes an LG OLED B2 when advertisements start.

### Getting Started

1. Configure audio capture using an HDMI splitter and USB capture interface. Verify the Linux host sees the device (e.g. `/dev/video0` or `hw:1,0`).
2. Copy `configs/local.yaml` to `/etc/admute.yaml` and update the `capture_device` and actuator settings for your environment.
3. Pair with the LG TV:
   - Ensure SimpLink (HDMI-CEC) is enabled: `Settings → General → Devices → HDMI Settings → SimpLink (CEC) → On`.
   - For webOS control, run the service once; accept the pairing prompt on the TV to store the client key.
4. Test HDMI-CEC fallback commands manually: `echo "volumedown" | cec-client -s -d 1`.
5. Run the service: `python -m admute.runner --config /etc/admute.yaml`.

### Manual Web Controls (FastHtml)

Set the `web_app` section in `admute.yaml` to expose a lightweight FastHtml interface for manual mute toggles. By default the
app listens on `http://<host>:8765/` and shows the current mute state, last action, and command counter. The interface provides
"Mute", "Unmute", and "Toggle" buttons that call the same actuator controller used by the detector pipeline, so manual actions
stay in sync with automatic state transitions.

### Systemd Unit Example

```
[Unit]
Description=AdMute service
After=network-online.target

[Service]
ExecStart=/usr/bin/python -m admute.runner --config /etc/admute.yaml
Restart=always
User=admute

[Install]
WantedBy=multi-user.target
```

### Troubleshooting

- If the TV updates to webOS 25 and refuses TLS, set `secure: false` in the actuator configuration to skip certificate validation.
- When the HDMI capture exposes video but no audio, force the input format with `input_format: v4l2` (or `alsa`).
- To retune detector thresholds, record ad segments in `scratch/detector_spikes.ipynb` and adjust the YAML settings.
