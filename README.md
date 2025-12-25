# Public containers

## Container Images

- [TimescaleDB](./containers/timescaledb/README.md) - `ghcr.io/expnt/containers/timescaledb`
- [Supabase](./containers/supabase/README.md) - `ghcr.io/expnt/containers/supabase`
- [MinIO](./containers/minio/README.md) - `ghcr.io/expnt/containers/minio`
- [Redis](./containers/redis/README.md) - `ghcr.io/expnt/containers/redis`
- [Python IAC](./containers/python/README.md) - `ghcr.io/expnt/containers/xep-python-iac`

## Development

### Prerequisites

- [Earthly](https://earthly.dev/get-earthly)
- Docker

### Building Locally

```bash
# Build specific container (saves to local Docker)
./dev/build.sh timescaledb -o
./dev/build.sh supabase -o
./dev/build.sh minio -o
./dev/build.sh redis -o
./dev/build.sh python -o

# Build all containers (saves to local Docker)
./dev/build.sh -o

# Build with multi-platform support (linux/amd64 and linux/arm64)
./dev/build.sh minio -o -m
./dev/build.sh redis -o -m
./dev/build.sh timescaledb -o -m

# For more options
./dev/build.sh --help
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
./dev/build.sh minio -o -m
./dev/build.sh redis -o -m
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

Edit the corresponding `versions.env` file.
