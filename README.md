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
# Build TimescaleDB image
./dev/build.sh timescaledb

# Build Supabase image
./dev/build.sh supabase

# Build and output to Docker
./dev/build.sh -o

# Push to registry
./dev/build.sh -p

# For more options
./dev/build.sh --help
```

### Updating Versions

Edit the corresponding `versions.env` file.
