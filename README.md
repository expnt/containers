# Public containers

## Container Images

<!-- VERSIONS_START -->

- [docker](./containers/docker/README.md) - `ghcr.io/expnt/containers/docker`
- [minio](./containers/minio/README.md) - `ghcr.io/expnt/containers/minio`
- [node](./containers/node/README.md) - `ghcr.io/expnt/containers/node`
- [python](./containers/python/README.md) - `ghcr.io/expnt/containers/xep-python-iac`
- [redis](./containers/redis/README.md) - `ghcr.io/expnt/containers/redis`
- [supabase](./containers/supabase/README.md) - `ghcr.io/expnt/containers/supabase`
- [timescaledb](./containers/timescaledb/README.md) - `ghcr.io/expnt/containers/timescaledb`

<!-- VERSIONS_END -->

## Development

### Prerequisites

- [Earthly](https://earthly.dev/get-earthly)
- Docker
- Python 3.12+ and Poetry

### Building Locally

```bash
# Install dependencies
poetry install

# Build specific container (all versions, saves to local Docker)
poetry run containers build docker -o
poetry run containers build timescaledb -o
poetry run containers build supabase -o
poetry run containers build minio -o
poetry run containers build redis -o
poetry run containers build python -o
poetry run containers build node -o

# Build specific version only
poetry run containers build docker -o --version 27
poetry run containers build minio -o --version 2022.2.7

# Build all containers (saves to local Docker)
poetry run containers build --all -o

# Build with multi-platform support (linux/amd64 and linux/arm64)
poetry run containers build docker -o -m
poetry run containers build minio -o -m
poetry run containers build redis -o -m
poetry run containers build timescaledb -o -m

# For more options
poetry run containers build --help
```

### Local Multi-Platform Testing

To test multi-platform builds locally, you need QEMU installed:

**macOS/Windows (Docker Desktop):**

- QEMU is included, no setup needed
- For Apple Silicon: Enable "Use Rosetta for x86/amd64 emulation" in Docker Desktop settings

**Linux:**

```bash
sudo apt-get install qemu-system binfmt-support qemu-user-static
docker run --rm --privileged multiarch/qemu-user-static --reset -p yes
docker stop earthly-buildkitd || true
```

Then you can test:

```bash
# Test both platforms
poetry run containers build minio -o -m
poetry run containers build redis -o -m
```

### Pushing to Registry

**Images are automatically pushed to GitHub Container Registry (GHCR) by CI when you merge to the main branch.**

Local builds only save images to your local Docker daemon for testing. To push images:

1. **Make your changes and commit them**
2. **Push to the repository**
3. **CI will automatically build and push multi-platform images** when changes are merged to `main`

The CI workflow:

- Builds for both `linux/amd64` and `linux/arm64` platforms
- Creates multi-manifest images
- Pushes to `ghcr.io/[REPO_OWNER]/[container]:[tag]`

**Note:** If you need to push manually (e.g., for testing CI), you can trigger the workflow or use Earthly directly with proper authentication.

### Updating Versions

Edit the corresponding `versions.yaml` file in each container directory. The manifest supports multiple versions per container.

### Regenerating READMEs

```bash
poetry run containers generate-readme
```
