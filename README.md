# Public containers

## Container Images

### TimescaleDB

```
ghcr.io/[REPO_OWNER]/timescaledb:[PG_MAJOR]-plugin-v[PLUGIN_VERSION]
```

Features: PostgreSQL with TimescaleDB extension, optimized for CloudNativePG

### Supabase

```
ghcr.io/[REPO_OWNER]/supabase:[PG_MAJOR]-plugin-v[PLUGIN_VERSION]
```

Features: PostgreSQL (Supabase distribution) with pg_failover_slots extension

## Usage with CloudNativePG

```yaml
apiVersion: postgresql.cnpg.io/v1
kind: Cluster
metadata:
  name: postgres-cluster
spec:
  instances: 3
  imageName: ghcr.io/[REPO_OWNER]/timescaledb:[PG_MAJOR]-plugin-v[PLUGIN_VERSION]
  storage:
    size: 10Gi
```

## Development

### Prerequisites

- [Earthly](https://earthly.dev/get-earthly)
- Docker

### Building Locally

```bash
# Build TimescaleDB image (saves to local Docker)
./dev/build.sh timescaledb -o

# Build Supabase image (saves to local Docker)
./dev/build.sh supabase -o

# Build all containers (saves to local Docker)
./dev/build.sh -o

# Build with multi-platform support (linux/amd64 and linux/arm64)
./dev/build.sh timescaledb -o -m

# Push to registry (automatically uses multi-platform support)
./dev/build.sh -p

# Test specific platform locally (direct Earthly command)
cd containers/timescaledb
earthly --platform=linux/amd64 +build
earthly --platform=linux/arm64 +build

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
earthly --platform=linux/amd64 --platform=linux/arm64 ./containers/timescaledb+build
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
