# TimescaleDB

```
ghcr.io/expnt/containers/timescaledb:[PG_MAJOR]-plugin-v[PLUGIN_VERSION]
```

Features: PostgreSQL with TimescaleDB extension, optimized for CloudNativePG

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
