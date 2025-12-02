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

### MinIO

```
ghcr.io/[REPO_OWNER]/minio:[BASE_VERSION]
```

Mirrored Bitnami MinIO image from `bitnamilegacy` repository. The image is deprecated in the main Bitnami repository and has been mirrored for continued availability.

### Redis

```
ghcr.io/[REPO_OWNER]/redis:[BASE_VERSION]
```

Mirrored Bitnami Redis image from `bitnamilegacy` repository. We use a single Redis image version across all deployments for consistency.

### Python IAC

```
ghcr.io/[REPO_OWNER]/xep-python-iac:[BASE_VERSION]-bookworm
```

Pre-configured Python image for Infrastructure as Code (IAC) CI/CD pipelines. Includes:
- Python 3.12 on Debian Bookworm
- pipx, poetry (pinned version), pre-commit (pinned version)
- OpenTofu (pinned version) - Terraform fork
- tflint (pinned version) - Terraform linter

This image follows the naming convention: `xep-[main image]-[flavor]:[upstream tag]`

All dependencies are pinned to specific versions for stability. This image is optimized for GitLab CI pre-commit jobs to avoid installing dependencies on every pipeline run.

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
