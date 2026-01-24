# Running bq-util in Containers

`bq-util` ships with Docker and Podman configuration that mirrors the local
setup experience. Use the provided `Makefile` targets to spin up a development
shell inside a container if you prefer an isolated environment.

## Quick Start

```bash
# Build images and start the development container
make dev-env
```

The target auto-detects whether Docker or Podman is available, preferring
Podman when both exist.

## Choosing an Engine

| Scenario | Recommendation |
|----------|----------------|
| You already use Docker Desktop | Continue using Docker |
| You need rootless containers or cannot run a daemon | Use Podman |
| You work on Linux and want tighter security | Use Podman |

Both options mount the repository into `/workspace` within the container so the
CLI and tests operate on your working copy.

## Authentication Inside Containers

The container does not include Google Cloud credentials. Authenticate using one
of the following approaches:

1. **Bind mount your ADC file**:
   ```bash
   docker run ... -v "$HOME/.config/gcloud/application_default_credentials.json:/root/.config/gcloud/application_default_credentials.json:ro"
   ```
2. **Use service account keys** by mounting the JSON file and exporting
   `GOOGLE_APPLICATION_CREDENTIALS` before invoking `bq-util`.

## Troubleshooting

### Permission Errors on Mounted Volumes

Docker containers may need your host UID/GID to prevent root-owned files. The
Makefile already applies these options, but if you launch containers manually
set `--user $(id -u):$(id -g)`.

### Podman Compose

Podman users should install `podman-compose` to mirror Docker Compose behaviour:

```bash
pip install podman-compose
```

### Podman Machine on macOS/Windows

If Podman reports that no machine is running, initialise and start one:

```bash
podman machine init
podman machine start
```

## Next Steps

After the container is running, use the standard workflow inside it:

```bash
make setup
make check
bq-util analyze --last
```

The commands behave the same as on the host machine.
